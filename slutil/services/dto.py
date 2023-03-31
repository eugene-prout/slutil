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
class JobResponse:
    fresh: bool
    updated_time: str
    job: JobDTO

@dataclass
class JobListResponse:
    fresh: bool
    minimum_updated_time: str
    jobs: list[JobDTO]

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


def map_job_to_jobResponse(job: Record) -> JobResponse:
    return JobResponse(
        fresh=job.fresh_read,
        updated_time=datetime.strftime(job.last_updated, "%y-%m-%d %H:%M:%S"),
        job=map_job_to_jobDTO(job)
    )

def map_jobs_to_job_list(jobs: list[Record]) -> JobListResponse:
    return JobListResponse(
        fresh=all(j.fresh_read for j in jobs), 
        minimum_updated_time=datetime.strftime(min([j.last_updated for j in jobs], default=datetime.now()), "%y-%m-%d %H:%M:%S"),
        jobs=[map_job_to_jobDTO(j) for j in jobs])



@dataclass
class FilterQuery:
    id_filter: Optional[re.Pattern] = None
    status_filter: Optional[re.Pattern] = None
    description_filter: Optional[re.Pattern] = None
    timestamp_filter: Optional[re.Pattern] = None
    commit_filter: Optional[re.Pattern] = None
    sbatch_filter: Optional[re.Pattern] = None