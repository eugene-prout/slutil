from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.services.services import load_record_from_slurm
import click
import logging

def cmd_load(uow: AbstractUnitOfWork, slurm: AbstractSlurmService, slurm_id: int, overwrite: bool):
    """Load a record from Slurm

    SLURM_ID is the id of the job to show.
    """
    logging.debug("cli: loading job id: %d", slurm_id)

    load_record_from_slurm(uow, slurm, slurm_id, overwrite)
    
    click.echo(f"Job {slurm_id} loaded")
