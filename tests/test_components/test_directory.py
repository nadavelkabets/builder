"""Tests for DirectoryHandler."""

from pathlib import Path

from builder.components.directory import DirectoryHandler
from builder.config.schema import DirectoryComponent


def test_directory_handler_copies_directory(tmp_path: Path) -> None:
    """Test that DirectoryHandler copies directory tree."""
    # Setup source directory
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    source_dir = config_dir / "myapp"
    source_dir.mkdir()
    (source_dir / "config.yaml").write_text("key: value")
    (source_dir / "subdir").mkdir()
    (source_dir / "subdir/nested.txt").write_text("nested")

    # Setup build_dir
    build_dir = tmp_path / "build_dir"
    build_dir.mkdir()

    # Create component and handler
    component = DirectoryComponent(
        type="directory",
        source=Path("myapp"),
        target=Path("/opt/myapp"),
    )
    handler = DirectoryHandler(component, config_dir)

    # Apply
    handler.stage(build_dir)

    # Verify
    target = build_dir / "opt/myapp"
    assert target.exists()
    assert target.is_dir()
    assert (target / "config.yaml").read_text() == "key: value"
    assert (target / "subdir/nested.txt").read_text() == "nested"


def test_directory_handler_sets_permissions(tmp_path: Path) -> None:
    """Test that DirectoryHandler sets correct permissions."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    source_dir = config_dir / "data"
    source_dir.mkdir()
    (source_dir / "file.txt").write_text("data")

    build_dir = tmp_path / "build_dir"
    build_dir.mkdir()

    component = DirectoryComponent(
        type="directory",
        source=Path("data"),
        target=Path("/var/data"),
        chmod="700",
    )
    handler = DirectoryHandler(component, config_dir)
    handler.stage(build_dir)

    target = build_dir / "var/data"
    assert target.stat().st_mode & 0o777 == 0o700


def test_directory_handler_replaces_existing(tmp_path: Path) -> None:
    """Test that DirectoryHandler replaces existing directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    source_dir = config_dir / "app"
    source_dir.mkdir()
    (source_dir / "new.txt").write_text("new content")

    build_dir = tmp_path / "build_dir"
    build_dir.mkdir()

    # Create existing directory with different content
    existing = build_dir / "opt/app"
    existing.mkdir(parents=True)
    (existing / "old.txt").write_text("old content")

    component = DirectoryComponent(
        type="directory",
        source=Path("app"),
        target=Path("/opt/app"),
    )
    handler = DirectoryHandler(component, config_dir)
    handler.stage(build_dir)

    target = build_dir / "opt/app"
    assert (target / "new.txt").exists()
    assert not (target / "old.txt").exists()
