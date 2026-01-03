"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def sample_config_path(fixtures_dir: Path) -> Path:
    """Return path to sample configuration file."""
    return fixtures_dir / "sample-config.yaml"


@pytest.fixture
def env_config_path(fixtures_dir: Path) -> Path:
    """Return path to config with environment variables."""
    return fixtures_dir / "env-config.yaml"


@pytest.fixture
def temp_rootfs(tmp_path: Path) -> Path:
    """Create minimal rootfs structure for testing."""
    rootfs = tmp_path / "rootfs"
    (rootfs / "var/lib/docker").mkdir(parents=True)
    (rootfs / "etc/systemd/system").mkdir(parents=True)
    (rootfs / "usr/local/bin").mkdir(parents=True)
    return rootfs
