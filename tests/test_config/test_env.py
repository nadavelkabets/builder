"""Tests for !ENV tag substitution."""

import os
from pathlib import Path

from builder.config import load_config


def test_env_var_required(env_config_path: Path) -> None:
    """Test required environment variable."""
    os.environ["CONFIG_PATH"] = "/path/to/config"

    try:
        config = load_config(env_config_path)
        assert config["components"][0]["source"] == "/path/to/config"
    finally:
        del os.environ["CONFIG_PATH"]


def test_env_var_with_default(env_config_path: Path) -> None:
    """Test environment variable with default value."""
    os.environ["CONFIG_PATH"] = "/path/to/config"

    if "TARGET_PATH" in os.environ:
        del os.environ["TARGET_PATH"]

    try:
        config = load_config(env_config_path)
        assert config["components"][0]["target"] == "/etc/default/app"
    finally:
        del os.environ["CONFIG_PATH"]


def test_env_var_override_default(env_config_path: Path) -> None:
    """Test environment variable overrides default."""
    os.environ["CONFIG_PATH"] = "/path/to/config"
    os.environ["TARGET_PATH"] = "/custom/path"

    try:
        config = load_config(env_config_path)
        assert config["components"][0]["target"] == "/custom/path"
    finally:
        del os.environ["CONFIG_PATH"]
        del os.environ["TARGET_PATH"]


def test_multiple_env_vars_in_value(multi_env_config_path: Path) -> None:
    """Test multiple environment variables in a single value."""
    os.environ["BASE_PATH"] = "/home/user"
    os.environ["APP_NAME"] = "testapp"

    try:
        config = load_config(multi_env_config_path)
        assert config["components"][0]["source"] == "/home/user/config/testapp.conf"
        assert config["components"][0]["target"] == "/opt/testapp/config.conf"
    finally:
        del os.environ["BASE_PATH"]
        del os.environ["APP_NAME"]


def test_multiple_env_vars_with_default(multi_env_config_path: Path) -> None:
    """Test multiple env vars where some use defaults."""
    os.environ["BASE_PATH"] = "/data"
    os.environ["APP_NAME"] = "customapp"

    try:
        config = load_config(multi_env_config_path)
        assert config["components"][0]["target"] == "/opt/customapp/config.conf"
    finally:
        del os.environ["BASE_PATH"]
        del os.environ["APP_NAME"]
