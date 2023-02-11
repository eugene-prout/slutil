import click
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.adapters.abstract_vcs import AbstractVCS
from slutil.cli.cmd_delete import cmd_delete
from slutil.cli.cmd_filter import cmd_filter
from slutil.cli.cmd_undelete import cmd_undelete
from slutil.services.abstract_uow import AbstractUnitOfWork
from slutil.cli.cmd_submit import cmd_submit
from slutil.cli.cmd_status import cmd_status
from slutil.cli.cmd_report import cmd_report
from slutil.cli.cmd_edit import cmd_edit


def command_factory(
    uow: AbstractUnitOfWork, slurm: AbstractSlurmService, vcs: AbstractVCS
) -> click.Group:
    parent_cmd = click.Group()

    parent_cmd.add_command(
        click.Command(
            name="submit",
            context_settings=None,
            callback=lambda sbatch_file, description: cmd_submit(
                uow, slurm, vcs, sbatch_file, description
            ),
            params=[
                click.Argument(
                    ["sbatch_file"], required=True, type=click.Path(exists=True)
                ),
                click.Argument(["description"], required=True, type=str),
            ],
        )
    )

    parent_cmd.add_command(
        click.Command(
            name="report",
            context_settings=None,
            callback=lambda count, verbose: cmd_report(uow, slurm, count, verbose),
            params=[
                click.Option(["-c", "--count"], default=10),
                click.Option(["-v", "--verbose"], is_flag=True, default=False),
            ],
        )
    )

    parent_cmd.add_command(
        click.Command(
            name="status",
            context_settings=None,
            callback=lambda slurm_id, verbose: cmd_status(
                uow, slurm, slurm_id, verbose
            ),
            params=[
                click.Argument(["slurm_id"], type=int),
                click.Option(["-v", "--verbose"], is_flag=True, default=False),
            ],
        )
    )

    parent_cmd.add_command(
        click.Command(
            name="delete",
            context_settings=None,
            callback=lambda slurm_id, verbose: cmd_delete(
                uow, slurm, slurm_id, verbose
            ),
            params=[
                click.Argument(["slurm_id"], type=int),
                click.Option(["-v", "--verbose"], is_flag=True, default=False),
            ],
        )
    )

    parent_cmd.add_command(
        click.Command(
            name="restore",
            context_settings=None,
            callback=lambda slurm_id: cmd_undelete(uow, slurm, slurm_id),
            params=[
                click.Argument(["slurm_id"], type=int),
            ],
        )
    )

    parent_cmd.add_command(
        click.Command(
            name="edit",
            context_settings=None,
            callback=lambda slurm_id: cmd_edit(uow, slurm, slurm_id),
            params=[
                click.Argument(["slurm_id"], type=int),
            ],
        )
    )

    parent_cmd.add_command(
        click.Command(
            name="filter",
            context_settings=None,
            callback=lambda job_id, status, description, submit_time, commit, sbatch, verbose: cmd_filter(
                uow,
                slurm,
                job_id,
                status,
                description,
                submit_time,
                commit,
                sbatch,
                verbose,
            ),
            params=[
                click.Option(["-j", "--job-id"], type=str, default=None),
                click.Option(["-s", "--status"], type=str, default=None),
                click.Option(["-d", "--description"], type=str, default=None),
                click.Option(["-t", "--submit-time"], type=str, default=None),
                click.Option(["-c", "--commit"], type=str, default=None),
                click.Option(["-sb", "--sbatch"], type=str, default=None),
                click.Option(["-v", "--verbose"], is_flag=True, default=False),
            ],
        )
    )

    return parent_cmd
