from rich.table import Table
from rich.text import Text
from rich import box
from slutil.services.services import JobDTO


def jobDTO_to_rich_text(
    job: JobDTO, verbose: bool
) -> tuple[Text, Text, Text, Text, Text, Text]:
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
    }

    def ellipsis_text(text: str, style=""):
        return Text(text, overflow="ellipsis", no_wrap=True, style=style)

    if verbose:
        return (
            Text(str(job.slurm_id)),
            Text(job.status, status_color_map[job.status]),
            Text(job.description),
            Text(job.submitted_timestamp),
            Text(job.git_tag),
            Text(job.sbatch),
        )
    else:
        return (
            ellipsis_text(str(job.slurm_id)),
            ellipsis_text(job.status, status_color_map[job.status]),
            ellipsis_text(job.description),
            ellipsis_text(job.submitted_timestamp),
            ellipsis_text(job.git_tag),
            ellipsis_text(job.sbatch),
        )


def create_jobs_table(
    title: str, verbose: bool, jobs: list[JobDTO], caption=None
) -> Table:
    table = Table(title=title, caption=caption, box=box.ROUNDED, expand=True)
    table.add_column("ID")
    table.add_column("Status")
    table.add_column("Description")
    table.add_column("Submit Time")
    table.add_column("Commit")
    table.add_column("sbatch File")

    for j in jobs:
        table.add_row(*jobDTO_to_rich_text(j, verbose))

    return table
