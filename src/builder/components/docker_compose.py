"""Docker Compose component handler."""

import shutil
from pathlib import Path

from builder.components.base import ComponentHandler
from builder.config.schema import DockerComposeComponent


class DockerComposeHandler(ComponentHandler[DockerComposeComponent]):
    """Handler for staging docker-compose configurations into the build directory.

    This handler copies the docker-compose file to the target location.
    The actual build/pull operations are handled by the Docker manager
    during the build phase (Phase 3).
    """

    def stage(self, build_dir: Path) -> None:
        """Stage docker-compose file into the build directory.

        Args:
            build_dir: Path to the deb package build directory.
        """
        source = self.resolve_source(self.component.path)
        target = self.resolve_target(build_dir, self.component.target)

        # Ensure target directory exists
        target.mkdir(parents=True, exist_ok=True)

        # Copy compose file to target directory
        dest_file = target / source.name
        shutil.copy2(source, dest_file)
        dest_file.chmod(0o644)
