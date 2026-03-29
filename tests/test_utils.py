"""Testes para whatsapp.pipeline.utils (audit, file_helpers, dataframe_helpers, text_helpers)."""

import pandas as pd
import pytest

from whatsapp.pipeline.utils.file_helpers import (
    format_bytes,
    get_file_overview,
    get_file_density_stats,
)
from whatsapp.pipeline.utils.audit import (
    audit_transformation,
    format_audit_table,
    get_file_stats,
    audit_pipeline,
)
from whatsapp.pipeline.utils.dataframe_helpers import (
    multi_position_preview_dataframe,
    format_file_overview_table,
    format_density_stats_table,
)
from whatsapp.pipeline.utils.text_helpers import format_markdown_lists


# ---------------------------------------------------------------------------
# file_helpers.py
# ---------------------------------------------------------------------------

class TestFormatBytes:
    def test_zero(self):
        assert format_bytes(0) == "0.00 B"

    def test_bytes(self):
        assert format_bytes(512) == "512.00 B"

    def test_kilobytes(self):
        assert format_bytes(1024) == "1.00 KB"

    def test_megabytes(self):
        assert format_bytes(1024 ** 2) == "1.00 MB"

    def test_gigabytes(self):
        assert format_bytes(1024 ** 3) == "1.00 GB"

    def test_terabytes(self):
        assert format_bytes(1024 ** 4) == "1.00 TB"

    def test_negative(self):
        result = format_bytes(-2048)
        assert result.startswith("-")
        assert "2.00 KB" in result

    def test_fractional_kb(self):
        result = format_bytes(1536)
        assert "KB" in result


