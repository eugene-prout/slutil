from dataclasses import dataclass
from functools import total_ordering
from datetime import datetime
from typing import Optional
from enum import Enum


class DependencyType(Enum):
    after = 1
    afterany = 2
    afternotok = 3
    afterok = 4
    singleton = 5


@dataclass
class Dependencies:
    type: DependencyType
    state: str
    ids: list[int]

@dataclass
@total_ordering
class Record:
    slurm_id: int
    submitted_timestamp: datetime
    git_tag: str
    sbatch: str
    status: str
    description: str
    dependencies: Optional[Dependencies] = None
    deleted: bool = False

    def __hash__(self):
        return hash((self.slurm_id, self.submitted_timestamp))

    def __eq__(self, other):
        if not isinstance(other, Record):
            return False
        return (self.slurm_id == other.slurm_id) and (
            self.submitted_timestamp == other.submitted_timestamp
        )

    def __gt__(self, other):
        return self.slurm_id > other.slurm_id
