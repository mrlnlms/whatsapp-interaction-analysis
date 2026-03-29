"""Testes para whatsapp.pipeline.config — validacao de env vars, paths e constantes."""

import importlib
import os
import re
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


# ---- Happy path: config ja foi importado via conftest.py com env vars validas ----

from whatsapp.pipeline.config import (
    DATA_FOLDER,
    DIAS_SEMANA,
    MESES,
    NOME_PARA_ANONIMO,
    PARTICIPANTES,
    PATHS,
    PERIODOS_DIA,
    PROJECT_ROOT,
    RADAR_MAXIMOS,
    REGEX_PATTERNS,
    STATUS_MIDIA,
    THRESHOLDS,
    TIPOS_MIDIA,
    VIZ_CONFIG,
)


# =============================================================================
# PROJECT_ROOT e DATA_FOLDER
# =============================================================================


class TestProjectRoot:
    """Testes para validacao de PROJECT_ROOT."""

    def test_project_root_is_path(self):
        assert isinstance(PROJECT_ROOT, Path)

    def test_project_root_exists(self):
        assert PROJECT_ROOT.exists()

    def test_missing_project_root_raises(self, tmp_path):
        """Recarrega config sem PROJECT_ROOT e espera EnvironmentError."""
        env = os.environ.copy()
        env.pop("PROJECT_ROOT", None)
        with patch.dict(os.environ, env, clear=True):
            # Remove modulo do cache para forcar re-execucao
            mod_name = "whatsapp.pipeline.config"
            saved = sys.modules.pop(mod_name, None)
            try:
                with pytest.raises(EnvironmentError, match="PROJECT_ROOT nao definido"):
                    importlib.import_module(mod_name)
            finally:
                # Restaura modulo original
                sys.modules.pop(mod_name, None)
                if saved is not None:
                    sys.modules[mod_name] = saved

    def test_nonexistent_project_root_raises(self, tmp_path):
        """PROJECT_ROOT aponta para caminho inexistente."""
        fake_path = str(tmp_path / "nao_existe")
        env = os.environ.copy()
        env["PROJECT_ROOT"] = fake_path
        env["DATA_FOLDER"] = "sample"
        with patch.dict(os.environ, env, clear=True):
            mod_name = "whatsapp.pipeline.config"
            saved = sys.modules.pop(mod_name, None)
            try:
                with pytest.raises(EnvironmentError, match="PROJECT_ROOT nao encontrado"):
                    importlib.import_module(mod_name)
            finally:
                sys.modules.pop(mod_name, None)
                if saved is not None:
                    sys.modules[mod_name] = saved


class TestDataFolder:
    """Testes para validacao de DATA_FOLDER."""

    def test_data_folder_is_set(self):
        assert DATA_FOLDER is not None
        assert len(DATA_FOLDER) > 0

    def test_missing_data_folder_raises(self, tmp_path):
        """Recarrega config sem DATA_FOLDER e espera EnvironmentError."""
        env = os.environ.copy()
        env.pop("DATA_FOLDER", None)
        # PROJECT_ROOT precisa existir para passar a primeira validacao
        env["PROJECT_ROOT"] = str(tmp_path)
        with patch.dict(os.environ, env, clear=True):
            mod_name = "whatsapp.pipeline.config"
            saved = sys.modules.pop(mod_name, None)
            try:
                with pytest.raises(EnvironmentError, match="DATA_FOLDER nao definido"):
                    importlib.import_module(mod_name)
            finally:
                sys.modules.pop(mod_name, None)
                if saved is not None:
                    sys.modules[mod_name] = saved


# =============================================================================
# PATHS dict
# =============================================================================


class TestPaths:
    """Testes para o dicionario PATHS."""

    EXPECTED_KEYS = {"raw", "media", "interim", "processed", "integrated", "analysis"}

    def test_all_keys_present(self):
        assert set(PATHS.keys()) == self.EXPECTED_KEYS

    def test_values_are_path_objects(self):
        for key, val in PATHS.items():
            assert isinstance(val, Path), f"PATHS['{key}'] deveria ser Path, got {type(val)}"

    def test_paths_derived_from_project_root(self):
        for key, val in PATHS.items():
            assert str(val).startswith(str(PROJECT_ROOT)), (
                f"PATHS['{key}'] nao deriva de PROJECT_ROOT"
            )

    def test_raw_contains_data_folder(self):
        assert DATA_FOLDER in str(PATHS["raw"])

    def test_interim_contains_data_folder(self):
        assert DATA_FOLDER in str(PATHS["interim"])

    def test_processed_contains_data_folder(self):
        assert DATA_FOLDER in str(PATHS["processed"])


# =============================================================================
# Constantes
# =============================================================================


