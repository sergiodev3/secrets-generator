import io
import re

import pytest
from rich.console import Console

from secrets_generator import interactive, ui
from secrets_generator.core import PRESETS, SecretFormat
from secrets_generator.interactive import Action


class FakePrompt:
    def __init__(self, answer):
        self._answer = answer

    def unsafe_ask(self):
        if isinstance(self._answer, BaseException):
            raise self._answer
        return self._answer

    ask = unsafe_ask


@pytest.fixture
def console():
    return Console(file=io.StringIO(), width=100, color_system=None)


@pytest.fixture
def script(monkeypatch):
    """Feed scripted answers to every questionary prompt, in order."""
    answers = []

    def fake_prompt(*args, **kwargs):
        return FakePrompt(answers.pop(0))

    monkeypatch.setattr(interactive.questionary, "select", fake_prompt)
    monkeypatch.setattr(interactive.questionary, "text", fake_prompt)
    return answers


def output_lines(console):
    return console.file.getvalue().splitlines()


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("JWT_SECRET", ["JWT_SECRET"]),
        ("JWT_SECRET, SESSION_SECRET", ["JWT_SECRET", "SESSION_SECRET"]),
        ("A B,C ,, D", ["A", "B", "C", "D"]),
        ("A, A", ["A"]),
        ("", []),
        ("  , ,", []),
    ],
)
def test_parse_env_names(raw, expected):
    assert interactive.parse_env_names(raw) == expected


def test_validator_accepts_valid_names():
    assert interactive.validate_env_names("JWT_SECRET, API_KEY") is True


@pytest.mark.parametrize(("raw", "bad"), [("MY-KEY", "MY-KEY"), ("OK 1BAD", "1BAD")])
def test_validator_rejects_invalid_names(raw, bad):
    message = interactive.validate_env_names(raw)
    assert isinstance(message, str)
    assert bad in message


def test_validator_rejects_empty_input():
    assert isinstance(interactive.validate_env_names("  "), str)


def test_logo_is_plain_ascii_and_fits_72_columns():
    assert ui.LOGO.isascii()
    assert max(len(line) for line in ui.LOGO.splitlines()) <= 72


def test_banner_shows_name_version_and_tagline(console):
    ui.render_banner(console, version="9.9.9")
    text = console.file.getvalue()
    assert "Secrets Generator" in text
    assert "9.9.9" in text
    assert "Cryptographically secure secrets for production apps" in text


def test_banner_shows_author(console):
    ui.render_banner(console, version="9.9.9")
    assert "by sergiodev3" in console.file.getvalue()


def test_secret_lines_are_never_wrapped():
    narrow = Console(file=io.StringIO(), width=40, color_system=None)
    line = "JWT_SECRET=" + "[ab]" * 30
    ui.print_secrets(narrow, [line])
    assert line in output_lines(narrow)


def test_env_flow_prints_key_value_lines_and_exit_ends_loop(script, console):
    script.extend([Action.ENV, "JWT_SECRET, SESSION_SECRET", 64, SecretFormat.HEX, Action.EXIT])
    interactive.run(console=console)
    lines = output_lines(console)
    assert any(re.fullmatch(r"JWT_SECRET=[0-9a-f]{128}", line) for line in lines)
    assert any(re.fullmatch(r"SESSION_SECRET=[0-9a-f]{128}", line) for line in lines)
    assert "Secrets Generator" in console.file.getvalue()
    assert script == []


def test_raw_flow_prints_one_secret(script, console):
    script.extend([Action.RAW, 32, SecretFormat.BASE64URL, Action.EXIT])
    interactive.run(console=console)
    assert any(re.fullmatch(r"[A-Za-z0-9_-]{43}", line) for line in output_lines(console))


def test_preset_flow_uses_preset_settings(script, console):
    api_key = next(preset for preset in PRESETS if preset.name == "API_KEY")
    script.extend([Action.PRESETS, api_key, Action.EXIT])
    interactive.run(console=console)
    assert any(re.fullmatch(r"API_KEY=[A-Za-z0-9]{43}", line) for line in output_lines(console))


def test_preset_back_returns_to_menu(script, console):
    script.extend([Action.PRESETS, interactive.BACK, Action.HELP, Action.EXIT])
    interactive.run(console=console)
    assert "secrets-gen JWT_SECRET -b 64 -f hex" in console.file.getvalue()
    assert script == []


@pytest.mark.parametrize(
    "answers",
    [
        [None],
        [KeyboardInterrupt()],
        [Action.ENV, None],
        [Action.RAW, 32, KeyboardInterrupt()],
    ],
)
def test_cancel_exits_cleanly_with_goodbye(script, console, answers):
    script.extend(answers)
    interactive.run(console=console)
    assert script == []
    assert "Goodbye" in console.file.getvalue()
