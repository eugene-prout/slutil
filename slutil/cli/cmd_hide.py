from rich.console import Console
from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.cli.formatter import create_jobs_table
from slutil.services.services import get_job, hide_job
import click
import logging

def cmd_hide(
    uow: AbstractUnitOfWork, slurm: AbstractSlurmService, slurm_id: int, verbose: bool
):
    """Hide a slurm job

    SLURM_ID is the id of the job to hide.

    Note: can be reversed with "slutil unhide <slurm id>"
    """
    logging.debug("cli: hide job %d requested", slurm_id)

    job_details = get_job(slurm, uow, slurm_id)
    
    table = create_jobs_table(f"Job {slurm_id}", verbose, [job_details.job])
    console = Console()
    console.print(table, overflow="ellipsis")

    click.confirm("Do you want to hide the above job? ", abort=True)
    logging.debug("cli: hide job %d confirmed", slurm_id)

    hide_job(uow, slurm_id)
    click.echo(f"Job {slurm_id} hidden")
