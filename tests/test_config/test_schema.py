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


class TestDockerComposeComponent:
    """Tests for DockerComposeComponent schema."""

    def test_valid_component(self) -> None:
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

    def test_invalid_operation(self) -> None:
        """Test invalid operation raises error."""
        with pytest.raises(ValidationError):
            DockerComposeComponent(
                type="docker-compose",
                path=Path("./compose/app.yaml"),
                target=Path("/opt/app"),
                operation="invalid",
                services=["api"],
            )


class TestSystemdComponent:
    """Tests for SystemdComponent schema."""

    def test_valid_component(self) -> None:
        """Test valid systemd component."""
        component = SystemdComponent(
            type="systemd",
            service=Path("./systemd/app.service"),
            enable=True,
        )
        assert component.enable is True

    def test_default_enable(self) -> None:
        """Test enable defaults to True."""
        component = SystemdComponent(
            type="systemd",
            service=Path("./systemd/app.service"),
        )
        assert component.enable is True


class TestFileComponent:
    """Tests for FileComponent schema."""

    def test_valid_component(self) -> None:
        """Test valid file component."""
        component = FileComponent(
            type="file",
            source=Path("./config/app.conf"),
            target=Path("/etc/app/app.conf"),
            chmod="644",
            chown="root:root",
        )
        assert component.chmod == "644"

    def test_chmod_as_int(self) -> None:
        """Test chmod accepts integer."""
        component = FileComponent(
            type="file",
            source=Path("./config/app.conf"),
            target=Path("/etc/app/app.conf"),
            chmod=755,
        )
        assert component.chmod == "755"

    def test_defaults(self) -> None:
        """Test default values."""
        component = FileComponent(
            type="file",
            source=Path("./config/app.conf"),
            target=Path("/etc/app/app.conf"),
        )
        assert component.chmod == "644"
        assert component.chown == "root:root"


class TestDirectoryComponent:
    """Tests for DirectoryComponent schema."""

    def test_valid_component(self) -> None:
        """Test valid directory component."""
        component = DirectoryComponent(
            type="directory",
            source=Path("./config"),
            target=Path("/etc/app"),
            chmod="755",
        )
        assert component.chmod == "755"

    def test_defaults(self) -> None:
        """Test default values."""
        component = DirectoryComponent(
            type="directory",
            source=Path("./config"),
            target=Path("/etc/app"),
        )
        assert component.chmod == "755"
        assert component.chown == "root:root"


class TestBuilderConfig:
    """Tests for BuilderConfig schema."""

    def test_valid_config(self) -> None:
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

    def test_empty_depends(self) -> None:
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

    def test_discriminated_union(self) -> None:
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

    def test_extra_fields_rejected(self) -> None:
        """Test extra fields are rejected."""
        with pytest.raises(ValidationError):
            BuilderConfig(
                depends=[],
                components=[],
                extra_field="not allowed",
            )
