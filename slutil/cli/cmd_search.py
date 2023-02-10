from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.services.services import search_description
from slutil.cli.formatter import create_jobs_table
from rich.console import Console

def cmd_search(
    uow: AbstractUnitOfWork,
    slurm: AbstractSlurmService,
    description: str,
    verbose: bool
):
    """Filter for slurm jobs containing by a fuzzy search of the description

    DESCRIPTION is the query for the description
    """
    jobs = search_description(uow, slurm, description)
    table = create_jobs_table(f"Descriptions containing {description}", verbose, jobs)
    console = Console()
    console.print(table, overflow="ellipsis")
