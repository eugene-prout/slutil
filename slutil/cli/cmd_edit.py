from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.services.services import get_job, update_description
import click
import logging

def cmd_edit(uow: AbstractUnitOfWork, slurm: AbstractSlurmService, slurm_id: int):
    """Edit description of a job

    SLURM_ID is the id of the job to update
    """
    logging.debug("cli: edit job %d requested", slurm_id)

    j = get_job(slurm, uow, slurm_id)
    new_description = click.edit(j.description)
    if new_description is None:
        logging.debug("cli: no changes")
        click.echo("No changes made")
    else:
        logging.debug("cli: changes made, calling service")
        update_description(uow, j.slurm_id, new_description)
        click.echo("Job description updated")
