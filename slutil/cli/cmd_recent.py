import time
from rich.console import Console
from rich.live import Live
from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.services.services import report
from slutil.cli.formatter import create_jobs_table
import logging


def create_output(slurm, uow, count, verbose):
    response = report(slurm, uow, count)
    jobs = response.jobs
    if len(jobs) > 0:
        caption = f"Showing last {count} jobs"
    else:   
        caption = "(No jobs found)"
    if response.fresh:
        return create_jobs_table("Slurm job status", verbose, jobs, caption)
    else:
        return create_jobs_table(f"Slurm job status\n[red](Slurm cannot be reached, showing cached data from {response.minimum_updated_time})[/red]", verbose, jobs, caption)

def cmd_recent(
    uow: AbstractUnitOfWork,
    slurm: AbstractSlurmService,
    count: int,
    live: bool,
    verbose: bool,
):
    """Get status of multiple jobs"""
    logging.debug(
        "cli: report requested, count: %d, verbose: %s, live: %s", count, verbose, live
    )

    if live:
        with Live(
            create_output(slurm, uow, count, verbose), auto_refresh=False
        ) as view:
            while True:
                time.sleep(1)
                view.update(create_output(slurm, uow, count, verbose), refresh=True)
    else:
        Console().print(create_output(slurm, uow, count, verbose), overflow="ellipsis")
