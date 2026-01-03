"""Custom !ENV YAML tag for environment variable substitution."""

import yaml
from expandvars import expandvars


class EnvVarConstructor:
    """
    YAML constructor for !ENV tag using expandvars.

    Supports bash-style variable expansion:
        !ENV $VARNAME                         # Variable (empty if unset)
        !ENV ${VARNAME}                       # Variable (empty if unset)
        !ENV ${VARNAME:-default}              # Default if unset or empty
        !ENV ${VARNAME:?}                     # Error if unset or empty
        !ENV ${VAR1}/path/${VAR2}             # Multiple variables
        !ENV ${VAR1:-default1}/${VAR2:-default2}  # Multiple with defaults
    """

    def __call__(self, loader: yaml.SafeLoader, node: yaml.Node) -> str:
        value = loader.construct_scalar(node)
        return expandvars(value)