class TestGetFileOverview:
    def test_returns_expected_keys(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("linha1\nlinha2\n\nlinha4\n", encoding="utf-8")
        result = get_file_overview(str(f))
        expected_keys = {
            "arquivo", "tamanho_bytes", "tamanho_formatted",
            "total_linhas", "linhas_nao_vazias", "linhas_vazias",
            "total_caracteres", "media_chars_por_linha",
        }
        assert expected_keys == set(result.keys())

    def test_counts(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("abc\n\nxyz\n", encoding="utf-8")
        result = get_file_overview(str(f))
        assert result["total_linhas"] == 3
        assert result["linhas_nao_vazias"] == 2
        assert result["linhas_vazias"] == 1

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("", encoding="utf-8")
        result = get_file_overview(str(f))
        assert result["total_linhas"] == 0
        assert result["total_caracteres"] == 0


class TestGetFileDensityStats:
    def test_returns_expected_keys(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("short\na longer line here\nmed\n", encoding="utf-8")
        result = get_file_density_stats(str(f))
        expected_keys = {
            "total_caracteres", "media_chars_linha", "mediana_chars_linha",
            "moda_chars_linha", "linha_mais_curta", "linha_mais_longa",
            "media_bytes_linha", "mediana_bytes_linha", "moda_bytes_linha",
        }
        assert expected_keys == set(result.keys())

    def test_single_line(self, tmp_path):
        f = tmp_path / "one.txt"
        f.write_text("hello\n", encoding="utf-8")
        result = get_file_density_stats(str(f))
        assert result["linha_mais_curta"] == result["linha_mais_longa"]


# ---------------------------------------------------------------------------
# audit.py
# ---------------------------------------------------------------------------

class TestGetFileStats:
    def test_returns_expected_keys(self, tmp_path):
        f = tmp_path / "a.txt"
        f.write_text("abc\ndef\n", encoding="utf-8")
        result = get_file_stats(str(f))
        assert "size_bytes" in result
        assert "total_lines" in result
        assert "total_chars" in result
        assert result["name"] == "a.txt"
        assert result["total_lines"] == 2

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("", encoding="utf-8")
        result = get_file_stats(str(f))
        assert result["total_lines"] == 0
        assert result["size_bytes"] == 0


class TestAuditTransformation:
    def test_returns_expected_keys(self, tmp_path):
        inp = tmp_path / "in.txt"
        out = tmp_path / "out.txt"
        inp.write_text("aaa\nbbb\nccc\n", encoding="utf-8")
        out.write_text("aaa\nbbb\n", encoding="utf-8")
        result = audit_transformation(str(inp), str(out), "test_step", show_output=False)
        assert result["transformation"] == "test_step"
        assert result["delta_lines"] == 1
        assert result["delta_bytes"] > 0
        assert "input" in result
        assert "output" in result

    def test_same_file_zero_delta(self, tmp_path):
        f = tmp_path / "same.txt"
        f.write_text("content\n", encoding="utf-8")
        result = audit_transformation(str(f), str(f), "noop", show_output=False)
        assert result["delta_lines"] == 0
        assert result["delta_bytes"] == 0
        assert result["lines_match"] is True


class TestFormatAuditTable:
    def test_returns_dataframe(self, tmp_path):
        # Cria dados minimos para audit_pipeline
        f1 = tmp_path / "s1.txt"
        f2 = tmp_path / "s2.txt"
        f1.write_text("aaa\nbbb\nccc\n", encoding="utf-8")
        f2.write_text("aaa\nbbb\n", encoding="utf-8")
        stages = [
            {"file": str(f1), "name": "Original"},
            {"file": str(f2), "name": "Cleaned"},
        ]
        df_audit, _ = audit_pipeline(stages, show_output=False)
        result = format_audit_table(df_audit)
        assert isinstance(result, pd.DataFrame)
        assert "Estágio" in result.columns

    def test_without_chars(self, tmp_path):
        f = tmp_path / "f.txt"
        f.write_text("x\n", encoding="utf-8")
        stages = [{"file": str(f), "name": "A"}, {"file": str(f), "name": "B"}]
        df_audit, _ = audit_pipeline(stages, show_output=False)
        result = format_audit_table(df_audit, include_chars=False)
        assert "Chars" not in result.columns


class TestAuditPipeline:
    def test_returns_tuple(self, tmp_path):
        f1 = tmp_path / "raw.txt"
        f2 = tmp_path / "clean.txt"
        f1.write_text("aaaa\nbbbb\ncccc\n", encoding="utf-8")
        f2.write_text("aaaa\nbbbb\n", encoding="utf-8")
        stages = [
            {"file": str(f1), "name": "Raw"},
            {"file": str(f2), "name": "Clean"},
        ]
        df, totals = audit_pipeline(stages, show_output=False)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert totals["total_lines"] == 1
        assert totals["total_bytes"] > 0

    def test_single_stage(self, tmp_path):
        f = tmp_path / "only.txt"
        f.write_text("x\n", encoding="utf-8")
        df, totals = audit_pipeline([{"file": str(f), "name": "Only"}], show_output=False)
        assert len(df) == 1
        assert totals["total_lines"] == 0
        assert totals["total_bytes"] == 0


# ---------------------------------------------------------------------------
# dataframe_helpers.py
# ---------------------------------------------------------------------------

class TestMultiPositionPreviewDataframe:
    def test_returns_dataframe(self, tmp_path):
        f = tmp_path / "lines.txt"
        f.write_text("\n".join(f"line {i}" for i in range(100)) + "\n", encoding="utf-8")
        df = multi_position_preview_dataframe(str(f), n_lines=3, positions=[0, 50, 100])
        assert isinstance(df, pd.DataFrame)
        assert "Conteúdo" in df.columns

    def test_separator_rows(self, tmp_path):
        f = tmp_path / "lines.txt"
        f.write_text("\n".join(f"line {i}" for i in range(50)) + "\n", encoding="utf-8")
        df = multi_position_preview_dataframe(str(f), n_lines=2, positions=[0, 100], insert_separator=True)
        # 2 positions x 2 lines + 1 separator = 5 rows
        assert len(df) == 5

    def test_no_separator(self, tmp_path):
        f = tmp_path / "lines.txt"
        f.write_text("\n".join(f"line {i}" for i in range(50)) + "\n", encoding="utf-8")
        df = multi_position_preview_dataframe(str(f), n_lines=2, positions=[0, 100], insert_separator=False)
        assert len(df) == 4


class TestFormatFileOverviewTable:
    def test_returns_dataframe_with_metrics(self):
        overview = {
            "arquivo": "test.txt",
            "tamanho_bytes": 1024,
            "tamanho_formatted": "1.00 KB",
            "total_linhas": 10,
            "linhas_nao_vazias": 8,
            "linhas_vazias": 2,
            "total_caracteres": 500,
            "media_chars_por_linha": 50.0,
        }
        df = format_file_overview_table(overview)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 7


class TestFormatDensityStatsTable:
    def test_returns_dataframe_with_metrics(self):
        stats = {
            "total_caracteres": 1000,
            "media_chars_linha": 50.0,
            "mediana_chars_linha": 45.0,
            "moda_chars_linha": 40,
            "linha_mais_curta": 5,
            "linha_mais_longa": 120,
            "media_bytes_linha": 55.0,
            "mediana_bytes_linha": 48.0,
            "moda_bytes_linha": 42,
        }
        df = format_density_stats_table(stats)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 9


# ---------------------------------------------------------------------------
# text_helpers.py
# ---------------------------------------------------------------------------

class TestFormatMarkdownLists:
    def test_empty_string(self):
        assert format_markdown_lists("") == ""

    def test_none_passthrough(self):
        assert format_markdown_lists(None) is None

    def test_category_with_subitems(self):
        text = "- Texto: puro, com emoji, com link"
        result = format_markdown_lists(text)
        assert "- Texto:" in result
        assert "- puro" in result
        assert "- com emoji" in result

    def test_bullet_comma_list(self):
        text = "- file1.txt, file2.txt, file3.txt"
        result = format_markdown_lists(text)
        assert "file1.txt" in result
        assert "file2.txt" in result
        lines = result.split("\n")
        assert len(lines) == 3

    def test_html_output(self):
        text = "- item1, item2"
        result = format_markdown_lists(text, output_format="html")
        assert "<li>" in result
        assert "<ul>" in result

    def test_no_expansion_with_backticks(self):
        text = "- `code, with, commas`"
        result = format_markdown_lists(text)
        # Should NOT expand — backticks protect from splitting
        assert result.count("\n") == 0

    def test_plain_text_unchanged(self):
        text = "just a normal line"
        assert format_markdown_lists(text) == text
