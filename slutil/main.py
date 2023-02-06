from rich.console import Console
from slutil.services.csv_uow import CsvUnitOfWork
from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.slurm import SlurmService
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.adapters.abstract_vcs import AbstractVCS
from slutil.adapters.git import Git
from slutil.cli.command_factory import command_factory
from dataclasses import dataclass
import os


@dataclass
class Dependencies:
    uow: AbstractUnitOfWork
    slurm: AbstractSlurmService
    vcs: AbstractVCS


def build_dependencies(debug: bool) -> Dependencies:
    if debug:
        uow = CsvUnitOfWork("")
        from tests.conftest import FakeSlurm, FakeVCS

        slurm = FakeSlurm()
        vcs = FakeVCS()
    else:
        uow = CsvUnitOfWork("")
        slurm = SlurmService()
        vcs = Git()
    return Dependencies(uow, slurm, vcs)


def start_cli():
    debug = False
    dependencies = build_dependencies(debug=debug)
    c = command_factory(dependencies.uow, dependencies.slurm, dependencies.vcs)
    try:
        c()
    except Exception as e:
        if debug:
            raise e
        else:
            console = Console()
            console.print(f"[red]Error: {str(e)}[/red]")


if __name__ == "__main__":
    start_cli()
