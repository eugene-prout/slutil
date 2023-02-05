from rich.console import Console
from slutil.services.csv_uow import CsvUnitOfWork
from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.adapters.slurm import SlurmService
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.cli.command_factory import command_factory
from dataclasses import dataclass


@dataclass
class Dependencies:
    uow: AbstractUnitOfWork
    slurm: AbstractSlurmService


def build_dependencies(debug: bool) -> Dependencies:
    if debug:
        uow = CsvUnitOfWork("")
        # from tests.conftest import FakeSlurm
        slurm = SlurmService()
    else:
        uow = CsvUnitOfWork("")
        slurm = SlurmService()
    return Dependencies(uow, slurm)


def start_cli():
    dependencies = build_dependencies(debug=True)
    c = command_factory(dependencies.uow, dependencies.slurm)
    try:
        c()
    except Exception as e:
        console = Console()
        console.print(f"[red]Error: {str(e)}[/red]")


if __name__ == "__main__":
    start_cli()
