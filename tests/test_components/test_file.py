"""Tests for FileHandler."""

from pathlib import Path

from builder.components.file import FileHandler
from builder.config.schema import FileComponent


def test_file_handler_copies_file(tmp_path: Path) -> None:
    """Test that FileHandler copies file to correct location."""
    # Setup source file
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    source_file = config_dir / "app.conf"
    source_file.write_text("key=value")

    # Setup build_dir
    build_dir = tmp_path / "build_dir"
    build_dir.mkdir()

    # Create component and handler
    component = FileComponent(
        type="file",
        source=Path("app.conf"),
        target=Path("/etc/app/app.conf"),
    )
    handler = FileHandler(component, config_dir)

    # Apply
    handler.stage(build_dir)

    # Verify
    target = build_dir / "etc/app/app.conf"
    assert target.exists()
    assert target.read_text() == "key=value"


def test_file_handler_sets_permissions(tmp_path: Path) -> None:
    """Test that FileHandler sets correct permissions."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    source_file = config_dir / "script.sh"
    source_file.write_text("#!/bin/bash")

    build_dir = tmp_path / "build_dir"
    build_dir.mkdir()

    component = FileComponent(
        type="file",
        source=Path("script.sh"),
        target=Path("/usr/local/bin/script.sh"),
        chmod="755",
    )
    handler = FileHandler(component, config_dir)
    handler.stage(build_dir)

    target = build_dir / "usr/local/bin/script.sh"
    assert target.stat().st_mode & 0o777 == 0o755


def test_file_handler_absolute_source(tmp_path: Path) -> None:
    """Test that FileHandler handles absolute source paths."""
    # Source outside config_dir
    source_dir = tmp_path / "external"
    source_dir.mkdir()
    source_file = source_dir / "external.conf"
    source_file.write_text("external=true")

    config_dir = tmp_path / "config"
    config_dir.mkdir()

    build_dir = tmp_path / "build_dir"
    build_dir.mkdir()

    component = FileComponent(
        type="file",
        source=source_file,  # Absolute path
        target=Path("/etc/external.conf"),
    )
    handler = FileHandler(component, config_dir)
    handler.stage(build_dir)

    target = build_dir / "etc/external.conf"
    assert target.exists()
    assert target.read_text() == "external=true"


def test_file_handler_creates_parent_dirs(tmp_path: Path) -> None:
    """Test that FileHandler creates parent directories."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    source_file = config_dir / "deep.conf"
    source_file.write_text("deep=true")

    build_dir = tmp_path / "build_dir"
    build_dir.mkdir()

    component = FileComponent(
        type="file",
        source=Path("deep.conf"),
        target=Path("/very/deep/nested/path/deep.conf"),
    )
    handler = FileHandler(component, config_dir)
    handler.stage(build_dir)

    target = build_dir / "very/deep/nested/path/deep.conf"
    assert target.exists()
