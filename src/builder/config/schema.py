"""Pydantic schemas for builder configuration."""

from pathlib import Path
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    model_config = ConfigDict(extra="forbid")

    type: Literal["file"]
    source: Path
    target: Path
    chmod: str | int = "644"
    chown: str = "root:root"

    @field_validator("chmod", mode="before")
    @classmethod
    def normalize_chmod(cls, v: str | int) -> str:
        """Convert chmod to string format."""
        if isinstance(v, int):
            return str(v)
        return v


class DirectoryComponent(BaseModel):
    """Directory deployment component."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["directory"]
    source: Path
    target: Path
    chmod: str | int = "755"
    chown: str = "root:root"

    @field_validator("chmod", mode="before")
    @classmethod
    def normalize_chmod(cls, v: str | int) -> str:
        """Convert chmod to string format."""
        if isinstance(v, int):
            return str(v)
        return v


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

    @field_validator("components", mode="before")
    @classmethod
    def ensure_list(cls, v: list | None) -> list:
        """Ensure components is a list."""
        if v is None:
            return []
        return v
