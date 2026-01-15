"""YAML configuration loader with !include and !ENV support."""

from pathlib import Path
from typing import Any

import yaml
from yaml_include import Constructor as IncludeConstructor

from builder.config.env import EnvVarConstructor


class BuilderLoader(yaml.SafeLoader):
    """Custom YAML loader with !include and !ENV support."""

    pass


def load_config(config_path: Path) -> dict[str, Any]:
    """
    Load a YAML configuration file with !include and !ENV support.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        yaml.YAMLError: If YAML parsing fails.
        ValueError: If environment variable is not set.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    # Register !include constructor with base directory
    IncludeConstructor.add_to_loader_class(
        loader_class=BuilderLoader,
        base_dir=config_path.parent,
    )

    # Register !ENV constructor
    BuilderLoader.add_constructor("!ENV", EnvVarConstructor())

    with open(config_path) as f:
        return yaml.load(f, Loader=BuilderLoader)
