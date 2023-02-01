import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box
from slutil.CsvUow import CsvUnitOfWork
from slutil.services import JobDTO, JobRequestDTO, report, get_job, submit


@click.group()
def cli():
    pass


def jobDTO_to_rich_text(job: JobDTO, verbose: bool) -> tuple[Text, Text, Text, Text, Text, Text]:
    status_color_map = {
        "COMPLETED": "green3",
        "COMPLETING": "chartreuse3",
        "FAILED": "red3",
        "CANCELLED+": "grey54",
        "PENDING": "blue3",
        "PREEMPTED": "red3",
        "RUNNING": "yellow3",
        "SUSPENDED": "orange3",
        "STOPPED": "red3"
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
            Text(job.sbatch)
        )
    else:
        return (
            ellipsis_text(str(job.slurm_id)),
            ellipsis_text(job.status, status_color_map[job.status]),
            ellipsis_text(job.description),
            ellipsis_text(job.submitted_timestamp),
            ellipsis_text(job.git_tag),
            ellipsis_text(job.sbatch)
        )


def create_jobs_table(title: str, verbose: bool, jobs: list[JobDTO], caption=None) -> Table:
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


@cli.command("status")
@click.argument('slurm_id', type=int)
@click.option("-v", "--verbose", is_flag=True, default=False)
def cmd_status(slurm_id: int, verbose: bool):
    """Get status of a slurm job.

    SLURM_ID is the id of the job to check.
    """
    uow = CsvUnitOfWork("")

    try:
        job_status = get_job(slurm_id, uow)
        table = create_jobs_table(f"Job {slurm_id}", verbose, [job_status])

        console = Console()
        console.print(table, overflow="ellipsis")
    except StopIteration:
        console = Console()
        console.print("[red]Error: Job not found in database[/red]")
        exit(1)


@cli.command("report")
@click.option("-c", "--count", default=10)
@click.option("-v", "--verbose", is_flag=True, default=False)
def cmd_report(count: int, verbose: bool):
    """Get status of multiple jobs
    """
    uow = CsvUnitOfWork("")

    jobs = report(uow, count)
    if len(jobs) > 0:
        caption = f"Showing last {count} jobs"
    else:
        caption = "(No jobs found)"

    table = create_jobs_table("Slurm job status", verbose, jobs, caption)
    console = Console()
    console.print(table, overflow="ellipsis")


@cli.command("submit")
@click.argument('sbatch_file', type=click.Path(exists=True))
@click.argument('description', type=str)
def cmd_submit(sbatch_file: str, description: str):
    """Submit a slurm job. 

    SBATCH_FILE is a path to the .sbatch file for the job

    DESCRIPTION is a text field describing the job
    """
    uow = CsvUnitOfWork("")

    job_slurm_id = submit(JobRequestDTO(sbatch_file, description), uow)
    click.echo(f"Successfully submitted job {job_slurm_id}")


def start_cli():
    try:
        cli()
    except Exception as e:
        raise e
        # console = Console()
        # console.print(f"[red]Error: {str(e)}[/red]")

if __name__ == '__main__':
    start_cli()
