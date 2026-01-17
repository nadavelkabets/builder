"""Tests for DockerComposeHandler."""

from pathlib import Path

from builder.components.docker_compose import DockerComposeHandler
from builder.config.schema import DockerComposeComponent


def test_docker_compose_handler_copies_file(tmp_path: Path) -> None:
    """Test that DockerComposeHandler copies compose file."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    compose_file = config_dir / "docker-compose.yaml"
    compose_file.write_text("services:\n  app:\n    image: nginx")

    build_dir = tmp_path / "build_dir"
    build_dir.mkdir()

    component = DockerComposeComponent(
        type="docker-compose",
        path=Path("docker-compose.yaml"),
        target=Path("/opt/myapp"),
        operation="pull",
        services=["app"],
    )
    handler = DockerComposeHandler(component, config_dir)
    handler.stage(build_dir)

    target = build_dir / "opt/myapp/docker-compose.yaml"
    assert target.exists()
    assert "nginx" in target.read_text()


def test_docker_compose_handler_creates_target_dir(tmp_path: Path) -> None:
    """Test that DockerComposeHandler creates target directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    compose_file = config_dir / "compose.yml"
    compose_file.write_text("services: {}")

    build_dir = tmp_path / "build_dir"
    build_dir.mkdir()

    component = DockerComposeComponent(
        type="docker-compose",
        path=Path("compose.yml"),
        target=Path("/opt/deep/nested/app"),
        operation="build",
        services=["web"],
    )
    handler = DockerComposeHandler(component, config_dir)
    handler.stage(build_dir)

    target_dir = build_dir / "opt/deep/nested/app"
    assert target_dir.exists()
    assert target_dir.is_dir()
    assert (target_dir / "compose.yml").exists()


def test_docker_compose_handler_sets_permissions(tmp_path: Path) -> None:
    """Test that DockerComposeHandler sets correct permissions."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    compose_file = config_dir / "docker-compose.yaml"
    compose_file.write_text("services: {}")

    build_dir = tmp_path / "build_dir"
    build_dir.mkdir()

    component = DockerComposeComponent(
        type="docker-compose",
        path=Path("docker-compose.yaml"),
        target=Path("/opt/app"),
        operation="pull",
        services=["app"],
    )
    handler = DockerComposeHandler(component, config_dir)
    handler.stage(build_dir)

    target = build_dir / "opt/app/docker-compose.yaml"
    assert target.stat().st_mode & 0o777 == 0o644
