"""Rich presentation helpers: banner, help and secret output."""

from collections.abc import Iterable

from rich.console import Console
from rich.text import Text

APP_NAME = "Secrets Generator"
TAGLINE = "Cryptographically secure secrets for production apps"

# Plain ASCII only (legacy Windows consoles) and at most 72 columns wide.
LOGO = r"""
                        _
 ___  ___  ___ _ __ ___| |_ ___        __ _  ___ _ __
/ __|/ _ \/ __| '__/ _ \ __/ __|_____ / _` |/ _ \ '_ \
\__ \  __/ (__| | |  __/ |_\__ \_____| (_| |  __/ | | |
|___/\___|\___|_|  \___|\__|___/      \__, |\___|_| |_|
                                      |___/
""".strip("\n")

_LOGO_STYLES = ("bright_cyan", "bright_cyan", "cyan", "cyan", "blue", "blue")

HELP_EXAMPLES: tuple[tuple[str, str], ...] = (
    ("secrets-gen", "interactive menu (this screen)"),
    ("secrets-gen JWT_SECRET", "one KEY=value line, 256 bits, base64url"),
    ("secrets-gen JWT_SECRET SESSION_SECRET", "several KEY=value lines"),
    ("secrets-gen JWT_SECRET -b 64 -f hex", "64 bytes (HS512) encoded as hex"),
    ("secrets-gen JWT_SECRET >> .env", "append to a .env file"),
    ("secrets-gen -f alnum", "raw secret, letters and digits only"),
    ("secrets-gen -h", "full help with every option"),
    ("secrets-gen --version", "print the version"),
)


def render_banner(console: Console, version: str) -> None:
    """Print the ASCII logo followed by the app name, version and tagline."""
    console.print()
    for index, line in enumerate(LOGO.splitlines()):
        style = _LOGO_STYLES[min(index, len(_LOGO_STYLES) - 1)]
        console.print(Text(line, style=f"bold {style}"), no_wrap=True, overflow="crop")
    console.print()
    title = Text(APP_NAME, style="bold")
    title.append(f"  v{version}", style="dim")
    console.print(title)
    console.print(Text(TAGLINE, style="italic cyan"))
    console.print()


def print_secrets(console: Console, lines: Iterable[str], title: str | None = None) -> None:
    """Print secret lines verbatim: no wrapping, no markup, no highlighting."""
    console.print()
    if title:
        console.print(Text(title, style="dim"))
    for line in lines:
        console.print(line, soft_wrap=True, markup=False, highlight=False)
    console.print()


def print_help(console: Console) -> None:
    """Print non-interactive usage examples."""
    console.print()
    console.print(Text("Non-interactive usage", style="bold"))
    width = max(len(command) for command, _ in HELP_EXAMPLES)
    for command, description in HELP_EXAMPLES:
        row = Text("  ")
        row.append(command.ljust(width), style="cyan")
        row.append(f"   {description}", style="dim")
        console.print(row, soft_wrap=True)
    console.print()


def print_goodbye(console: Console) -> None:
    console.print(Text("Goodbye.", style="dim"))
