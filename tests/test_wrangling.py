"""Testes para whatsapp/pipeline/wrangling.py — parsing, classificacao e enriquecimento."""

import pytest
import pandas as pd

from whatsapp.pipeline.wrangling import (
    parse_to_dataframe,
    classify_message_type,
    add_message_classification,
    extract_filename_from_content,
    extract_media_type_from_filename,
    enrich_content,
    _validate_schema,
    COLUMNS_CORE,
    REQUIRED_COLUMNS,
)


# =============================================================================
# parse_to_dataframe
# =============================================================================

class TestParseToDataframe:
    def test_parses_simple_messages(self, tmp_file, sample_chat_clean):
        inp, _ = tmp_file(sample_chat_clean)
        df = parse_to_dataframe(inp)
        assert len(df) == 8  # 9 linhas, mas continuacao e agregada a msg anterior
        assert list(df.columns) == [
            "linha_original", "data", "hora", "remetente", "conteudo", "timestamp"
        ]

    def test_first_message_content(self, tmp_file, sample_chat_clean):
        inp, _ = tmp_file(sample_chat_clean)
        df = parse_to_dataframe(inp)
        assert df.iloc[0]["remetente"] == "P1"
        assert df.iloc[0]["conteudo"] == "Oi, tudo bem?"
        assert df.iloc[0]["data"] == "24/11/24"
        assert df.iloc[0]["hora"] == "15:30:05"

    def test_multiline_message(self, tmp_file, sample_chat_clean):
        inp, _ = tmp_file(sample_chat_clean)
        df = parse_to_dataframe(inp)
        # Mensagem 3 (index 2) deve ter a continuacao concatenada
        msg3 = df.iloc[2]["conteudo"]
        assert "Bem tambem" in msg3
        assert "Continuacao da mensagem anterior" in msg3
        assert "\n" in msg3

    def test_timestamp_parsing(self, tmp_file, sample_chat_clean):
        inp, _ = tmp_file(sample_chat_clean)
        df = parse_to_dataframe(inp)
        assert "datetime64" in str(df["timestamp"].dtype)
        assert df.iloc[0]["timestamp"].year == 2024
        assert df.iloc[0]["timestamp"].month == 11
        assert df.iloc[0]["timestamp"].day == 24

    def test_empty_file(self, tmp_file):
        inp, _ = tmp_file("")
        df = parse_to_dataframe(inp)
        assert len(df) == 0
        assert "timestamp" in df.columns

    def test_single_message(self, tmp_file):
        inp, _ = tmp_file("24/11/24 15:30:05 P1: Oi\n")
        df = parse_to_dataframe(inp)
        assert len(df) == 1
        assert df.iloc[0]["conteudo"] == "Oi"


# =============================================================================
# classify_message_type
# =============================================================================

class TestClassifyMessageType:
    # Texto
    def test_text_pure(self):
        assert classify_message_type("Oi, tudo bem?") == "text_pure"

    def test_text_with_link(self):
        assert classify_message_type("Veja https://example.com") == "text_with_link"

    # Media omitted
    def test_audio_omitted(self):
        assert classify_message_type("audio omitted") == "audio_omitted"

    def test_image_omitted(self):
        assert classify_message_type("image omitted") == "image_omitted"

    def test_video_omitted(self):
        assert classify_message_type("video omitted") == "video_omitted"

    def test_sticker_omitted(self):
        assert classify_message_type("sticker omitted") == "sticker_omitted"

    def test_gif_omitted(self):
        assert classify_message_type("GIF omitted") == "gif_omitted"

    def test_document_omitted(self):
        assert classify_message_type("document omitted") == "document_omitted"

    # Media attached
    def test_image_attached(self):
        assert classify_message_type("<attached: IMG-20241124-WA0001.jpg>") == "image_attached"

    def test_audio_attached(self):
        assert classify_message_type("<attached: AUD-20241124-WA0001.opus>") == "audio_attached"

    def test_video_attached(self):
        assert classify_message_type("<attached: VID-20241124-WA0001.mp4>") == "video_attached"

    def test_sticker_attached(self):
        assert classify_message_type("<attached: STK-20241124-WA0001.webp>") == "sticker_attached"

    def test_contact_attached(self):
        assert classify_message_type("<attached: contact.vcf>") == "contact_attached"

    def test_file_attached_generic(self):
        assert classify_message_type("<attached: document.pdf>") == "file_attached"

    # Sistema
    def test_message_deleted(self):
        assert classify_message_type("This message was deleted") == "message_deleted"

    def test_message_edited(self):
        assert classify_message_type("<This message was edited>") == "message_edited"

    def test_voice_call(self):
        assert classify_message_type("Voice call") == "voice_call"

    def test_missed_call(self):
        assert classify_message_type("Missed voice call") == "missed_call"

    def test_system_message(self):
        assert classify_message_type("This message can't be displayed") == "system_message"


