"""Tests for SystemdHandler."""

from pathlib import Path

from builder.components.systemd import SystemdHandler
from builder.config.schema import SystemdComponent


def test_systemd_handler_copies_service(tmp_path: Path) -> None:
    """Test that SystemdHandler copies service file."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    service_file = config_dir / "myapp.service"
    service_file.write_text("[Unit]\nDescription=My App")

    build_dir = tmp_path / "build_dir"
    build_dir.mkdir()

    component = SystemdComponent(
        type="systemd",
        service=Path("myapp.service"),
    )
    handler = SystemdHandler(component, config_dir)
    handler.stage(build_dir)

    target = build_dir / "etc/systemd/system/myapp.service"
    assert target.exists()
    assert target.read_text() == "[Unit]\nDescription=My App"


def test_systemd_handler_enables_service(tmp_path: Path) -> None:
    """Test that SystemdHandler creates enable symlink."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    service_file = config_dir / "myapp.service"
    service_file.write_text("[Unit]\nDescription=My App")

    build_dir = tmp_path / "build_dir"
    build_dir.mkdir()

    component = SystemdComponent(
        type="systemd",
        service=Path("myapp.service"),
        enable=True,
    )
    handler = SystemdHandler(component, config_dir)
    handler.stage(build_dir)

    symlink = build_dir / "etc/systemd/system/multi-user.target.wants/myapp.service"
    assert symlink.is_symlink()
    assert symlink.resolve().name == "myapp.service"


def test_systemd_handler_disable_no_symlink(tmp_path: Path) -> None:
    """Test that SystemdHandler does not create symlink when disabled."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    service_file = config_dir / "myapp.service"
    service_file.write_text("[Unit]\nDescription=My App")

    build_dir = tmp_path / "build_dir"
    build_dir.mkdir()

    component = SystemdComponent(
        type="systemd",
        service=Path("myapp.service"),
        enable=False,
    )
    handler = SystemdHandler(component, config_dir)
    handler.stage(build_dir)

    # Service file should exist
    target = build_dir / "etc/systemd/system/myapp.service"
    assert target.exists()

    # But no symlink in wants directory
    wants_dir = build_dir / "etc/systemd/system/multi-user.target.wants"
    assert not wants_dir.exists() or not (wants_dir / "myapp.service").exists()


def test_systemd_handler_sets_permissions(tmp_path: Path) -> None:
    """Test that SystemdHandler sets correct permissions on service file."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    service_file = config_dir / "myapp.service"
    service_file.write_text("[Unit]\nDescription=My App")

    build_dir = tmp_path / "build_dir"
    build_dir.mkdir()

    component = SystemdComponent(
        type="systemd",
        service=Path("myapp.service"),
    )
    handler = SystemdHandler(component, config_dir)
    handler.stage(build_dir)

    target = build_dir / "etc/systemd/system/myapp.service"
    assert target.stat().st_mode & 0o777 == 0o644
