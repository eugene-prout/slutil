import os
from rich.console import Console
from slutil.services.csv_uow import CsvUnitOfWork
from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.slurm import SlurmService
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.adapters.abstract_vcs import AbstractVCS
from slutil.adapters.git import Git
from slutil.cli.command_factory import command_factory
from dataclasses import dataclass
import logging




def start_cli():
    debug = os.getenv("SLUTIL_DEBUG", 'False').lower() in ('true', '1', 't')

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler("debug.log", "w")],
    )

    logging.debug("starting cli")

    dependencies = {
        "uow": CsvUnitOfWork(),
        "slurm_service": SlurmService(),
        "vcs": Git()
    }

    c = command_factory(dependencies)

    try:
        c()
    except Exception as e:
        if debug:
            raise e
        else:
            logging.exception("error inside command group")
            console = Console()
            console.print(f"[red]Error: {str(e)}[/red]")


if __name__ == "__main__":
    start_cli()
