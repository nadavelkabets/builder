"""Systemd component handler."""

import shutil
from pathlib import Path

from builder.components.base import ComponentHandler
from builder.config.schema import SystemdComponent


class SystemdHandler(ComponentHandler[SystemdComponent]):
    """Handler for staging systemd service files into the build directory."""

    SYSTEMD_DIR = Path("/etc/systemd/system")
    WANTS_DIR = SYSTEMD_DIR / "multi-user.target.wants"

    def stage(self, build_dir: Path) -> None:
        """Stage systemd service file into the build directory.

        Args:
            build_dir: Path to the deb package build directory.
        """
        source = self.resolve_source(self.component.service)
        service_name = source.name

        # Target location in systemd directory
        systemd_dir = self.resolve_target(build_dir, self.SYSTEMD_DIR)
        target = systemd_dir / service_name

        # Ensure systemd directory exists
        systemd_dir.mkdir(parents=True, exist_ok=True)

        # Copy service file
        shutil.copy2(source, target)
        target.chmod(0o644)

        # Enable service by creating symlink in wants directory
        if self.component.enable:
            wants_dir = self.resolve_target(build_dir, self.WANTS_DIR)
            wants_dir.mkdir(parents=True, exist_ok=True)

            symlink = wants_dir / service_name
            if symlink.exists() or symlink.is_symlink():
                symlink.unlink()

            # Create relative symlink pointing to ../service_name
            symlink.symlink_to(f"../{service_name}")
