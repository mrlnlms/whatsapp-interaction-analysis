"""Testes para src/cleaning.py — pipeline de limpeza de dados WhatsApp."""

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cleaning import (
    remove_u200e,
    remove_empty_lines,
    normalize_whitespace,
    anonymize_participants,
    optimize_timestamps,
    normalize_indentation,
    remove_empty_timestamps,
    CLEANING_STEPS,
    get_available_steps,
)


# =============================================================================
# remove_u200e
# =============================================================================

class TestRemoveU200e:
    def test_removes_invisible_chars(self, tmp_file):
        inp, out = tmp_file("Hello\u200eWorld\u200e\n")
        result = remove_u200e(inp, out)
        assert out.read_text() == "HelloWorld\n"
        assert result["caracteres_removidos"] == 2

    def test_no_u200e_passthrough(self, tmp_file):
        inp, out = tmp_file("Texto normal sem caracteres invisiveis\n")
        result = remove_u200e(inp, out)
        assert out.read_text() == "Texto normal sem caracteres invisiveis\n"
        assert result["caracteres_removidos"] == 0

    def test_multiple_lines(self, tmp_file):
        content = "\u200eLinha 1\u200e\n\u200eLinha 2\n"
        inp, out = tmp_file(content)
        result = remove_u200e(inp, out)
        assert out.read_text() == "Linha 1\nLinha 2\n"
        assert result["caracteres_removidos"] == 3


# =============================================================================
# remove_empty_lines
# =============================================================================

class TestRemoveEmptyLines:
    def test_removes_blank_lines(self, tmp_file):
        inp, out = tmp_file("Linha 1\n\n\nLinha 2\n")
        result = remove_empty_lines(inp, out)
        assert out.read_text() == "Linha 1\nLinha 2\n"
        assert result["linhas_removidas"] == 2

    def test_preserves_content_lines(self, tmp_file):
        inp, out = tmp_file("A\nB\nC\n")
        result = remove_empty_lines(inp, out)
        assert out.read_text() == "A\nB\nC\n"
        assert result["linhas_removidas"] == 0

    def test_preserves_lines_with_spaces(self, tmp_file):
        inp, out = tmp_file("A\n   \nB\n")
        result = remove_empty_lines(inp, out)
        # "   \n" nao e "\n", entao nao e removida
        assert result["linhas_removidas"] == 0


# =============================================================================
# normalize_whitespace
# =============================================================================

class TestNormalizeWhitespace:
    def test_collapses_multiple_spaces(self, tmp_file):
        inp, out = tmp_file("Muitos    espacos   aqui\n")
        normalize_whitespace(inp, out)
        assert out.read_text() == "Muitos espacos aqui\n"

    def test_tabs_to_spaces(self, tmp_file):
        inp, out = tmp_file("Tab\there\n")
        normalize_whitespace(inp, out)
        assert out.read_text() == "Tab here\n"

    def test_strips_trailing_whitespace(self, tmp_file):
        inp, out = tmp_file("Trailing spaces   \n")
        normalize_whitespace(inp, out)
        assert out.read_text() == "Trailing spaces\n"

    def test_returns_bytes_saved(self, tmp_file):
        inp, out = tmp_file("A     B\n")
        result = normalize_whitespace(inp, out)
        assert result["bytes_economizados"] > 0


# =============================================================================
# anonymize_participants
# =============================================================================

class TestAnonymizeParticipants:
    def test_replaces_names(self, tmp_file):
        content = "[28/11/24, 19:30:05] Marlon: Oi\n[28/11/24, 19:30:10] Lê 🖤: Oi!\n"
        inp, out = tmp_file(content)
        result = anonymize_participants(inp, out)
        text = out.read_text()
        assert "] P1:" in text
        assert "] P2:" in text
        assert "Marlon" not in text
        assert result["substituicoes"]["Marlon"] == 1
        assert result["substituicoes"]["Lê 🖤"] == 1

    def test_ignores_name_in_content(self, tmp_file):
        # "Marlon" no conteudo (sem "] Marlon:") nao deve ser substituido
        content = "[28/11/24, 19:30:05] P1: Falei com Marlon ontem\n"
        inp, out = tmp_file(content)
        result = anonymize_participants(inp, out)
        assert "Falei com Marlon ontem" in out.read_text()
        assert result["substituicoes"]["Marlon"] == 0


