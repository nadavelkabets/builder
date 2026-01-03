"""Custom !ENV YAML tag for environment variable substitution."""

import yaml
from envsubst import envsubst


class EnvVarConstructor:
    """
    YAML constructor for !ENV tag using python-envsubst.

    Supports:
        !ENV $VARNAME                         # Single required variable
        !ENV ${VARNAME}                       # Single required variable (explicit)
        !ENV ${VARNAME:-default}              # Single variable with default
        !ENV ${VAR1}/path/${VAR2}             # Multiple variables in text
        !ENV ${VAR1:-default1}/${VAR2:-default2} # Multiple with defaults
    """

    def __call__(self, loader: yaml.SafeLoader, node: yaml.Node) -> str:
        value = loader.construct_scalar(node)
        return envsubst(value)
