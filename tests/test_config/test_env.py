"""Tests for !ENV tag substitution."""

from pathlib import Path

from builder.config import load_config


def test_env_var_required(env_config_path: Path, env_vars: dict[str, str]) -> None:
    """Test required environment variable."""
    config = load_config(env_config_path)
    assert config["components"][0]["source"] == env_vars["CONFIG_PATH"]


def test_env_var_with_default(env_config_path: Path, env_vars: dict[str, str]) -> None:
    """Test environment variable with default value."""
    config = load_config(env_config_path)
    assert config["components"][0]["target"] == "/etc/default/app"


def test_env_var_override_default(
    env_config_path: Path, env_vars_with_target: dict[str, str]
) -> None:
    """Test environment variable overrides default."""
    config = load_config(env_config_path)
    assert config["components"][0]["target"] == env_vars_with_target["TARGET_PATH"]


def test_multiple_env_vars_in_value(
    multi_env_config_path: Path, multi_env_vars: dict[str, str]
) -> None:
    """Test multiple environment variables in a single value."""
    config = load_config(multi_env_config_path)
    assert config["components"][0]["source"] == "/home/user/config/testapp.conf"
    assert config["components"][0]["target"] == "/opt/testapp/config.conf"


def test_multiple_env_vars_with_default(
    multi_env_config_path: Path, multi_env_vars_custom: dict[str, str]
) -> None:
    """Test multiple env vars where some use defaults."""
    config = load_config(multi_env_config_path)
    assert config["components"][0]["target"] == "/opt/customapp/config.conf"
