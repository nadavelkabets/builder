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
def multi_env_config_path(fixtures_dir: Path) -> Path:
    """Return path to config with multiple environment variables."""
    return fixtures_dir / "multi-env-config.yaml"


@pytest.fixture
def temp_rootfs(tmp_path: Path) -> Path:
    """Create minimal rootfs structure for testing."""
    rootfs = tmp_path / "rootfs"
    (rootfs / "var/lib/docker").mkdir(parents=True)
    (rootfs / "etc/systemd/system").mkdir(parents=True)
    (rootfs / "usr/local/bin").mkdir(parents=True)
    return rootfs


@pytest.fixture
def env_vars(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Set up basic environment variables for env-config.yaml tests."""
    vars = {"CONFIG_PATH": "/path/to/config"}
    for key, value in vars.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("TARGET_PATH", raising=False)
    return vars


@pytest.fixture
def env_vars_with_target(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Set up environment variables including TARGET_PATH override."""
    vars = {"CONFIG_PATH": "/path/to/config", "TARGET_PATH": "/custom/path"}
    for key, value in vars.items():
        monkeypatch.setenv(key, value)
    return vars


@pytest.fixture
def multi_env_vars(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Set up environment variables for multi-env-config.yaml tests."""
    vars = {"BASE_PATH": "/home/user", "APP_NAME": "testapp"}
    for key, value in vars.items():
        monkeypatch.setenv(key, value)
    return vars


@pytest.fixture
def multi_env_vars_custom(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Set up custom environment variables for multi-env tests."""
    vars = {"BASE_PATH": "/data", "APP_NAME": "customapp"}
    for key, value in vars.items():
        monkeypatch.setenv(key, value)
    return vars
