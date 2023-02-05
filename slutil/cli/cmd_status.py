from rich.console import Console
from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.cli.formatter import create_jobs_table
from slutil.services.services import get_job


def cmd_status(
    uow: AbstractUnitOfWork, slurm: AbstractSlurmService, slurm_id: int, verbose: bool
):
    """Get status of a slurm job.

    SLURM_ID is the id of the job to check.
    """
    job_status = get_job(slurm, uow, slurm_id)
    table = create_jobs_table(f"Job {slurm_id}", verbose, [job_status])

    console = Console()
    console.print(table, overflow="ellipsis")
