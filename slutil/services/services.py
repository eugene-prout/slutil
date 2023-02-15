from datetime import datetime
from typing import Optional, Iterable
from slutil.model.Record import Record, Dependencies, DependencyType
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
    dependency_ids: list[int]|list[str]

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
        job.status,
        job.description,
        job.dependencies.type.name if job.dependencies else "NONE",
        job.dependencies.state if job.dependencies else "NONE",
        job.dependencies.ids if job.dependencies else ["NONE"],
    )

def get_job(
    slurm_service: AbstractSlurmService, uow: AbstractUnitOfWork, slurm_id: int
) -> JobDTO:
    with uow:
        job = uow.jobs.get(slurm_id)
        get_latest_job_states_nocommit([job], slurm_service)
        dependency_state = "NONE"
        dependency_state_mapping = {
            DependencyType.after: {
                "completed": ["COMPLETED", "COMPLETING", "FAILED", "CANCELLED+", "PREEMPTED", "RUNNING", "SUSPENDED", "STOPPED"],
                "failed": [],
                "runnning": [],
                "pending": ["PENDING"]
            },
            DependencyType.afterok: {
                "completed": ["COMPLETED"],
                "failed": ["FAILED", "CANCELLED+", "PREEMPTED", "SUSPENDED", "STOPPED"],
                "running": ["RUNNING", "COMPLETING"],
                "pending": ["PENDING"]
            },
            DependencyType.afterany: {
                "completed": ["COMPLETED", "COMPLETING", "FAILED", "CANCELLED+", "PREEMPTED", "SUSPENDED", "STOPPED"],
                "failed": [],
                "running": ["RUNNING"],
                "pending": ["PENDING"]
            },
            DependencyType.afternotok: {
                "completed": ["FAILED", "CANCELLED+", "PREEMPTED", "SUSPENDED", "STOPPED"],
                "failed": ["COMPLETED"],
                "running": ["RUNNING", "COMPLETING"],
                "pending": ["PENDING"]
            }
        }
        if job.dependencies:
            if job.dependencies.type == DependencyType.singleton:
                if job.status != "RUNNING":
                    dependency_state = "RUNNING"
                else:
                    dependency_state = "COMPLETED"
            else:
                try:
                    dependencies_job = [get_job(slurm_service, uow, j) for j in job.dependencies.ids]
                    dependencies_state = [j.status for j in dependencies_job]
                    state_map = dependency_state_mapping[job.dependencies.type]
                    if any(s in state_map["failed"] for s in dependencies_state):
                        dependency_state = "FAILED"
                    elif all(s in state_map["completed"] for s in dependencies_state):
                        dependency_state = "COMPLETED"
                    elif any(s in state_map["running"] for s in dependencies_state):
                        dependency_state = "RUNNING"
                    elif all(s in state_map["pending"] for s in dependencies_state):
                        dependency_state = "PENDING"
                except KeyError:
                    dependency_state = "UNKNOWN"
            job.dependencies.state = dependency_state

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
        numbers = [j.slurm_id for j in sorted([j for j in all_jobs if not j.deleted])[:count]]
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
            dependencies = Dependencies(DependencyType[req.dependency_type], "PENDING", req.dependency_list)
        else:
            dependencies = None
        new_job = Record(
            slurm_id, timestamp, repo_stamp, req.sbatch, "PENDING", req.description, dependencies
        )
        uow.jobs.add(new_job)
        uow.commit()

        return str(slurm_id)


def update_description(uow: AbstractUnitOfWork, slurm_id: int, new_description: str):
    with uow:
        j = uow.jobs.get(slurm_id)
        j.description = new_description
        uow.commit()


def get_latest_job_states_nocommit(
    jobs: Iterable[Record], slurm_service: AbstractSlurmService
):
    end_states = ["COMPLETED", "FAILED", "PREEMPTED"]
    for job in jobs:
        if job.status not in end_states:
            job.status = slurm_service.get_job_status(job.slurm_id)
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
        matching_jobs = set(get_latest_job_states_nocommit(uow.jobs.list(), slurm))

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
                j for j in matching_jobs if re.search(query.status_filter, j.status)
            }

    return [map_job_to_jobDTO(j) for j in matching_jobs]
