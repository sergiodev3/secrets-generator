from typing import Annotated

import typer

from secrets_generator.core import (
    DEFAULT_BYTES,
    MIN_BYTES,
    SecretFormat,
    generate_secret,
    is_valid_env_name,
)

app = typer.Typer(
    add_completion=False,
    help="Generate cryptographically secure secrets for production apps.",
)


def _validate_names(names: list[str] | None) -> list[str] | None:
    for name in names or []:
        if not is_valid_env_name(name):
            raise typer.BadParameter(f"'{name}' is not a valid environment variable name")
    return names


@app.command()
def generate(
    names: Annotated[
        list[str] | None,
        typer.Argument(
            help="Variable names. Prints KEY=value lines; without names prints a raw secret.",
            callback=_validate_names,
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
) -> None:
    """Generate one secret per NAME (or a single raw secret)."""
    if not names:
        typer.echo(generate_secret(num_bytes, fmt))
        return

    for name in names:
        typer.echo(f"{name}={generate_secret(num_bytes, fmt)}")
