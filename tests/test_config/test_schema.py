"""Tests for configuration schema validation."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from builder.config.schema import (
    BuilderConfig,
    DirectoryComponent,
    DockerComposeComponent,
    FileComponent,
    SystemdComponent,
)


# DockerComposeComponent tests

def test_docker_compose_valid() -> None:
    """Test valid docker-compose component."""
    component = DockerComposeComponent(
        type="docker-compose",
        path=Path("./compose/app.yaml"),
        target=Path("/opt/app"),
        operation="build",
        services=["api", "worker"],
    )
    assert component.operation == "build"
    assert len(component.services) == 2


def test_docker_compose_invalid_operation() -> None:
    """Test invalid operation raises error."""
    with pytest.raises(ValidationError):
        DockerComposeComponent(
            type="docker-compose",
            path=Path("./compose/app.yaml"),
            target=Path("/opt/app"),
            operation="invalid",
            services=["api"],
        )


# SystemdComponent tests

def test_systemd_valid() -> None:
    """Test valid systemd component."""
    component = SystemdComponent(
        type="systemd",
        service=Path("./systemd/app.service"),
        enable=True,
    )
    assert component.enable is True


def test_systemd_default_enable() -> None:
    """Test enable defaults to True."""
    component = SystemdComponent(
        type="systemd",
        service=Path("./systemd/app.service"),
    )
    assert component.enable is True


# FileComponent tests

def test_file_valid() -> None:
    """Test valid file component."""
    component = FileComponent(
        type="file",
        source=Path("./config/app.conf"),
        target=Path("/etc/app/app.conf"),
        chmod="644",
        chown="root:root",
    )
    assert component.chmod == "644"


def test_file_chmod_as_int() -> None:
    """Test chmod accepts integer."""
    component = FileComponent(
        type="file",
        source=Path("./config/app.conf"),
        target=Path("/etc/app/app.conf"),
        chmod=755,
    )
    assert component.chmod == "755"


def test_file_defaults() -> None:
    """Test default values."""
    component = FileComponent(
        type="file",
        source=Path("./config/app.conf"),
        target=Path("/etc/app/app.conf"),
    )
    assert component.chmod == "644"
    assert component.chown == "root:root"


# DirectoryComponent tests

def test_directory_valid() -> None:
    """Test valid directory component."""
    component = DirectoryComponent(
        type="directory",
        source=Path("./config"),
        target=Path("/etc/app"),
        chmod="755",
    )
    assert component.chmod == "755"


def test_directory_defaults() -> None:
    """Test default values."""
    component = DirectoryComponent(
        type="directory",
        source=Path("./config"),
        target=Path("/etc/app"),
    )
    assert component.chmod == "755"
    assert component.chown == "root:root"


# BuilderConfig tests

def test_config_valid() -> None:
    """Test valid full configuration."""
    config = BuilderConfig(
        depends=["docker-ce"],
        components=[
            {
                "type": "docker-compose",
                "path": "./compose/app.yaml",
                "target": "/opt/app",
                "operation": "pull",
                "services": ["api"],
            },
            {
                "type": "systemd",
                "service": "./systemd/app.service",
                "enable": True,
            },
        ],
    )
    assert len(config.depends) == 1
    assert len(config.components) == 2


def test_config_empty_depends() -> None:
    """Test empty depends is allowed."""
    config = BuilderConfig(
        components=[
            {
                "type": "file",
                "source": "./config.txt",
                "target": "/etc/config.txt",
            },
        ],
    )
    assert config.depends == []


def test_config_discriminated_union() -> None:
    """Test component type discrimination works."""
    config = BuilderConfig(
        components=[
            {
                "type": "file",
                "source": "./a.txt",
                "target": "/a.txt",
            },
            {
                "type": "directory",
                "source": "./dir",
                "target": "/dir",
            },
        ],
    )
    assert isinstance(config.components[0], FileComponent)
    assert isinstance(config.components[1], DirectoryComponent)


def test_config_extra_fields_rejected() -> None:
    """Test extra fields are rejected."""
    with pytest.raises(ValidationError):
        BuilderConfig(
            depends=[],
            components=[],
            extra_field="not allowed",
        )