# =============================================================================
# add_message_classification
# =============================================================================

class TestAddMessageClassification:
    def test_adds_column(self, tmp_file, sample_chat_clean):
        inp, _ = tmp_file(sample_chat_clean)
        df = parse_to_dataframe(inp)
        df = add_message_classification(df)
        assert "tipo_mensagem" in df.columns
        assert df.iloc[0]["tipo_mensagem"] == "text_pure"
        assert df.iloc[3]["tipo_mensagem"] == "audio_omitted"

    def test_does_not_mutate_original(self, tmp_file, sample_chat_clean):
        inp, _ = tmp_file(sample_chat_clean)
        df = parse_to_dataframe(inp)
        original_cols = list(df.columns)
        add_message_classification(df)
        assert list(df.columns) == original_cols


# =============================================================================
# extract_filename_from_content
# =============================================================================

class TestExtractFilename:
    def test_extracts_filename(self):
        assert extract_filename_from_content("<attached: IMG-123.jpg>") == "IMG-123.jpg"

    def test_returns_none_for_no_attachment(self):
        assert extract_filename_from_content("Mensagem normal") is None

    def test_handles_spaces_in_filename(self):
        assert extract_filename_from_content("<attached: my file.pdf>") == "my file.pdf"


# =============================================================================
# extract_media_type_from_filename
# =============================================================================

class TestExtractMediaType:
    def test_audio(self):
        assert extract_media_type_from_filename("AUD-20241124-WA0001.opus") == "20241124"
        # Nota: a funcao extrai o segundo segmento split por "-"

    def test_img(self):
        assert extract_media_type_from_filename("IMG-20241124-WA0001.jpg") == "20241124"

    def test_none_input(self):
        assert extract_media_type_from_filename(None) is None

    def test_no_dash(self):
        assert extract_media_type_from_filename("simplefile.txt") is None


# =============================================================================
# enrich_content
# =============================================================================

class TestEnrichContent:
    def _build_df(self):
        """Cria DataFrame minimo para testar enriquecimento."""
        return pd.DataFrame([
            {"conteudo": "Oi", "tipo_mensagem": "text_pure", "tem_transcricao": False, "transcricao": None},
            {"conteudo": "audio omitted", "tipo_mensagem": "audio_omitted", "tem_transcricao": True, "transcricao": "Transcricao do audio"},
            {"conteudo": "image omitted", "tipo_mensagem": "image_omitted", "tem_transcricao": False, "transcricao": None},
            {"conteudo": "This message was deleted", "tipo_mensagem": "message_deleted", "tem_transcricao": False, "transcricao": None},
            {"conteudo": "Voice call", "tipo_mensagem": "voice_call", "tem_transcricao": False, "transcricao": None},
        ])

    def test_adds_grupo_mensagem(self):
        df = enrich_content(self._build_df())
        assert "grupo_mensagem" in df.columns
        assert list(df["grupo_mensagem"]) == ["TEXT", "AUDIO", "IMG", "SYSTEM", "CALL"]

    def test_adds_conteudo_enriquecido(self):
        df = enrich_content(self._build_df())
        assert "conteudo_enriquecido" in df.columns

    def test_text_keeps_original_content(self):
        df = enrich_content(self._build_df())
        assert df.iloc[0]["conteudo_enriquecido"] == "Oi"

    def test_audio_with_transcription_uses_it(self):
        df = enrich_content(self._build_df())
        assert df.iloc[1]["conteudo_enriquecido"] == "Transcricao do audio"

    def test_media_without_transcription_is_none(self):
        df = enrich_content(self._build_df())
        assert pd.isna(df.iloc[2]["conteudo_enriquecido"])

    def test_system_keeps_content(self):
        df = enrich_content(self._build_df())
        assert df.iloc[3]["conteudo_enriquecido"] == "This message was deleted"

    def test_does_not_mutate_original(self):
        df = self._build_df()
        original_cols = list(df.columns)
        enrich_content(df)
        assert list(df.columns) == original_cols


class TestValidateSchema:
    """Testa validação de schema entre stages do pipeline."""

    def test_passes_with_required_columns(self):
        df = pd.DataFrame({'data': [], 'hora': [], 'remetente': [], 'conteudo': []})
        _validate_schema(df, 'classify')  # não deve levantar

    def test_fails_missing_columns(self):
        df = pd.DataFrame({'data': [], 'hora': []})
        with pytest.raises(ValueError, match="requer colunas"):
            _validate_schema(df, 'classify')

    def test_skips_unknown_step(self):
        df = pd.DataFrame({'x': []})
        _validate_schema(df, 'parse')  # parse não tem schema, não deve levantar

    def test_all_stages_have_valid_columns(self):
        """Verifica que as colunas requeridas são strings não vazias."""
        for step_id, cols in REQUIRED_COLUMNS.items():
            assert isinstance(cols, set)
            for col in cols:
                assert isinstance(col, str) and len(col) > 0
