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

import pathlib
import typing


def backports() -> typing.Sequence[pathlib.Path]:
    """Return a list of backport files."""
    current_directory = pathlib.Path(__file__).parent

    return list(current_directory.glob("*.yaml"))

def backport(name: str) -> pathlib.Path:
    """Return the path to a backport file."""
    target = pathlib.Path(__file__).parent / f"{name}.yaml"
    if not target.exists():
        raise FileNotFoundError(f"Backport file {name} not found.")
    return target
