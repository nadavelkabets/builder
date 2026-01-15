"""Pydantic schemas for builder configuration."""

from pathlib import Path
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field


class DockerComposeComponent(BaseModel):
    """Docker Compose deployment component."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["docker-compose"]
    path: Path
    target: Path
    operation: Literal["build", "pull"]
    services: list[str]


class SystemdComponent(BaseModel):
    """Systemd service component."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["systemd"]
    service: Path
    enable: bool = True


class FileComponent(BaseModel):
    """Single file deployment component."""

    model_config = ConfigDict(extra="forbid", coerce_numbers_to_str=True)

    type: Literal["file"]
    source: Path
    target: Path
    chmod: str = "644"
    chown: str = "root:root"


class DirectoryComponent(BaseModel):
    """Directory deployment component."""

    model_config = ConfigDict(extra="forbid", coerce_numbers_to_str=True)

    type: Literal["directory"]
    source: Path
    target: Path
    chmod: str = "755"
    chown: str = "root:root"


Component = Annotated[
    Union[
        DockerComposeComponent,
        SystemdComponent,
        FileComponent,
        DirectoryComponent,
    ],
    Field(discriminator="type"),
]


class BuilderConfig(BaseModel):
    """Root configuration schema for builder."""

    model_config = ConfigDict(extra="forbid")

    depends: list[str] = Field(default_factory=list)
    components: list[Component]
