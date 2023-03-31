from rich.console import Console
from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.cli.formatter import create_job_table_detailed
from slutil.services.services import get_job
import logging

def cmd_status(
    uow: AbstractUnitOfWork, slurm: AbstractSlurmService, slurm_id: int, verbose: bool
):
    """Get status of a slurm job.

    SLURM_ID is the id of the job to check.
    """
    logging.debug("cli: status requested job id: %d", slurm_id)
    job_response = get_job(slurm, uow, slurm_id)

    title = f"Job {slurm_id}"
    if not job_response.fresh:
        title += f"\n[red](Slurm cannot be reached, showing cached data from {job_response.updated_time})[/red]"

    table = create_job_table_detailed(title, verbose, [job_response.job])

    console = Console()
    console.print(table, overflow="ellipsis")
