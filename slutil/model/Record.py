from dataclasses import dataclass
from functools import total_ordering
from datetime import datetime
from typing import Iterable, Optional
from enum import Enum


class DependencyType(Enum):
    after = 1
    afterany = 2
    afternotok = 3
    afterok = 4
    singleton = 5


class DependencyState(Enum):
    PENDING = 1
    RUNNING = 2
    COMPLETED = 3
    NONE = 4
    UNKNOWN = 5
    FAILED = 6


@dataclass
class Dependencies:
    type: DependencyType
    state: DependencyState
    ids: list[int]


class JobStatus(Enum):
    PENDING = 1
    RUNNING = 2
    SUSPENDED = 3
    COMPLETED = 4
    CANCELLED = 5
    FAILED = 6
    TIMEOUT = 7
    NODE_FAIL = 8
    PREEMPTED = 9
    BOOT_FAIL = 10
    DEADLINE = 11
    OUT_OF_MEMORY = 12
    COMPLETING = 13
    STOPPED = 14

@dataclass
@total_ordering
class Record:
    slurm_id: int
    submitted_timestamp: datetime
    git_tag: str
    sbatch: str
    status: JobStatus
    description: str
    last_updated: datetime

    dependencies: Optional[Dependencies] = None
    fresh_read: bool = False
    deleted: bool = False

    def __hash__(self):
        return hash((self.slurm_id, self.submitted_timestamp))

    def __eq__(self, other):
        if not isinstance(other, Record):
            return False
        return (self.slurm_id == other.slurm_id) and (
            self.submitted_timestamp == other.submitted_timestamp
        )

    @property
    def is_finished(self) -> bool:
        return self.status in [
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.PREEMPTED,
        ]
    
    @property
    def in_progress(self) -> bool:
        return self.status not in [
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.PREEMPTED,
        ]

    def __gt__(self, other):
        return self.slurm_id > other.slurm_id


def aggregate_depedencies(job: Record, dependent_jobs: Iterable[Record]) -> DependencyState:
    if job.dependencies is None:
        return DependencyState.NONE
    
    if job.dependencies.type == DependencyType.singleton:
        if job.status != JobStatus.RUNNING:
            return DependencyState.RUNNING
        else:
            return DependencyState.PENDING

    dependency_state_mapping = {
        DependencyType.after: {
            "completed": [s for s in JobStatus if s != JobStatus.PENDING],
            "failed": [],
            "runnning": [],
            "pending": [JobStatus.PENDING]
        },
        DependencyType.afterok: {
            "completed": [JobStatus.COMPLETED],
            "failed": [JobStatus.FAILED, JobStatus.CANCELLED, JobStatus.PREEMPTED, JobStatus.SUSPENDED, JobStatus.STOPPED],
            "running": [JobStatus.RUNNING, JobStatus.COMPLETING],
            "pending": [JobStatus.PENDING]
        },
        DependencyType.afterany: {
            "completed": [s for s in JobStatus if s not in [JobStatus.PENDING, JobStatus.RUNNING]],
            "failed": [],
            "running": [JobStatus.RUNNING],
            "pending": [JobStatus.PENDING]
        },
        DependencyType.afternotok: {
            "completed": [JobStatus.FAILED, JobStatus.CANCELLED, JobStatus.PREEMPTED, JobStatus.SUSPENDED, JobStatus.STOPPED],
            "failed": [JobStatus.COMPLETED],
            "running": [JobStatus.RUNNING, JobStatus.COMPLETING],
            "pending": [JobStatus.PENDING]
        }
    }
    state_map = dependency_state_mapping[job.dependencies.type]
    if any(s.status in state_map["failed"] for s in dependent_jobs):
        return DependencyState.FAILED
    elif all(s.status in state_map["completed"] for s in dependent_jobs):
        return DependencyState.COMPLETED
    elif any(s.status in state_map["running"] for s in dependent_jobs):
        return DependencyState.RUNNING
    elif all(s.status in state_map["pending"] for s in dependent_jobs):
        return DependencyState.PENDING
    else:
        return DependencyState.UNKNOWN