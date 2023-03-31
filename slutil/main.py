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


@dataclass
class Dependencies:
    uow: AbstractUnitOfWork
    slurm: AbstractSlurmService
    vcs: AbstractVCS


def build_dependencies(debug: bool) -> Dependencies:
    uow = CsvUnitOfWork("")
    slurm = SlurmService()
    vcs = Git()
    return Dependencies(uow, slurm, vcs)


def start_cli():
    debug = False

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler("debug.log", "w")],
    )

    dependencies = build_dependencies(debug=debug)
    logging.debug(
        "starting cli with %s, %s, %s",
        dependencies.uow,
        dependencies.slurm,
        dependencies.vcs,
    )
    c = command_factory(dependencies.uow, dependencies.slurm, dependencies.vcs)

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
