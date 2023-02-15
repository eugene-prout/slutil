from rich.table import Table
from rich.text import Text
from rich import box
from slutil.services.services import JobDTO
from typing import Optional, Iterable


def jobDTO_to_rich_text(
    job: JobDTO, verbose: bool
) -> tuple[Text, Text, Text, Text, Text, Text, Text]:
    status_color_map = {
        "COMPLETED": "green3",
        "COMPLETING": "chartreuse3",
        "FAILED": "red3",
        "CANCELLED+": "grey54",
        "PENDING": "blue3",
        "PREEMPTED": "red3",
        "RUNNING": "yellow3",
        "SUSPENDED": "orange3",
        "STOPPED": "red3",
        "UNKNOWN": "grey54",
        "NONE": "grey54"
    }

    def ellipsis_text(text: str, style: str = ""):
        return Text(text, overflow="ellipsis", no_wrap=True, style=style)

    if verbose:
        return (
            Text(str(job.slurm_id)),
            Text(job.status, status_color_map[job.status]),
            Text(job.description),
            Text(job.submitted_timestamp),
            Text(job.git_tag),
            Text(job.dependency_state, status_color_map[job.dependency_state]),
            Text(job.sbatch),
        )
    else:
        return (
            ellipsis_text(str(job.slurm_id)),
            ellipsis_text(job.status, status_color_map[job.status]),
            ellipsis_text(job.description),
            ellipsis_text(job.submitted_timestamp),
            ellipsis_text(job.git_tag),
            ellipsis_text(job.dependency_state, status_color_map[job.dependency_state]),
            ellipsis_text(job.sbatch),
        )


def jobDTO_to_rich_text_detailed(
    job: JobDTO, verbose: bool
) -> tuple[Text, Text, Text, Text, Text, Text, Text, Text, Text]:
    status_color_map = {
        "COMPLETED": "green3",
        "COMPLETING": "chartreuse3",
        "FAILED": "red3",
        "CANCELLED+": "grey54",
        "PENDING": "blue3",
        "PREEMPTED": "red3",
        "RUNNING": "yellow3",
        "SUSPENDED": "orange3",
        "STOPPED": "red3",
        "UNKNOWN": "grey54",
        "NONE": "grey54"
    }

    def ellipsis_text(text: str, style: str = ""):
        return Text(text, overflow="ellipsis", no_wrap=True, style=style)

    if verbose:
        return (
            Text(str(job.slurm_id)),
            Text(job.status, status_color_map[job.status]),
            Text(job.description),
            Text(job.submitted_timestamp),
            Text(job.git_tag),
            Text(job.sbatch),
            Text(job.dependency_state, status_color_map[job.dependency_state]),
            Text(job.dependency_type),
            Text(", ".join(map(str, job.dependency_ids)))
        )
    else:
        return (
            ellipsis_text(str(job.slurm_id)),
            ellipsis_text(job.status, status_color_map[job.status]),
            ellipsis_text(job.description),
            ellipsis_text(job.submitted_timestamp),
            ellipsis_text(job.git_tag),
            ellipsis_text(job.sbatch),
            ellipsis_text(job.dependency_state, status_color_map[job.dependency_state]),
            ellipsis_text(job.dependency_type),
            ellipsis_text(", ".join(map(str, job.dependency_ids)))
        )

def create_jobs_table(
    title: str, verbose: bool, jobs: Iterable[JobDTO], caption: Optional[str] = None
) -> Table:
    table = Table(title=title, caption=caption, box=box.ROUNDED, expand=True)
    table.add_column("ID")
    table.add_column("Status")
    table.add_column("Description")
    table.add_column("Submit Time")
    table.add_column("Commit")
    table.add_column("Dependency State")
    table.add_column("sbatch File")

    for j in sorted(jobs, reverse=True):
        table.add_row(*jobDTO_to_rich_text(j, verbose))

    return table

def create_job_table_detailed(
    title: str, verbose: bool, jobs: Iterable[JobDTO], caption: Optional[str] = None
) -> Table:
    table = Table(title=title, caption=caption, box=box.ROUNDED, expand=True)
    table.add_column("ID")
    table.add_column("Status")
    table.add_column("Description")
    table.add_column("Submit Time")
    table.add_column("Commit")
    table.add_column("sbatch File")
    table.add_column("Dependency State")
    table.add_column("Dependency Type")
    table.add_column("Dependency IDs")

    for j in sorted(jobs, reverse=True):
        table.add_row(*jobDTO_to_rich_text_detailed(j, verbose))

    return table
