"""Tests for configuration loading."""

from pathlib import Path

import pytest

from builder.config import BuilderConfig, load_config


def test_load_sample_config(sample_config_path: Path) -> None:
    """Test loading a sample configuration file."""
    config = load_config(sample_config_path)

    assert "depends" in config
    assert "components" in config
    assert len(config["depends"]) == 2
    assert len(config["components"]) == 4


def test_load_nonexistent_file(tmp_path: Path) -> None:
    """Test loading a nonexistent file raises error."""
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nonexistent.yaml")


def test_validate_sample_config(sample_config_path: Path) -> None:
    """Test validating a sample configuration."""
    raw_config = load_config(sample_config_path)
    config = BuilderConfig.model_validate(raw_config)

    assert len(config.depends) == 2
    assert "docker-ce" in config.depends
    assert len(config.components) == 4


def test_component_types(sample_config_path: Path) -> None:
    """Test all component types are parsed correctly."""
    raw_config = load_config(sample_config_path)
    config = BuilderConfig.model_validate(raw_config)

    types = [c.type for c in config.components]
    assert "docker-compose" in types
    assert "systemd" in types
    assert "file" in types
    assert "directory" in types
