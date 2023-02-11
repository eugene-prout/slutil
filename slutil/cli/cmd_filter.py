from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.services.services import filter_jobs, FilterQuery
from slutil.cli.formatter import create_jobs_table
from rich.console import Console
import re
from typing import Optional


def cmd_filter(
    uow: AbstractUnitOfWork,
    slurm: AbstractSlurmService,
    job_id: Optional[str],
    status: Optional[str],
    description: Optional[str],
    timestamp: Optional[str],
    commit: Optional[str],
    sbatch: Optional[str],
    verbose: bool,
):
    """
    Display all jobs matching the specified regexes.

    \b
    NOTE:
    At least one filter must be set
    When filters are set to plaintext the filter acts as a fuzzy search
    For a strict text search, use anchors: ^phrase to search strictly for$
    When writing regex make sure your shell parses them correctly, e.g. | (or) is often interpreted as a pipe. Make sure to escape or quote such characters
    For best results, wrap each regex string with double quotes
    """
    fields = (job_id, status, description, timestamp, commit, sbatch)
    if not any(fields):
        raise ValueError("Please supply at least 1 filter")

    def null_safe_re_compile(field: Optional[str]) -> Optional[re.Pattern]:
        if field is None:
            return field
        else:
            return re.compile(field)

    filter_compiled = [null_safe_re_compile(field) for field in fields]

    query = FilterQuery(*filter_compiled)
    matched_jobs = filter_jobs(uow, slurm, query)

    filter_description = []
    if job_id:
        filter_description.append(f"id matching '{job_id}'")
    if status:
        filter_description.append(f"status matching '{status}'")
    if description:
        filter_description.append(f"description matching '{description}'")
    if timestamp:
        filter_description.append(f"timestamp matching '{timestamp}'")
    if commit:
        filter_description.append(f"commit matching '{commit}'")
    if sbatch:
        filter_description.append(f"sbatch file matching '{sbatch}'")

    output = f"{(len(matched_jobs))} jobs with: {' and '.join(filter_description)}"
    console = Console()
    if len(matched_jobs) == 0:
        console.print(output)
    else:
        table = create_jobs_table(output, verbose, matched_jobs)
        console.print(table, overflow="ellipsis")
