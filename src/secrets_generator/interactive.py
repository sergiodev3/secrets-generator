"""Arrow-key interactive menu. Orchestrates prompts; generation lives in ``core``."""

import re
from collections.abc import Callable
from enum import StrEnum

import questionary
from questionary import Choice, Style
from rich.console import Console

from secrets_generator import ui
from secrets_generator.core import (
    PRESETS,
    Preset,
    SecretFormat,
    generate_secret,
    is_valid_env_name,
    package_version,
)


class Action(StrEnum):
    ENV = "env"
    RAW = "raw"
    PRESETS = "presets"
    HELP = "help"
    EXIT = "exit"


BACK = "back"

STYLE = Style(
    [
        ("qmark", "fg:#00afd7 bold"),
        ("question", "bold"),
        ("pointer", "fg:#00afd7 bold"),
        ("highlighted", "fg:#00afd7 bold"),
        ("selected", "fg:#5fd700"),
        ("answer", "fg:#5fd700 bold"),
        ("instruction", "fg:#808080 italic"),
    ]
)
POINTER = "»"

MENU_CHOICES = [
    Choice("Generate .env variables", Action.ENV),
    Choice("Generate a raw secret", Action.RAW),
    Choice("Presets", Action.PRESETS),
    Choice("Help", Action.HELP),
    Choice("Exit", Action.EXIT),
]

BYTES_CHOICES = [
    Choice("16 bytes — 128 bits (minimum)", 16),
    Choice("32 bytes — 256 bits (recommended, JWT HS256)", 32),
    Choice("64 bytes — 512 bits (JWT HS512)", 64),
]
_DEFAULT_BYTES_CHOICE = BYTES_CHOICES[1]

FORMAT_CHOICES = [
    Choice("base64url", SecretFormat.BASE64URL, description="URL-safe, no padding (default)"),
    Choice("base64", SecretFormat.BASE64, description="Standard base64 with + / and = padding"),
    Choice("hex", SecretFormat.HEX, description="0-9a-f, two characters per byte"),
    Choice("alnum", SecretFormat.ALNUM, description="Letters and digits only"),
]

_NAME_SEPARATORS = re.compile(r"[,\s]+")


class _Cancelled(Exception):
    """The user dismissed a prompt."""


def parse_env_names(raw: str) -> list[str]:
    """Split comma and/or whitespace separated names, dropping empties and duplicates."""
    names = (piece for piece in _NAME_SEPARATORS.split(raw) if piece)
    return list(dict.fromkeys(names))


def validate_env_names(raw: str) -> bool | str:
    """questionary validator: ``True`` when valid, otherwise an error message."""
    names = parse_env_names(raw)
    if not names:
        return "Enter at least one variable name, e.g. JWT_SECRET"
    invalid = [name for name in names if not is_valid_env_name(name)]
    if invalid:
        return (
            f"Invalid name(s): {', '.join(invalid)}. "
            "Use letters, digits and _, not starting with a digit."
        )
    return True


def _ask(question: questionary.Question):
    answer = question.unsafe_ask()
    if answer is None:
        raise _Cancelled
    return answer


def _select(message: str, choices: list[Choice], default: Choice | None = None):
    return _ask(
        questionary.select(
            message,
            choices=choices,
            default=default,
            style=STYLE,
            pointer=POINTER,
            instruction="(arrow keys, Enter to select)",
        )
    )


def _ask_bytes_and_format() -> tuple[int, SecretFormat]:
    num_bytes = _select("Entropy:", BYTES_CHOICES, default=_DEFAULT_BYTES_CHOICE)
    fmt = _select("Format:", FORMAT_CHOICES)
    return num_bytes, fmt


def _describe(num_bytes: int, fmt: SecretFormat) -> str:
    return f"{num_bytes} bytes ({num_bytes * 8} bits), {fmt}"


def _env_flow(console: Console) -> None:
    raw = _ask(
        questionary.text(
            "Variable names:",
            validate=validate_env_names,
            style=STYLE,
            instruction="(comma or space separated, e.g. JWT_SECRET SESSION_SECRET)",
        )
    )
    names = parse_env_names(raw)
    num_bytes, fmt = _ask_bytes_and_format()
    lines = [f"{name}={generate_secret(num_bytes, fmt)}" for name in names]
    ui.print_secrets(console, lines, title=f"# {_describe(num_bytes, fmt)}")


def _raw_flow(console: Console) -> None:
    num_bytes, fmt = _ask_bytes_and_format()
    ui.print_secrets(console, [generate_secret(num_bytes, fmt)], title=f"# {_describe(num_bytes, fmt)}")


def _presets_flow(console: Console) -> None:
    choices = [Choice(preset.label, preset, description=f"{preset.name}, {preset.description}") for preset in PRESETS]
    choices.append(Choice("Back", BACK))
    preset = _select("Preset:", choices)
    if not isinstance(preset, Preset):  # "Back"
        return
    line = f"{preset.name}={generate_secret(preset.num_bytes, preset.fmt)}"
    ui.print_secrets(console, [line], title=f"# {preset.label}: {_describe(preset.num_bytes, preset.fmt)}")


def _help_flow(console: Console) -> None:
    ui.print_help(console)


_HANDLERS: dict[Action, Callable[[Console], None]] = {
    Action.ENV: _env_flow,
    Action.RAW: _raw_flow,
    Action.PRESETS: _presets_flow,
    Action.HELP: _help_flow,
}


def run(console: Console | None = None) -> None:
    """Show the banner and loop over the main menu until Exit or Ctrl+C."""
    console = console or Console()
    ui.render_banner(console, version=package_version())
    try:
        while (action := _select("What do you want to do?", MENU_CHOICES)) != Action.EXIT:
            _HANDLERS[action](console)
    except (_Cancelled, KeyboardInterrupt, EOFError):
        console.print()
    ui.print_goodbye(console)
