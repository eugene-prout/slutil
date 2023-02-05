from dataclasses import dataclass
from functools import total_ordering
from datetime import datetime


@dataclass
@total_ordering
class Record:
    slurm_id: int
    submitted_timestamp: datetime
    git_tag: str
    sbatch: str
    status: str
    description: str

    def __eq__(self, other):
        return self.slurm_id == other.slurm_id

    def __gt__(self, other):
        return self.slurm_id > other.slurm_id
