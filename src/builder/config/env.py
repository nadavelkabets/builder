"""Custom !ENV YAML tag for environment variable substitution."""

import re

import yaml
from expandvars import expandvars


class EnvVarConstructor:
    """
    YAML constructor for !ENV tag using expandvars.

    Supports bash-style variable expansion:
        !ENV VARNAME                          # Bare variable name
        !ENV $VARNAME                         # Variable (empty if unset)
        !ENV ${VARNAME}                       # Variable (empty if unset)
        !ENV ${VARNAME:-default}              # Default if unset or empty
        !ENV ${VARNAME:?}                     # Error if unset or empty
        !ENV ${VAR1}/path/${VAR2}             # Multiple variables
        !ENV ${VAR1:-default1}/${VAR2:-default2}  # Multiple with defaults
    """

    # Pattern for bare variable name (no $ or special chars)
    BARE_VAR_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def __call__(self, loader: yaml.SafeLoader, node: yaml.Node) -> str:
        value = loader.construct_scalar(node)

        # If it's a bare variable name (no $), convert to ${VAR} syntax
        if self.BARE_VAR_PATTERN.match(value):
            value = f"${{{value}}}"

        return expandvars(value)
