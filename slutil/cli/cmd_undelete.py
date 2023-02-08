from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.services.services import undelete_job
import click


def cmd_undelete(uow: AbstractUnitOfWork, slurm: AbstractSlurmService, slurm_id: int):
    """Get status of a slurm job.

    SLURM_ID is the id of the job to check.
    """
    undelete_job(uow, slurm_id)
    click.echo(f"Job {slurm_id} restored")
