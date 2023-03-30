from datetime import datetime
from typing import Optional, Iterable, Union
from slutil.model.Record import DependencyState, Record, Dependencies, DependencyType, JobStatus, aggregate_depedencies
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.adapters.abstract_vcs import AbstractVCS
from slutil.services.abstract_uow import AbstractUnitOfWork
from dataclasses import dataclass
import re
from functools import total_ordering

@dataclass(frozen=True)
@total_ordering
class JobDTO:
    slurm_id: int
    submitted_timestamp: str
    git_tag: str
    sbatch: str
    status: str
    description: str
    dependency_type: str
    dependency_state: str
    dependency_ids: Union[list[int],list[str]]

    def __gt__(self, other):
        return self.slurm_id > other.slurm_id


@dataclass
class JobRequestDTO:
    sbatch: str
    description: str
    dependency_type: Optional[str]
    dependency_list: list[int]


def map_job_to_jobDTO(job: Record) -> JobDTO:
    return JobDTO(
        job.slurm_id,
        datetime.strftime(job.submitted_timestamp, "%y-%m-%d %H:%M:%S"),
        job.git_tag,
        job.sbatch,
        job.status.name,
        job.description,
        job.dependencies.type.name if job.dependencies else "NONE",
        job.dependencies.state.name if job.dependencies else "NONE",
        [str(j) for j in job.dependencies.ids] if job.dependencies else ["NONE"],
    )

def update_dependencies(slurm_service: AbstractSlurmService, uow: AbstractUnitOfWork, job: Record):
    if job.dependencies is not None:
        try:
            dependent_jobs = update_job_states_nc([uow.jobs.get(j) for j in job.dependencies.ids], slurm_service, uow)
            job.dependencies.state = aggregate_depedencies(job, dependent_jobs)
        except KeyError:
            job.dependencies.state = DependencyState.UNKNOWN

def get_job(
    slurm_service: AbstractSlurmService, uow: AbstractUnitOfWork, slurm_id: int
) -> JobDTO:
    with uow:
        job = uow.jobs.get(slurm_id)
        update_job_states_nc([job], slurm_service, uow)

        uow.commit()
        return map_job_to_jobDTO(job)


def delete_job(uow: AbstractUnitOfWork, slurm_id: int):
    with uow:
        job = uow.jobs.get(slurm_id)
        job.deleted = True
        uow.commit()


def undelete_job(uow: AbstractUnitOfWork, slurm_id: int):
    with uow:
        job = uow.jobs.get_deleted(slurm_id)
        job.deleted = False
        uow.commit()


def report(
    slurm_service: AbstractSlurmService, uow: AbstractUnitOfWork, count: int
) -> list[JobDTO]:
    with uow:
        all_jobs = uow.jobs.list()
        numbers = [j.slurm_id for j in sorted([j for j in all_jobs if not j.deleted], reverse=True)[:count]]
        output = [get_job(slurm_service, uow, i) for i in numbers]
        uow.commit()
        return output


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
            slurm_id, timestamp, repo_stamp, req.sbatch, JobStatus.PENDING, req.description, dependencies
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
    jobs: Iterable[Record], slurm_service: AbstractSlurmService, uow: AbstractUnitOfWork
):
    for j in filter(lambda j: j.in_progress, jobs):
        time_difference = (datetime.now() - j.submitted_timestamp).total_seconds() 
        allow_none = j.status == JobStatus.PENDING and time_difference < 60*30
        new_status = slurm_service.get_job_status(j.slurm_id, allow_none)
        if new_status:  
            j.status = JobStatus[new_status]
        update_dependencies(slurm_service, uow, j)

    return jobs


@dataclass
class FilterQuery:
    id_filter: Optional[re.Pattern] = None
    status_filter: Optional[re.Pattern] = None
    description_filter: Optional[re.Pattern] = None
    timestamp_filter: Optional[re.Pattern] = None
    commit_filter: Optional[re.Pattern] = None
    sbatch_filter: Optional[re.Pattern] = None


def filter_jobs(
    uow: AbstractUnitOfWork, slurm: AbstractSlurmService, query: FilterQuery
) -> list[JobDTO]:
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

    return [map_job_to_jobDTO(j) for j in matching_jobs]
