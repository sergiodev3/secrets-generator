import re

import pytest
from typer.testing import CliRunner

from secrets_generator import cli, interactive
from secrets_generator.cli import app

runner = CliRunner()


@pytest.fixture
def interactive_calls(monkeypatch):
    calls = []
    monkeypatch.setattr(interactive, "run", lambda: calls.append("run"))
    return calls


def test_without_names_prints_raw_secret():
    result = runner.invoke(app, ["--format", "hex"])
    assert result.exit_code == 0
    assert re.fullmatch(r"[0-9a-f]{64}\n", result.stdout)


def test_with_names_prints_env_lines():
    result = runner.invoke(app, ["JWT_SECRET", "SESSION_SECRET"])
    assert result.exit_code == 0
    lines = result.stdout.splitlines()
    assert [line.split("=", 1)[0] for line in lines] == ["JWT_SECRET", "SESSION_SECRET"]
    assert lines[0].split("=", 1)[1] != lines[1].split("=", 1)[1]


def test_bytes_option_changes_length():
    result = runner.invoke(app, ["--bytes", "64", "--format", "hex"])
    assert result.exit_code == 0
    assert len(result.stdout.strip()) == 128


def test_rejects_invalid_env_name():
    result = runner.invoke(app, ["MY-KEY"])
    assert result.exit_code != 0


def test_rejects_too_few_bytes():
    result = runner.invoke(app, ["--bytes", "8"])
    assert result.exit_code != 0


def test_short_h_flag_shows_help():
    result = runner.invoke(app, ["-h"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout
    assert "--bytes" in result.stdout


def test_long_help_flag_shows_examples():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "secrets-gen JWT_SECRET" in result.stdout


def test_version_flag_prints_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert re.fullmatch(r"secrets-gen \d+\.\d+\.\d+\S*\n", result.stdout)


def test_short_version_flag_prints_version():
    result = runner.invoke(app, ["-V"])
    assert result.exit_code == 0
    assert result.stdout.startswith("secrets-gen ")


def test_no_args_in_terminal_launches_interactive_mode(monkeypatch, interactive_calls):
    monkeypatch.setattr(cli, "_is_interactive_terminal", lambda: True)
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert interactive_calls == ["run"]
    assert result.stdout == ""


def test_no_args_outside_terminal_prints_raw_secret(monkeypatch, interactive_calls):
    monkeypatch.setattr(cli, "_is_interactive_terminal", lambda: False)
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert interactive_calls == []
    assert re.fullmatch(r"[A-Za-z0-9_-]{43}\n", result.stdout)


@pytest.mark.parametrize("args", [["JWT_SECRET"], ["--bytes", "64"], ["-f", "hex"]])
def test_explicit_arguments_skip_interactive_mode(monkeypatch, interactive_calls, args):
    monkeypatch.setattr(cli, "_is_interactive_terminal", lambda: True)
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    assert interactive_calls == []
    assert result.stdout.strip() != ""
