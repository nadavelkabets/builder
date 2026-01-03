"""Shell command execution utilities."""

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CommandResult:
    """Result of a shell command execution."""

    returncode: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        """Check if command succeeded."""
        return self.returncode == 0


class ShellError(Exception):
    """Exception raised when a shell command fails."""

    def __init__(self, cmd: list[str], result: CommandResult) -> None:
        self.cmd = cmd
        self.result = result
        super().__init__(
            f"Command failed with code {result.returncode}: {' '.join(cmd)}\n"
            f"stderr: {result.stderr}"
        )


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    capture: bool = True,
    env: dict[str, str] | None = None,
) -> CommandResult:
    """
    Execute a shell command safely.

    Args:
        cmd: Command and arguments as a list (never use shell=True).
        cwd: Working directory for the command.
        check: Raise ShellError if command fails.
        capture: Capture stdout/stderr (if False, streams to console).
        env: Environment variables to set.

    Returns:
        CommandResult with return code and output.

    Raises:
        ShellError: If check=True and command fails.
    """
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture,
        text=True,
        env=env,
    )

    cmd_result = CommandResult(
        returncode=result.returncode,
        stdout=result.stdout if capture else "",
        stderr=result.stderr if capture else "",
    )

    if check and not cmd_result.success:
        raise ShellError(cmd, cmd_result)

    return cmd_result


def run_chroot(
    rootfs: Path,
    cmd: list[str],
    *,
    check: bool = True,
    capture: bool = True,
) -> CommandResult:
    """
    Execute a command inside a chroot environment.

    Args:
        rootfs: Path to the rootfs directory.
        cmd: Command and arguments to run inside chroot.
        check: Raise ShellError if command fails.
        capture: Capture stdout/stderr.

    Returns:
        CommandResult with return code and output.
    """
    return run(
        ["chroot", str(rootfs), *cmd],
        check=check,
        capture=capture,
    )
