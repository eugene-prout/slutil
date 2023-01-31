from dataclasses import dataclass
from functools import total_ordering
from datetime import datetime
from rich.text import Text

@dataclass
@total_ordering
class Record():
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

    def to_row(self) -> list:
        # slurm_id, submitted timestamp, git tag, sbatch, status, description
        return [self.slurm_id, self.submitted_timestamp.strftime('%Y-%m-%d %H:%M:%S'), self.git_tag, self.sbatch, self.status, self.description]

    def to_rich_text(self, verbose: bool) -> list:
        status_color_map = {
            "COMPLETED": "green3",
            "COMPLETING": "chartreuse3",
            "FAILED": "red3",
            "PENDING": "blue3",
            "PREEMPTED": "red3",
            "RUNNING": "yellow3",
            "SUSPENDED": "orange3",
            "STOPPED": "red3"
        }
        goal_color = status_color_map[self.status]
        if verbose:
            description = self.description
        else:
            description = Text(self.description, overflow="ellipsis", no_wrap=True)
        return [str(self.slurm_id), f"[{goal_color}]{self.status}[/{goal_color}]", description, self.submitted_timestamp.strftime('%y-%m-%d %H:%M'), self.git_tag, self.sbatch]

