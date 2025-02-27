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

import pydantic
import yaml

from ..errors import ValidationError


class BackportPackage(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        extra="forbid",
    )

    package: str
    suffix: str = pydantic.Field(
        default="~cloud0",
        description="Use higher suffix to force a new backport",
    )
    reason: str | None = pydantic.Field(
        default=None,
        description="Reason for backporting",
    )

    def is_updated(self, other: "BackportPackage") -> bool:
        """Is that an updated version of the same package?"""
        if self.package != other.package:
            raise ValueError("not the same package")

        return self.suffix != other.suffix


def require_unique(bps: list[BackportPackage]):
    packages = [bp.package for bp in bps]
    if len(packages) != len(list(set(packages))):
        raise ValueError("not unique")
    return bps


RequireUniqueDuringValidation = pydantic.AfterValidator(require_unique)


class DiffResult(pydantic.BaseModel):
    added: typing.Sequence[BackportPackage]
    removed: typing.Sequence[BackportPackage]
    updated: typing.Sequence[BackportPackage]


class BackportFile(pydantic.BaseModel):
    root: typing.Annotated[list[BackportPackage], RequireUniqueDuringValidation]
    _name: str = pydantic.PrivateAttr()
    _path: str | None = pydantic.PrivateAttr(None)

    @classmethod
    def load(cls, path: pathlib.Path) -> "BackportFile":
        data = yaml.safe_load(path.read_text()) or []
        name = path.name.removesuffix(".yaml")
        try:
            model = cls.model_validate({"root": data})
        except pydantic.ValidationError as e:
            raise ValidationError(e)
        model._name = name
        model._path = str(path)
        return model

    @classmethod
    def from_string(cls, name: str, data: str) -> "BackportFile":
        try:
            model = cls.model_validate({"root": yaml.safe_load(data) or []})
        except pydantic.ValidationError as e:
            raise ValidationError(e)
        model._name = name
        model._path = None
        return model

    @property
    def target(self) -> str:
        return self._name

    @property
    def packages(self) -> typing.Sequence[BackportPackage]:
        return self.root

    def diff(self, other: "BackportFile") -> DiffResult:
        """Compute the difference between two backport files."""
        current_pkgs = {p.package: p for p in self.packages}
        other_pkgs = {p.package: p for p in other.packages}

        added = [p for p in other.packages if p.package not in current_pkgs]
        removed = [p for p in self.packages if p.package not in other_pkgs]
        updated = [
            o_p
            for p in self.packages
            if (o_p := other_pkgs.get(p.package)) and p.is_updated(o_p)
        ]
        return DiffResult(added=added, removed=removed, updated=updated)
