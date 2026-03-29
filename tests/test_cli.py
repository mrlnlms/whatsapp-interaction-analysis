"""Testes para o CLI whatsapp-interaction."""

import re
import pytest
from typer.testing import CliRunner

from whatsapp.cli import app
from whatsapp.cli.helpers import validate_steps


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes do output."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


class TestValidateSteps:
    def test_returns_all_when_empty(self):
        valid = ["a", "b", "c"]
        assert validate_steps("", valid) == valid

    def test_returns_requested_steps(self):
        valid = ["a", "b", "c"]
        assert validate_steps("a,c", valid) == ["a", "c"]

    def test_exits_on_invalid_step(self):
        from click.exceptions import Exit
        valid = ["a", "b", "c"]
        with pytest.raises(Exit):
            validate_steps("a,x", valid)

    def test_handles_spaces(self):
        valid = ["a", "b", "c"]
        assert validate_steps("a, b, c", valid) == ["a", "b", "c"]


runner = CliRunner()


class TestCLIHelp:
    """Testa que todos os comandos respondem --help sem crash."""

    def _run(self, args):
        result = runner.invoke(app, args)
        return result.exit_code, strip_ansi(result.output)

    def test_main_help(self):
        code, output = self._run(["--help"])
        assert code == 0
        assert "prepare" in output
        assert "process" in output
        assert "status" in output
        assert "run" in output

    def test_prepare_help(self):
        code, output = self._run(["prepare", "--help"])
        assert code == 0
        assert "clean" in output
        assert "wrangle" in output
        assert "transcribe" in output

    def test_process_help(self):
        code, output = self._run(["process", "--help"])
        assert code == 0
        assert "sentiment" in output
        assert "embeddings" in output

    def test_clean_help(self):
        code, output = self._run(["prepare", "clean", "--help"])
        assert code == 0
        assert "--steps" in output

    def test_sentiment_help(self):
        code, output = self._run(["process", "sentiment", "--help"])
        assert code == 0
        assert "--model" in output

    def test_embeddings_help(self):
        code, output = self._run(["process", "embeddings", "--help"])
        assert code == 0
        assert "--model" in output

    def test_run_help(self):
        code, output = self._run(["run", "--help"])
        assert code == 0
        assert "--skip-transcribe" in output
        assert "--skip-process" in output

    def test_status_without_env(self):
        code, output = self._run(["status"])
        assert code == 0
        assert "Status do Pipeline" in output
