from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.services.services import unhide_job
import click
import logging

def cmd_unhide(uow: AbstractUnitOfWork, slurm: AbstractSlurmService, slurm_id: int):
    """Unhide a slurm job.

    SLURM_ID is the id of the job to show.
    """
    logging.debug("cli: undeleted requested job id: %d", slurm_id)

    unhide_job(uow, slurm_id)
    click.echo(f"Job {slurm_id} restored")
