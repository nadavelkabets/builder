"""Directory component handler."""

import shutil
from pathlib import Path

from builder.components.base import ComponentHandler
from builder.config.schema import DirectoryComponent


class DirectoryHandler(ComponentHandler[DirectoryComponent]):
    """Handler for staging directories into the build directory."""

    def stage(self, build_dir: Path) -> None:
        """Stage directory into the build directory.

        Args:
            build_dir: Path to the deb package build directory.
        """
        source = self.resolve_source(self.component.source)
        target = self.resolve_target(build_dir, self.component.target)

        # Ensure parent directory exists
        target.parent.mkdir(parents=True, exist_ok=True)

        # Copy directory tree (remove target first if exists)
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)

        # Set permissions recursively
        mode = int(self.component.chmod, 8)
        for path in target.rglob("*"):
            if path.is_file():
                # Files get chmod without execute bits (unless source had them)
                path.chmod(mode & 0o666 | (path.stat().st_mode & 0o111))
            else:
                path.chmod(mode)
        target.chmod(mode)
