"""Custom !ENV YAML tag for environment variable substitution."""

import os
import re

import yaml


class EnvVarConstructor:
    """
    YAML constructor for !ENV tag.

    Supports:
        !ENV VARNAME              # Required variable
        !ENV ${VARNAME}           # Required variable (explicit)
        !ENV ${VARNAME:default}   # With default value
    """

    ENV_PATTERN = re.compile(r"\$\{([^}:]+)(?::([^}]*))?\}|(\w+)")

    def __call__(self, loader: yaml.Loader, node: yaml.Node) -> str:
        value = loader.construct_scalar(node)
        match = self.ENV_PATTERN.match(value)

        if not match:
            return value

        var_name = match.group(1) or match.group(3)
        default = match.group(2)

        result = os.environ.get(var_name)
        if result is None:
            if default is not None:
                return default
            raise ValueError(f"Environment variable '{var_name}' is not set")
        return result


def add_env_constructor(loader_class: type[yaml.Loader]) -> None:
    """Register the !ENV constructor with a YAML loader class."""
    loader_class.add_constructor("!ENV", EnvVarConstructor())
