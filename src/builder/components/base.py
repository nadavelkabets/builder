"""Abstract base class for component handlers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ComponentHandler(ABC, Generic[T]):
    """Abstract base class for component handlers."""

    def __init__(self, component: T, config_dir: Path) -> None:
        """Initialize the handler.

        Args:
            component: The component configuration.
            config_dir: Directory containing the config file (for resolving relative paths).
        """
        self.component = component
        self.config_dir = config_dir

    def resolve_source(self, source: Path) -> Path:
        """Resolve a source path relative to config directory.

        Args:
            source: Source path from component config.

        Returns:
            Absolute path to the source.
        """
        if source.is_absolute():
            return source
        return self.config_dir / source

    def resolve_target(self, build_dir: Path, target: Path) -> Path:
        """Resolve a target path within the build directory.

        Args:
            build_dir: Path to the deb package build directory.
            target: Target path from component config.

        Returns:
            Absolute path within the build directory.
        """
        # Strip leading slash to make it relative, then join with build_dir
        target_relative = str(target).lstrip("/")
        return build_dir / target_relative

    @abstractmethod
    def stage(self, build_dir: Path) -> None:
        """Stage the component files into the build directory.

        The build directory will become the deb package content,
        which is later installed to the rootfs via chroot + dpkg.

        Args:
            build_dir: Path to the deb package build directory.
        """
        pass
