import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box
from slutil.CsvUow import CsvUnitOfWork
from slutil.abstract_uow import AbstractUnitOfWork
from slutil.slurm import SlurmService
from slutil.abstract_slurm_service import AbstractSlurmService
from slutil.services import JobDTO, JobRequestDTO, report, get_job, submit
from dataclasses import dataclass

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

def cmd_status(uow: AbstractUnitOfWork, slurm: AbstractSlurmService, slurm_id: int, verbose: bool):
    """Get status of a slurm job.

    SLURM_ID is the id of the job to check.
    """
    job_status = get_job(slurm, uow, slurm_id)
    table = create_jobs_table(f"Job {slurm_id}", verbose, [job_status])

    console = Console()
    console.print(table, overflow="ellipsis")


def cmd_report(uow: AbstractUnitOfWork, slurm: AbstractSlurmService, count: int, verbose: bool):
    """Get status of multiple jobs
    """
    jobs = report(slurm, uow, count)
    if len(jobs) > 0:
        caption = f"Showing last {count} jobs"
    else:
        caption = "(No jobs found)"

    table = create_jobs_table("Slurm job status", verbose, jobs, caption)
    console = Console()
    console.print(table, overflow="ellipsis")

def cmd_submit(uow: AbstractUnitOfWork, slurm: AbstractSlurmService, sbatch_file: str, description: str):
    """Submit a slurm job. 

    SBATCH_FILE is a path to the .sbatch file for the job

    DESCRIPTION is a text field describing the job
    """
    job_slurm_id = submit(slurm, uow, JobRequestDTO(sbatch_file, description))
    click.echo(f"Successfully submitted job {job_slurm_id}")


def command_factory(uow: AbstractUnitOfWork, slurm: AbstractSlurmService) -> click.Group:
    parent_cmd = click.Group()

    parent_cmd.add_command(
        click.Command(
            name="submit", 
            context_settings=None,
            callback=lambda sbatch_file, description: cmd_submit(uow, slurm, sbatch_file, description),
            params=[
                click.Argument(['sbatch_file'], required=True, type=click.Path(exists=True)),
                click.Argument(['description'], required=True, type=str)  
            ]
        )
    )

    parent_cmd.add_command(
        click.Command(
            name="report", 
            context_settings=None,
            callback=lambda count, verbose: cmd_report(uow, slurm, count, verbose),
            params=[
                click.Option(["-c", "--count"], default=10),
                click.Option(["-v", "--verbose"], is_flag=True, default=False)
            ]
        )
    )

    parent_cmd.add_command(
        click.Command(
            name="status", 
            context_settings=None,
            callback=lambda slurm_id, verbose: cmd_status(uow, slurm, slurm_id, verbose),
            params=[
                click.Argument(['slurm_id'], type=int),
                click.Option(["-v", "--verbose"], is_flag=True, default=False)
            ]
        )
        )
    return parent_cmd

@dataclass
class Dependencies():
    uow: AbstractUnitOfWork
    slurm: AbstractSlurmService

def build_dependencies(debug: bool) -> Dependencies:
    if debug:
        uow = CsvUnitOfWork("")
        from slutil.fake_slurm import FakeSlurm
        slurm = FakeSlurm()
    else:
        uow = CsvUnitOfWork("")
        slurm = SlurmService()
    return Dependencies(uow, slurm)

def start_cli():
    dependencies = build_dependencies(debug=True)
    c = command_factory(dependencies.uow, dependencies.slurm)
    try:
        c()
    except Exception as e:
        console = Console()
        console.print(f"[red]Error: {str(e)}[/red]")

if __name__ == '__main__':
    start_cli()