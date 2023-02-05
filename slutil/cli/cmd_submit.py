import click
from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.services.services import JobRequestDTO, submit


def cmd_submit(
    uow: AbstractUnitOfWork,
    slurm: AbstractSlurmService,
    sbatch_file: str,
    description: str,
):
    """Submit a slurm job.

    SBATCH_FILE is a path to the .sbatch file for the job

    DESCRIPTION is a text field describing the job
    """
    job_slurm_id = submit(slurm, uow, JobRequestDTO(sbatch_file, description))
    click.echo(f"Successfully submitted job {job_slurm_id}")
