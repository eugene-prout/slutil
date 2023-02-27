import click
from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.abstract_vcs import AbstractVCS
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.services.services import JobRequestDTO, submit
from typing import Optional
import logging

def cmd_submit(
    uow: AbstractUnitOfWork,
    slurm: AbstractSlurmService,
    vcs: AbstractVCS,
    sbatch_file: str,
    description: str,
    dependency: tuple[Optional[str], list[int]],
):
    """Submit a slurm job.

    SBATCH_FILE is a path to the .sbatch file for the job

    DESCRIPTION is a text field describing the job
    """
    logging.debug("cli: submit requested, sbatch: %s, description: %s, dependency: %s", sbatch_file, description, dependency)

    job_slurm_id = submit(
        slurm,
        uow,
        vcs,
        JobRequestDTO(sbatch_file, description, dependency[0], dependency[1]),
    )
    click.echo(f"Successfully submitted job {job_slurm_id}")
