"""Command-line interface for builder."""

from pathlib import Path

import click
from rich.console import Console

from builder import __version__
from builder.config import BuilderConfig, load_config

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="builder")
def main() -> None:
    """Deployment utility for embedded Linux projects."""
    pass


@main.command()
@click.option(
    "--rootfs",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Path to the mounted rootfs directory.",
)
@click.option(
    "--config",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to the YAML configuration file.",
)
@click.option(
    "--name",
    required=True,
    help="Bundle name (used for package naming).",
)
def build(rootfs: Path, config: Path, name: str) -> None:
    """Prepare rootfs with all configured components."""
    console.print(f"[bold blue]Builder[/] - Building {name}")
    console.print(f"  Rootfs: {rootfs}")
    console.print(f"  Config: {config}")

    # Load and validate configuration
    raw_config = load_config(config)
    builder_config = BuilderConfig.model_validate(raw_config)

    console.print(f"  Components: {len(builder_config.components)}")
    console.print(f"  Dependencies: {builder_config.depends}")

    # TODO: Implement build logic
    console.print("[yellow]Build command not yet implemented[/]")


@main.command()
@click.option(
    "--rootfs",
    required=True,
    help="Path or URL to the rootfs image (.img for RPi, .tar for Jetson).",
)
@click.option(
    "--config",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to the YAML configuration file.",
)
@click.option(
    "--name",
    required=True,
    help="Bundle name (used for package naming).",
)
@click.option(
    "--target",
    required=True,
    type=click.Choice(["jetson", "rpi"]),
    help="Target platform.",
)
@click.option(
    "--output",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("./bundle"),
    help="Output directory (default: ./bundle).",
)
@click.option(
    "--bsp",
    help="(Jetson only) Path or URL to the NVIDIA JetPack BSP.",
)
@click.option(
    "--workdir",
    type=click.Path(file_okay=False, path_type=Path),
    help="Optional custom working directory (default: tmpdir, auto-cleaned).",
)
def bundle(
    rootfs: str,
    config: Path,
    name: str,
    target: str,
    output: Path,
    bsp: str | None,
    workdir: Path | None,
) -> None:
    """Create a flashable makeself bundle for deployment."""
    console.print(f"[bold blue]Builder[/] - Bundling {name}")
    console.print(f"  Rootfs: {rootfs}")
    console.print(f"  Config: {config}")
    console.print(f"  Target: {target}")
    console.print(f"  Output: {output}")

    if target == "jetson" and not bsp:
        raise click.UsageError("--bsp is required for Jetson target")

    # Load and validate configuration
    raw_config = load_config(config)
    builder_config = BuilderConfig.model_validate(raw_config)

    console.print(f"  Components: {len(builder_config.components)}")

    # TODO: Implement bundle logic
    console.print("[yellow]Bundle command not yet implemented[/]")


if __name__ == "__main__":
    main()
