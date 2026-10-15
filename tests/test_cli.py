import re

from typer.testing import CliRunner

from secrets_generator.cli import app

runner = CliRunner()


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
