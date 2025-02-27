# Copyright 2025 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

import click

import ubuntu_cloud_archive.backports as uca_backports
from ubuntu_cloud_archive.core import errors as uca_errors
from ubuntu_cloud_archive.core import git
from ubuntu_cloud_archive.core import schema as uca_schema


@click.group("schema")
def cli():
    pass


@cli.command()
@click.option(
    "--format",
    help="The output format",
    default="value",
    type=click.Choice(["json", "value"]),
)
def targets(format: str):
    """List the available backport targets."""
    targets = [
        backport.name.removesuffix(".yaml") for backport in uca_backports.backports()
    ]

    if format == "json":
        click.echo(json.dumps(targets))
    else:
        for target in targets:
            click.echo(target)


@cli.command()
@click.option(
    "--target",
    help="The target os_release-series to validate",
    default=None,
    type=str,
)
def validate(target: str | None):
    """Validate backport files against the schema."""
    backports = []
    if target:
        try:
            backports.append(uca_backports.backport(target))
        except FileNotFoundError:
            raise click.ClickException(f"No backports found for target {target}")
    else:
        backports.extend(uca_backports.backports())

    for backport_file in backports:
        click.echo(f"Validating {backport_file}")
        try:
            backport = uca_schema.BackportFile.load(backport_file)
            click.echo(
                f"Target {backport.target} contains {len(backport.packages)} packages"
            )
        except uca_errors.ValidationError as e:
            click.echo(f"Failed to validate {backport_file}: {e}")


@cli.command()
@click.argument("target", type=str)
@click.option(
    "--format",
    help="The output format",
    default="value",
    type=click.Choice(["json", "value"]),
)
@click.option(
    "--updated",
    help="Show only updated packages",
    is_flag=True,
)
@click.option(
    "--added",
    help="Show only added packages",
    is_flag=True,
)
@click.option(
    "--removed",
    help="Show only removed packages",
    is_flag=True,
)
def diff(target: str, format: str, updated: bool, added: bool, removed: bool):
    """Show package differences between backport and previous history."""
    rev_count = git.get_rev_count()
    if rev_count < 2:
        raise click.ClickException("Need at least two git revisions to compare")

    try:
        target_path = uca_backports.backport(target)
    except FileNotFoundError:
        raise click.ClickException(f"No backport found for target {target}")
    current = uca_schema.BackportFile.load(target_path)
    previous = uca_schema.BackportFile.from_string(
        target, git.get_previous_content(target_path)
    )

    diff = previous.diff(current)
    if not diff.added and not diff.removed and not diff.updated:
        if format == "json":
            click.echo("{}")
        else:
            click.echo("No changes detected")
        return

    show_all = not (updated or added or removed)

    if format == "json":
        fields_to_dump = set()
        if show_all or added:
            fields_to_dump.add("added")
        if show_all or removed:
            fields_to_dump.add("removed")
        if show_all or updated:
            fields_to_dump.add("updated")

        click.echo(diff.model_dump_json(include=fields_to_dump))
        return

    click.echo(f"Diff for {target}")
    if show_all or added:
        click.echo("Added:")
        for package in diff.added:
            click.echo(f"  {package.package}")
    if show_all or removed:
        click.echo("Removed:")
        for package in diff.removed:
            click.echo(f"  {package.package}")
    if show_all or updated:
        click.echo("Updated:")
        for package in diff.updated:
            click.echo(f"  {package.package}")
