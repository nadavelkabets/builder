"""Custom !ENV YAML tag for environment variable substitution."""

import os
import re

import yaml


class EnvVarConstructor:
    """
    YAML constructor for !ENV tag.

    Supports:
        !ENV VARNAME                          # Single required variable
        !ENV ${VARNAME}                       # Single required variable (explicit)
        !ENV ${VARNAME:default}               # Single variable with default
        !ENV ${VAR1}/path/${VAR2}             # Multiple variables in text
        !ENV ${VAR1:default1}/${VAR2:default2} # Multiple with defaults
    """

    # Pattern matches ${VARNAME} or ${VARNAME:default}
    ENV_PATTERN = re.compile(r"\$\{([^}:]+)(?::([^}]*))?\}")
    # Pattern for bare variable name (no ${})
    BARE_PATTERN = re.compile(r"^(\w+)$")

    def _replace_env_var(self, match: re.Match) -> str:
        """Replace a single environment variable match."""
        var_name = match.group(1)
        default = match.group(2)

        result = os.environ.get(var_name, default)
        if result is None:
            raise ValueError(f"Environment variable '{var_name}' is not set")
        return result

    def __call__(self, loader: yaml.SafeLoader, node: yaml.Node) -> str:
        value = loader.construct_scalar(node)

        # Handle bare variable name: !ENV VARNAME
        bare_match = self.BARE_PATTERN.match(value)
        if bare_match:
            var_name = bare_match.group(1)
            result = os.environ.get(var_name)
            if result is None:
                raise ValueError(f"Environment variable '{var_name}' is not set")
            return result

        # Handle ${VAR} patterns - supports multiple variables
        return self.ENV_PATTERN.sub(self._replace_env_var, value)
