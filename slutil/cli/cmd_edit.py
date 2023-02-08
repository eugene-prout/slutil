from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.services.services import get_job, update_description
import click


def cmd_edit(uow: AbstractUnitOfWork, slurm: AbstractSlurmService, slurm_id: int):
    """Edit description of a job

    SLURM_ID is the id of the job to update
    """
    j = get_job(slurm, uow, slurm_id)
    new_description = click.edit(j.description)
    if new_description is None:
        click.echo("No changes made")
    else:
        update_description(uow, j.slurm_id, new_description)
        click.echo("Job description updated")
