from rich.console import Console
from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.cli.formatter import create_jobs_table
from slutil.services.services import get_job, delete_job
import click


def cmd_delete(
    uow: AbstractUnitOfWork, slurm: AbstractSlurmService, slurm_id: int, verbose: bool
):
    """Delete a slurm job

    SLURM_ID is the id of the job to delete.

    Note: can be reversed with "slutil restore <slurm id>"
    """
    job_details = get_job(slurm, uow, slurm_id)
    table = create_jobs_table(f"Job {slurm_id}", verbose, [job_details])
    console = Console()
    console.print(table, overflow="ellipsis")
    click.confirm("Do you want to delete the above job? ", abort=True)
    delete_job(uow, slurm_id)
    click.echo(f"Job {slurm_id} deleted")
