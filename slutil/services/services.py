from datetime import datetime
from typing import Iterable
from slutil.model.Record import DependencyState, Record, Dependencies, DependencyType, JobStatus, aggregate_depedencies
from slutil.adapters.abstract_slurm_service import AbstractSlurmService, SlurmNotAccessibleError
from slutil.adapters.abstract_vcs import AbstractVCS
from slutil.services.abstract_uow import AbstractUnitOfWork
import re
from slutil.services.dto import JobResponse, JobListResponse, JobRequestDTO, FilterQuery, map_job_to_jobResponse, map_jobs_to_job_list


def update_dependencies(slurm_service: AbstractSlurmService, uow: AbstractUnitOfWork, job: Record):
    if job.dependencies is not None:
        try:
            dependent_jobs = update_job_states_nc([uow.jobs.get(j) for j in job.dependencies.ids], slurm_service, uow)
            job.dependencies.state = aggregate_depedencies(job, dependent_jobs)
        except KeyError:
            job.dependencies.state = DependencyState.UNKNOWN

def get_job(
    slurm_service: AbstractSlurmService, uow: AbstractUnitOfWork, slurm_id: int
) -> JobResponse:
    with uow:
        job = uow.jobs.get(slurm_id)
        update_job_states_nc([job], slurm_service, uow)

        uow.commit()
        return map_job_to_jobResponse(job)
    
def hide_job(uow: AbstractUnitOfWork, slurm_id: int):
    with uow:
        job = uow.jobs.get(slurm_id)
        job.deleted = True
        uow.commit()


def unhide_job(uow: AbstractUnitOfWork, slurm_id: int):
    with uow:
        job = uow.jobs.get_deleted(slurm_id)
        job.deleted = False
        uow.commit()


def recent(
    slurm_service: AbstractSlurmService, uow: AbstractUnitOfWork, count: int
) -> JobListResponse:
    with uow:
        all_jobs = uow.jobs.list()
        jobs = [j for j in sorted([j for j in all_jobs if not j.deleted], reverse=True)[:count]]
        output = update_job_states_nc(jobs, slurm_service, uow)
        uow.commit()

        return map_jobs_to_job_list(output)

def report(
    slurm_service: AbstractSlurmService, uow: AbstractUnitOfWork
) -> JobListResponse:
    with uow:
        if not slurm_service.test_slurm_accessible():
            raise SlurmNotAccessibleError("cannot access Slurm. Slurm access is required for this command. Please ensure Slurm is accessible before running this command.")
        all_jobs = uow.jobs.list()
        jobs = all_jobs
        output = update_job_states_nc_return_changed(jobs, slurm_service, uow)
        uow.commit()

        return map_jobs_to_job_list(output)

def submit(
    slurm_service: AbstractSlurmService,
    uow: AbstractUnitOfWork,
    vcs: AbstractVCS,
    req: JobRequestDTO,
) -> str:
    with uow:
        repo_stamp = vcs.get_current_commit()
        timestamp = datetime.now()
        slurm_id = slurm_service.submit_job(req.sbatch, req.dependency_type, req.dependency_list)
        if req.dependency_type:
            dependencies = Dependencies(DependencyType[req.dependency_type], DependencyState.PENDING, req.dependency_list)
        else:
            dependencies = None
        new_job = Record(
            slurm_id, timestamp, repo_stamp, req.sbatch, JobStatus.PENDING, req.description, datetime.now(), dependencies
        )
        uow.jobs.add(new_job)
        uow.commit()

        return str(slurm_id)


def update_description(uow: AbstractUnitOfWork, slurm_id: int, new_description: str):
    with uow:
        j = uow.jobs.get(slurm_id)
        j.description = new_description
        uow.commit()


def update_job_states_nc(
    jobs: list[Record], slurm_service: AbstractSlurmService, uow: AbstractUnitOfWork
) -> list[Record]:
    for j in jobs:
        try:
            if j.in_progress:
                time_difference = (datetime.now() - j.submitted_timestamp).total_seconds() 
                allow_none = j.status == JobStatus.PENDING and time_difference < 60*30
                new_status = slurm_service.get_job_status(j.slurm_id, allow_none)
                if new_status:  
                    j.status = JobStatus[new_status]
            j.last_updated = datetime.now()
            j.fresh_read = True
        except SlurmNotAccessibleError:
            pass

        update_dependencies(slurm_service, uow, j)

    return jobs

def update_job_states_nc_return_changed(
    jobs: list[Record], slurm_service: AbstractSlurmService, uow: AbstractUnitOfWork
) -> list[Record]:
    changed_state = []
    for j in jobs:
        try:
            if j.in_progress:
                time_difference = (datetime.now() - j.submitted_timestamp).total_seconds() 
                allow_none = j.status == JobStatus.PENDING and time_difference < 60*30

                new_status = slurm_service.get_job_status(j.slurm_id, allow_none)
                if new_status:
                    if j.status != JobStatus[new_status]:
                        changed_state.append(j)
                    j.status = JobStatus[new_status]
            j.last_updated = datetime.now()
            j.fresh_read = True
        except SlurmNotAccessibleError:
            pass

        update_dependencies(slurm_service, uow, j)

    return changed_state



def filter_jobs(
    uow: AbstractUnitOfWork, slurm: AbstractSlurmService, query: FilterQuery
) -> JobListResponse:
    with uow:
        matching_jobs = set(update_job_states_nc(uow.jobs.list(), slurm, uow))

        if query.id_filter:
            matching_jobs = {
                j for j in matching_jobs if re.search(query.id_filter, str(j.slurm_id))
            }

        if query.description_filter:
            matching_jobs = {
                j
                for j in matching_jobs
                if re.search(query.description_filter, str(j.description))
            }

        if query.commit_filter:
            matching_jobs = {
                j for j in matching_jobs if re.search(query.commit_filter, j.git_tag)
            }

        if query.sbatch_filter:
            matching_jobs = {
                j for j in matching_jobs if re.search(query.sbatch_filter, j.sbatch)
            }

        if query.timestamp_filter:
            matching_jobs = {
                j
                for j in matching_jobs
                if re.search(
                    query.timestamp_filter,
                    datetime.strftime(j.submitted_timestamp, "%Y-%m-%d %H:%M:%S"),
                )
            }

        if query.status_filter:
            matching_jobs = {
                j for j in matching_jobs if re.search(query.status_filter, j.status.name)
            }

    return map_jobs_to_job_list(list(matching_jobs))


def create_repository_file(uow: AbstractUnitOfWork):
    uow.jobs.create_file()