class TestParticipantes:
    """Testes para PARTICIPANTES e NOME_PARA_ANONIMO."""

    def test_has_p1_and_p2(self):
        assert "P1" in PARTICIPANTES
        assert "P2" in PARTICIPANTES

    def test_each_participant_has_required_fields(self):
        for pid, info in PARTICIPANTES.items():
            assert "nome" in info, f"{pid} sem campo 'nome'"
            assert "cor" in info, f"{pid} sem campo 'cor'"
            assert "cor_light" in info, f"{pid} sem campo 'cor_light'"

    def test_cores_are_hex(self):
        hex_re = re.compile(r"^#[0-9A-Fa-f]{6}$")
        for pid, info in PARTICIPANTES.items():
            assert hex_re.match(info["cor"]), f"{pid}.cor invalida: {info['cor']}"
            assert hex_re.match(info["cor_light"]), f"{pid}.cor_light invalida"

    def test_nome_para_anonimo_maps_to_participants(self):
        valid_ids = set(PARTICIPANTES.keys())
        for nome, pid in NOME_PARA_ANONIMO.items():
            assert pid in valid_ids, f"'{nome}' mapeia para '{pid}' que nao esta em PARTICIPANTES"


class TestThresholds:
    """Testes para THRESHOLDS."""

    def test_required_keys(self):
        expected = {"reply_quick_seconds", "conversation_gap_hours", "msg_size", "min_letters_all_caps"}
        assert expected.issubset(set(THRESHOLDS.keys()))

    def test_reply_quick_is_positive(self):
        assert THRESHOLDS["reply_quick_seconds"] > 0

    def test_msg_size_ordering(self):
        ms = THRESHOLDS["msg_size"]
        assert ms["vazia"] < ms["curta"] < ms["media"] < ms["longa"]


class TestPeriodosDia:
    """Testes para PERIODOS_DIA."""

    def test_covers_24_hours(self):
        hours = set()
        for inicio, fim in PERIODOS_DIA.values():
            hours.update(range(inicio, fim))
        assert hours == set(range(24))

    def test_values_are_tuples(self):
        for nome, val in PERIODOS_DIA.items():
            assert isinstance(val, tuple) and len(val) == 2, f"'{nome}' deveria ser tupla (inicio, fim)"


class TestDiasSemana:
    """Testes para DIAS_SEMANA."""

    def test_seven_days(self):
        assert len(DIAS_SEMANA) == 7

    def test_keys_0_to_6(self):
        assert set(DIAS_SEMANA.keys()) == set(range(7))


class TestMeses:
    """Testes para MESES."""

    def test_twelve_months(self):
        assert len(MESES) == 12

    def test_keys_1_to_12(self):
        assert set(MESES.keys()) == set(range(1, 13))


# =============================================================================
# REGEX_PATTERNS
# =============================================================================


class TestRegexPatterns:
    """Testes para REGEX_PATTERNS — compilam e casam inputs esperados."""

    def test_all_patterns_compile(self):
        for name, pattern in REGEX_PATTERNS.items():
            try:
                re.compile(pattern)
            except re.error as e:
                pytest.fail(f"REGEX_PATTERNS['{name}'] nao compila: {e}")

    def test_timestamp_original(self):
        pat = re.compile(REGEX_PATTERNS["timestamp_original"])
        m = pat.match("[24/11/24, 15:30:05]")
        assert m is not None
        assert m.group(1) == "24/11/24"
        assert m.group(2) == "15:30:05"

    def test_timestamp_original_no_match(self):
        pat = re.compile(REGEX_PATTERNS["timestamp_original"])
        assert pat.match("24/11/24 15:30:05") is None

    def test_timestamp_otimizado(self):
        pat = re.compile(REGEX_PATTERNS["timestamp_otimizado"])
        m = pat.match("24/11/24 15:30:05")
        assert m is not None
        assert m.group(1) == "24/11/24"

    def test_mensagem_completa(self):
        pat = re.compile(REGEX_PATTERNS["mensagem_completa"])
        m = pat.match("24/11/24 15:30:05 P1: Oi tudo bem?")
        assert m is not None
        assert m.group(3) == "P1"
        assert m.group(4) == "Oi tudo bem?"

    def test_midia_omitida(self):
        pat = re.compile(REGEX_PATTERNS["midia_omitida"])
        for tipo in ("audio", "image", "video", "sticker", "GIF", "document", "video note"):
            assert pat.search(f"{tipo} omitted"), f"nao casou '{tipo} omitted'"

    def test_midia_anexada(self):
        pat = re.compile(REGEX_PATTERNS["midia_anexada"])
        m = pat.search("<attached: IMG-001.jpg>")
        assert m is not None
        assert m.group(1) == "IMG-001.jpg"

    def test_url(self):
        pat = re.compile(REGEX_PATTERNS["url"])
        assert pat.search("veja https://example.com/path?q=1")
        assert pat.search("http://foo.bar")
        assert pat.search("sem link aqui") is None

    def test_editada(self):
        pat = re.compile(REGEX_PATTERNS["editada"])
        assert pat.search("<This message was edited>")

    def test_deletada(self):
        pat = re.compile(REGEX_PATTERNS["deletada"])
        assert pat.search("This message was deleted")
