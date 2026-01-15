"""File component handler."""

import shutil
from pathlib import Path

from builder.components.base import ComponentHandler
from builder.config.schema import FileComponent


class FileHandler(ComponentHandler[FileComponent]):
    """Handler for staging single files into the build directory."""

    def stage(self, build_dir: Path) -> None:
        """Stage file into the build directory.

        Args:
            build_dir: Path to the deb package build directory.
        """
        source = self.resolve_source(self.component.source)
        target = self.resolve_target(build_dir, self.component.target)

        # Ensure parent directory exists
        target.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(source, target)

        # Set permissions (chmod stored as octal string like "644")
        target.chmod(int(self.component.chmod, 8))
