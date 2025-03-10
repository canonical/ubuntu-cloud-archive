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

import click

from ubuntu_cloud_archive.cli import schema

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group("init", context_settings=CONTEXT_SETTINGS)
def cli():
    pass


def main():
    cli.add_command(schema.cli)

    cli()


if __name__ == "__main__":
    main()
