"""Tests for configuration loading."""

import os
from pathlib import Path

import pytest

from builder.config import BuilderConfig, load_config


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_sample_config(self, sample_config_path: Path) -> None:
        """Test loading a sample configuration file."""
        config = load_config(sample_config_path)

        assert "depends" in config
        assert "components" in config
        assert len(config["depends"]) == 2
        assert len(config["components"]) == 4

    def test_load_nonexistent_file(self, tmp_path: Path) -> None:
        """Test loading a nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_config(tmp_path / "nonexistent.yaml")

    def test_validate_sample_config(self, sample_config_path: Path) -> None:
        """Test validating a sample configuration."""
        raw_config = load_config(sample_config_path)
        config = BuilderConfig.model_validate(raw_config)

        assert len(config.depends) == 2
        assert "docker-ce" in config.depends
        assert len(config.components) == 4

    def test_component_types(self, sample_config_path: Path) -> None:
        """Test all component types are parsed correctly."""
        raw_config = load_config(sample_config_path)
        config = BuilderConfig.model_validate(raw_config)

        types = [c.type for c in config.components]
        assert "docker-compose" in types
        assert "systemd" in types
        assert "file" in types
        assert "directory" in types


class TestEnvVarSubstitution:
    """Tests for !ENV tag substitution."""

    def test_env_var_required(self, env_config_path: Path) -> None:
        """Test required environment variable."""
        os.environ["CONFIG_PATH"] = "/path/to/config"

        try:
            config = load_config(env_config_path)
            assert config["components"][0]["source"] == "/path/to/config"
        finally:
            del os.environ["CONFIG_PATH"]

    def test_env_var_with_default(self, env_config_path: Path) -> None:
        """Test environment variable with default value."""
        os.environ["CONFIG_PATH"] = "/path/to/config"

        # TARGET_PATH not set, should use default
        if "TARGET_PATH" in os.environ:
            del os.environ["TARGET_PATH"]

        try:
            config = load_config(env_config_path)
            assert config["components"][0]["target"] == "/etc/default/app"
        finally:
            del os.environ["CONFIG_PATH"]

    def test_env_var_override_default(self, env_config_path: Path) -> None:
        """Test environment variable overrides default."""
        os.environ["CONFIG_PATH"] = "/path/to/config"
        os.environ["TARGET_PATH"] = "/custom/path"

        try:
            config = load_config(env_config_path)
            assert config["components"][0]["target"] == "/custom/path"
        finally:
            del os.environ["CONFIG_PATH"]
            del os.environ["TARGET_PATH"]

    def test_env_var_missing_raises(self, env_config_path: Path) -> None:
        """Test missing required environment variable raises error."""
        if "CONFIG_PATH" in os.environ:
            del os.environ["CONFIG_PATH"]

        with pytest.raises(ValueError, match="CONFIG_PATH"):
            load_config(env_config_path)
