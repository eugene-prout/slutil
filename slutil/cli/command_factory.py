from __future__ import annotations

import functools
import inspect
from dataclasses import dataclass
import click
from slutil.cli.cmd_hide import cmd_hide
from slutil.cli.cmd_filter import cmd_filter
from slutil.cli.cmd_report import cmd_report
from slutil.cli.cmd_unhide import cmd_unhide
from slutil.cli.cmd_submit import cmd_submit
from slutil.cli.cmd_status import cmd_status
from slutil.cli.cmd_recent import cmd_recent
from slutil.cli.cmd_edit import cmd_edit
from slutil.cli.cmd_init import cmd_init
import re
from typing import Any, Callable, Optional


def inject_dependencies(function, dependencies: dict[str, Callable]):
    params = inspect.signature(function).parameters

    deps = {
        name: dependency
        for name, dependency in dependencies.items()
        if name in params
    }

    return functools.partial(function, **deps)

@dataclass
class CommandSpec:
    name: str
    func: Callable
    params: list[click.Parameter]


def command_factory(dependencies: dict[str, Any]) -> click.Group:
    parent_cmd = click.Group()

    def validate_dependency_str(ctx, param, value) -> tuple[Optional[str], list[int]]:
        if value:
            if re.match(
                r"^(((after|afterany|afternotok|afterok)(:([\d])*)+)|singleton)$", value
            ):
                dep_type, *numbers = value.split(":")
                return (dep_type, numbers)
            raise click.BadParameter("not a supported dependency option")
        return (None, [])

    commands = [
        CommandSpec(
            name="submit",
            func=cmd_submit,
            params=[
                click.Argument(
                    ["sbatch_file"], required=True, type=click.Path(exists=True)
                ),
                click.Argument(["description"], required=True, type=str),
                click.Option(
                    ["-dp", "--dependency"],
                    required=False,
                    type=str,
                    callback=validate_dependency_str,
                    help="The job's dependencies. In the form ('<type>(:[dependent_id])+' type:=after|afterany|afternotok|afterok) or 'singleton' e.g. 'afterok:123456:345678'"
                )]),
        CommandSpec(
            name="report",
            func=cmd_report,
            params=[
                click.Option(["-v", "--verbose"], is_flag=True, default=False)
            ]),
        CommandSpec(
            name="recent",
            func=cmd_recent,
            params=[
                click.Option(["-c", "--count"], default=10),
                click.Option(["-v", "--verbose"], is_flag=True, default=False),
                click.Option(
                    ["-l", "--live"], help="infinitely refresh the display with new data", is_flag=True, default=False),
            ]),
        CommandSpec(
            name="status",
            func=cmd_status,
            params=[
                click.Argument(["slurm_id"], type=int),
                click.Option(["-v", "--verbose"], is_flag=True, default=False),
            ]),
        CommandSpec(
            name="delete",
            func=cmd_hide,
            params=[
                click.Argument(["slurm_id"], type=int),
                click.Option(["-v", "--verbose"], is_flag=True, default=False),
            ],
        ),
        CommandSpec(
            name="restore",
            func=cmd_unhide,
            params=[
                click.Argument(["slurm_id"], type=int),
            ],
        ),
        CommandSpec(
            name="edit",
            func=cmd_edit,
            params=[
                click.Argument(["slurm_id"], type=int),
            ]
        ),
        CommandSpec(
            name="filter",
            func=cmd_filter,
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
        ),
        CommandSpec(
            name="init",
            func=cmd_init,
            params=[]
        )
    ]

    for c in commands:
        parent_cmd.add_command(
            click.Command(
                name=c.name,
                callback=inject_dependencies(c.func, dependencies),
                params=c.params,
                help=c.func.__doc__,
            )
        )

    return parent_cmd
