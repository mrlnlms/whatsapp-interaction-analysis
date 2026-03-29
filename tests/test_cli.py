"""Testes para o CLI whatsapp-interaction."""

import pytest
import sys
from pathlib import Path
from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cli import app
from cli.helpers import validate_steps


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


class TestCLIHelp:
    """Testa que todos os comandos respondem --help sem crash."""

    def test_main_help(self):
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "prepare" in result.output
        assert "process" in result.output
        assert "status" in result.output
        assert "run" in result.output

    def test_prepare_help(self):
        runner = CliRunner()
        result = runner.invoke(app, ["prepare", "--help"])
        assert result.exit_code == 0
        assert "clean" in result.output
        assert "wrangle" in result.output
        assert "transcribe" in result.output

    def test_process_help(self):
        runner = CliRunner()
        result = runner.invoke(app, ["process", "--help"])
        assert result.exit_code == 0
        assert "sentiment" in result.output
        assert "embeddings" in result.output

    def test_clean_help(self):
        runner = CliRunner()
        result = runner.invoke(app, ["prepare", "clean", "--help"])
        assert result.exit_code == 0
        assert "--steps" in result.output

    def test_sentiment_help(self):
        runner = CliRunner()
        result = runner.invoke(app, ["process", "sentiment", "--help"])
        assert result.exit_code == 0
        assert "--model" in result.output

    def test_embeddings_help(self):
        runner = CliRunner()
        result = runner.invoke(app, ["process", "embeddings", "--help"])
        assert result.exit_code == 0
        assert "--model" in result.output

    def test_run_help(self):
        runner = CliRunner()
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "--skip-transcribe" in result.output
        assert "--skip-process" in result.output

    def test_status_without_env(self):
        runner = CliRunner()
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "Status do Pipeline" in result.output
