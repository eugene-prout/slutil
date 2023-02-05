from rich.console import Console
from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.services.services import report
from slutil.cli.formatter import create_jobs_table


def cmd_report(
    uow: AbstractUnitOfWork, slurm: AbstractSlurmService, count: int, verbose: bool
):
    """Get status of multiple jobs"""
    jobs = report(slurm, uow, count)
    if len(jobs) > 0:
        caption = f"Showing last {count} jobs"
    else:
        caption = "(No jobs found)"

    table = create_jobs_table("Slurm job status", verbose, jobs, caption)
    console = Console()
    console.print(table, overflow="ellipsis")
