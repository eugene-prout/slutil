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
            help=cmd_submit.__doc__,
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
            help=cmd_report.__doc__,
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
            help=cmd_status.__doc__,
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
            help=cmd_delete.__doc__,
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
            help=cmd_undelete.__doc__,
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
            help=cmd_edit.__doc__,
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
                click.Option(
                    ["-j", "--job-id"],
                    help="regex to match against job id",
                    type=str,
                    default=None,
                ),
                click.Option(
                    ["-s", "--status"],
                    help="regex to match against job status",
                    type=str,
                    default=None,
                ),
                click.Option(
                    ["-d", "--description"],
                    help="regex to match against job description",
                    type=str,
                    default=None,
                ),
                click.Option(
                    ["-t", "--submit-time"],
                    help="regex to match against string representation of submit timestamp (e.g. '2023-02-06 14:32:38')",
                    type=str,
                    default=None,
                ),
                click.Option(
                    ["-c", "--commit"],
                    help="regex to match against commit tag",
                    type=str,
                    default=None,
                ),
                click.Option(
                    ["-sb", "--sbatch"],
                    help="regex to match against sbatch file used",
                    type=str,
                    default=None,
                ),
                click.Option(["-v", "--verbose"], is_flag=True, default=False),
            ],
            help=cmd_filter.__doc__,
        )
    )

    return parent_cmd
