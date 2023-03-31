from rich.console import Console
from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.services.services import report
from slutil.cli.formatter import create_jobs_table
import logging

def cmd_report(
    uow: AbstractUnitOfWork,
    slurm: AbstractSlurmService,
    verbose: bool,
):
    """Display all jobs with changed state since the last time they were checked by slutil"""
    logging.debug(
        "cli: report requested, verbose: %s", verbose
    )

    response = report(slurm, uow)
    jobs = response.jobs
    caption = ""
    if len(jobs) > 0:
        caption = f"Showing jobs with changed state since last check"
    else:   
        caption = "(No jobs found with changed state, is Slurm accessible?)"

    title = "Slurm job status"
    if not response.fresh:
        title += f"\n[red](Slurm cannot be reached, showing cached data from {response.minimum_updated_time})[/red]"
    
    table = create_jobs_table(title, verbose, jobs, caption)

    console = Console()
    console.print(table, overflow="ellipsis")
