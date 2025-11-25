# Scripts

Scripts utilitários para processamento de dados.

## transcribe_media.py

Transcreve arquivos de áudio e vídeo do WhatsApp usando a API Groq Whisper.

### Uso

```bash
python scripts/transcribe_media.py
```

### Requisitos

```bash
pip install groq python-dotenv
```

### Configuração

No arquivo `.env`:

```properties
PROJECT_ROOT=/caminho/para/whatsapp-ds-analytics
DATA_FOLDER=export_2024-10_2025-10
GROQ_API_KEY=sua_chave_aqui  # opcional, tem fallback no script
```

### Comportamento

1. **Primeira execução:** Processa todos os arquivos (~40 min para ~700 arquivos)
2. **Interrupção:** Salva progresso a cada 10 arquivos em `transcriptions_progress.csv`
3. **Retomada:** Continua de onde parou automaticamente
4. **Completo:** Gera `transcriptions.csv` e deleta arquivo de progresso

### Output

```
data/processed/{DATA_FOLDER}/transcriptions.csv
```

Colunas:
- `file_path`: Nome do arquivo
- `media_type`: audio/video
- `transcription`: Texto transcrito
- `transcription_status`: completed/error/pending
- `transcription_language`: Idioma detectado
- `error_message`: Mensagem de erro (se houver)
- `is_synthetic`: Se é arquivo órfão

### Integração com Pipeline

O notebook `02-data-wrangling.qmd` detecta automaticamente este arquivo:
- Se existe → carrega e faz merge com mensagens
- Se não existe → exibe instruções para rodar o script
