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
import subprocess

from .errors import GitError


def git(*args):
    try:
        return subprocess.check_output(
            ["git"] + list(args),
            stderr=subprocess.PIPE,
            encoding="utf-8",
        ).strip()
    except subprocess.CalledProcessError as e:
        raise GitError(e.stderr) from e


def get_rev_count() -> int:
    return int(git("rev-list", "--count", "--all"))


def get_top_level() -> pathlib.Path:
    """Get the root of the git repository."""
    return pathlib.Path(git("rev-parse", "--show-toplevel"))


def get_previous_content(path: pathlib.Path) -> str:
    """Get the content of the file at the previous commit.

    If new file, returns an empty string.
    """

    root = get_top_level()
    path = path.relative_to(root)

    try:
        return git("show", f"HEAD~1:{path}")
    except GitError as e:
        msg = str(e)
        if "exists on disk, but not in 'HEAD~1'" in msg:
            return ""
        raise
