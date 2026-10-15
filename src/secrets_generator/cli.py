from typing import Annotated

import typer

from secrets_generator.core import (
    DEFAULT_BYTES,
    MIN_BYTES,
    SecretFormat,
    generate_secret,
    is_valid_env_name,
    package_version,
)

_EPILOG = """\
[bold]Examples[/bold]

  [cyan]secrets-gen JWT_SECRET[/cyan]                    one KEY=value line (256 bits)

  [cyan]secrets-gen JWT_SECRET SESSION_SECRET[/cyan]     several KEY=value lines

  [cyan]secrets-gen JWT_SECRET -b 64 -f hex[/cyan]       64 bytes (HS512) encoded as hex

  [cyan]secrets-gen JWT_SECRET >> .env[/cyan]            append to a .env file

  [cyan]secrets-gen -f alnum[/cyan]                      raw secret, letters and digits only
"""

app = typer.Typer(
    add_completion=False,
    help="Generate cryptographically secure secrets for production apps.",
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_markup_mode="rich",
)


def _validate_names(names: list[str] | None) -> list[str] | None:
    for name in names or []:
        if not is_valid_env_name(name):
            raise typer.BadParameter(f"'{name}' is not a valid environment variable name")
    return names


def _print_version(value: bool) -> None:
    if value:
        typer.echo(f"secrets-gen {package_version()}")
        raise typer.Exit()


@app.command(epilog=_EPILOG)
def generate(
    names: Annotated[
        list[str] | None,
        typer.Argument(
            help="Variable names. Prints KEY=value lines; without names prints a raw secret.",
            callback=_validate_names,
            show_default=False,
        ),
    ] = None,
    num_bytes: Annotated[
        int,
        typer.Option("--bytes", "-b", min=MIN_BYTES, help="Entropy in bytes (32 = 256 bits)."),
    ] = DEFAULT_BYTES,
    fmt: Annotated[
        SecretFormat,
        typer.Option("--format", "-f", help="Output encoding."),
    ] = SecretFormat.BASE64URL,
    _version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=_print_version,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = False,
) -> None:
    """Generate one secret per [bold]NAME[/bold] (or a single raw secret).

    Secrets come from the OS CSPRNG ([italic]secrets[/italic] module), never [italic]random[/italic].
    """
    if not names:
        typer.echo(generate_secret(num_bytes, fmt))
        return

    for name in names:
        typer.echo(f"{name}={generate_secret(num_bytes, fmt)}")