# =============================================================================
# optimize_timestamps
# =============================================================================

class TestOptimizeTimestamps:
    def test_removes_brackets_and_comma(self, tmp_file):
        content = "[28/11/24, 19:30:05] P1: Mensagem\n"
        inp, out = tmp_file(content)
        result = optimize_timestamps(inp, out)
        assert out.read_text() == "28/11/24 19:30:05 P1: Mensagem\n"
        assert result["timestamps_otimizados"] == 1

    def test_preserves_continuation_lines(self, tmp_file):
        content = "[28/11/24, 19:30:05] P1: Linha 1\nContinuacao\n"
        inp, out = tmp_file(content)
        optimize_timestamps(inp, out)
        lines = out.read_text().splitlines()
        assert lines[0] == "28/11/24 19:30:05 P1: Linha 1"
        assert lines[1] == "Continuacao"

    def test_multiple_timestamps(self, tmp_file):
        content = (
            "[01/01/25, 00:00:00] P1: Feliz ano novo!\n"
            "[01/01/25, 00:00:01] P2: Igualmente!\n"
        )
        inp, out = tmp_file(content)
        result = optimize_timestamps(inp, out)
        assert result["timestamps_otimizados"] == 2


# =============================================================================
# normalize_indentation
# =============================================================================

class TestNormalizeIndentation:
    def test_strips_continuation_indent(self, tmp_file):
        content = "24/11/24 15:30:05 P1: Oi\n    Continuacao identada\n"
        inp, out = tmp_file(content)
        result = normalize_indentation(inp, out)
        lines = out.read_text().splitlines()
        assert lines[1] == "Continuacao identada"
        assert result["espacos_removidos"] == 4

    def test_preserves_timestamp_lines(self, tmp_file):
        content = "24/11/24 15:30:05 P1: Nao muda\n24/11/24 15:31:00 P2: Tambem nao\n"
        inp, out = tmp_file(content)
        result = normalize_indentation(inp, out)
        assert out.read_text() == content
        assert result["espacos_removidos"] == 0


# =============================================================================
# remove_empty_timestamps
# =============================================================================

class TestRemoveEmptyTimestamps:
    def test_removes_empty_timestamp_before_media_burst(self, tmp_file):
        content = (
            "24/11/24 15:30:00 P1:\n"
            "24/11/24 15:30:00 P1: image omitted\n"
            "24/11/24 15:30:00 P1: image omitted\n"
            "24/11/24 15:31:00 P2: Oi\n"
        )
        inp, out = tmp_file(content)
        result = remove_empty_timestamps(inp, out)
        assert result["linhas_removidas"] == 1
        assert "P1:\n" not in out.read_text()

    def test_preserves_normal_messages(self, tmp_file):
        content = (
            "24/11/24 15:30:00 P1: Oi\n"
            "24/11/24 15:31:00 P2: Tudo bem?\n"
        )
        inp, out = tmp_file(content)
        result = remove_empty_timestamps(inp, out)
        assert result["linhas_removidas"] == 0


# =============================================================================
# CLEANING_STEPS registry
# =============================================================================

class TestCleaningSteps:
    def test_all_steps_have_required_keys(self):
        for step_id, step in CLEANING_STEPS.items():
            assert "name" in step, f"{step_id} falta 'name'"
            assert "function" in step, f"{step_id} falta 'function'"
            assert "description" in step, f"{step_id} falta 'description'"
            assert callable(step["function"]), f"{step_id} function nao e callable"

    def test_get_available_steps(self):
        steps = get_available_steps()
        assert isinstance(steps, list)
        assert len(steps) == 7
        assert "u200e" in steps
        assert "anonymize" in steps

    def test_step_count(self):
        assert len(CLEANING_STEPS) == 7
