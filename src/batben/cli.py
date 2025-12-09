# src/batben/cli.py

import sys
import click

from . import __version__
# from . import battery, workload, sleep as sleep_mod


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "-V", "--version", prog_name="batben")
def cli():
    """Battery benchmarking and sleep/wake helper."""
    # Top-level command group; subcommands below.
    pass


@cli.command("bench", help="Run a simple workload benchmark and report battery impact.")
@click.option(
    "-t",
    "--time",
    "duration",
    type=int,
    default=30,
    show_default=True,
    help="Run benchmark for N seconds.",
)
@click.option(
    "-w",
    "--workload",
    type=click.Choice(["quick", "cpu", "io", "memory", "dev"], case_sensitive=False),
    default="quick",
    show_default=True,
    help="Which workload pattern to run.",
)
def bench_cmd(duration: int, workload: str) -> None:
    """Entry point for the benchmark command."""


@cli.command("sleep-check", help="Measure battery during suspend/resume cycles.")
@click.option(
    "-t",
    "--time",
    "duration",
    type=int,
    default=60,
    show_default=True,
    help="How long to stay in each state (seconds).",
)
@click.option(
    "--no-sleep",
    is_flag=True,
    default=False,
    help="Skip the suspend portion (debugging/testing).",
)
@click.option(
    "--no-wake",
    is_flag=True,
    default=False,
    help="Skip the post-resume measurement (debugging/testing).",
)
def sleep_check_cmd(duration: int, no_sleep: bool, no_wake: bool) -> None:
    """Entry point for sleep/wake testing."""
    # TODO: hook into `sleep_mod.quick_sleep`, `battery.sleep_check`, `battery.wake_check`.
    click.echo(f"[stub] sleep-check: duration={duration}s, no_sleep={no_sleep}, no_wake={no_wake}")
    sys.exit(0)


def main() -> None:
    """Console script entry point."""
    cli(prog_name="batben")


if __name__ == "__main__":
    main()
