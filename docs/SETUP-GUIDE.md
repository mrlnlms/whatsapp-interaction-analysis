# WhatsApp DS Analytics - Guia de Setup

## 📋 Pré-requisitos

- Python 3.11+
- Quarto CLI ([quarto.org](https://quarto.org/docs/get-started/))
- Git

---

## 🚀 Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/mrlnlms/whatsapp-ds-analytics.git
cd whatsapp-ds-analytics

# 2. Crie o ambiente virtual
python3 -m venv venv

# 3. Ative o ambiente
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Registre o kernel Jupyter
python -m ipykernel install --user --name=whatsapp-ds --display-name="WhatsApp DS"

# 6. Configure o ambiente
cp .env.example .env
# Edite o .env com seus paths

# 7. Verifique a instalação
quarto check jupyter
```

---

## ⚙️ Configuração do `.env`

Copie `.env.example` para `.env` e ajuste:

```bash
PROJECT_ROOT=/Users/SEU_USUARIO/caminho/para/whatsapp-ds-analytics
DATA_FOLDER=export_2024-10_2025-10
GROQ_API_KEY=sua_chave_aqui
```

| Variável | Descrição |
|----------|-----------|
| `PROJECT_ROOT` | Caminho absoluto da pasta do projeto |
| `DATA_FOLDER` | Nome da pasta em `data/raw/` com seus dados |
| `GROQ_API_KEY` | Chave da API Groq para transcrição (opcional) |

### Obter GROQ_API_KEY

1. Acesse [console.groq.com](https://console.groq.com)
2. Crie uma conta gratuita
3. Vá em **API Keys** e gere uma nova chave
4. Cole no `.env`

> A chave só é necessária se quiser transcrever áudios/vídeos.

---

## 🎙️ Transcrição de Áudios (Opcional)

Para transcrever áudios e vídeos do WhatsApp:

```bash
# 1. Certifique-se que GROQ_API_KEY está no .env

# 2. Execute o script de transcrição
python scripts/transcribe_media.py

# 3. Aguarde (~40 min para ~700 arquivos)
# O script salva progresso a cada 10 arquivos

# 4. Rode o notebook de wrangling
quarto render notebooks/02-data-wrangling.qmd
```

O script detecta automaticamente arquivos já transcritos e continua de onde parou.

---

## 🔧 Uso Diário

Se usar Positron/VS Code com interpretador configurado pro venv:

```bash
quarto preview
```

Se usar terminal avulso:

```bash
source venv/bin/activate
quarto preview
```

---

## 📁 Estrutura de Dados

```
data/
├── raw/
│   └── export_2024-10_2025-10/    ← Sua pasta (DATA_FOLDER)
│       ├── _chat.txt               ← Export do WhatsApp
│       └── media/                  ← Arquivos de mídia
├── interim/
│   └── export_2024-10_2025-10/
│       └── raw-data_cln7.txt       ← Saída do cleaning
└── processed/
    └── export_2024-10_2025-10/
        ├── messages.csv            ← Dataset principal
        ├── messages.parquet        ← Versão otimizada
        ├── transcriptions.csv      ← Cache de transcrições
        └── corpus_*.txt            ← Textos para NLP
```

---

## ⚠️ Troubleshooting

### Erro: `No module named 'profiling'`

Verifique:
1. O `.env` existe e tem `PROJECT_ROOT` correto
2. O kernel `whatsapp-ds` está registrado: `jupyter kernelspec list`

### Erro: `Starting python3 kernel...` (deveria ser `whatsapp-ds`)

Adicione no header do notebook:

```yaml
---
jupyter: whatsapp-ds
---
```

### Erro: `No module named 'nbformat'`

O venv não está ativado:

```bash
source venv/bin/activate
quarto preview
```

### Erro: `GROQ_API_KEY não configurada`

Adicione a chave no `.env`:

```bash
echo "GROQ_API_KEY=sua_chave_aqui" >> .env
```

### Erro: `Missing optional dependency 'pyarrow'`

Instale o pyarrow:

```bash
pip install pyarrow
```

---

## 🔄 Resetar Ambiente

```bash
rm -rf venv _site _freeze .quarto *_files
jupyter kernelspec uninstall whatsapp-ds -y
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m ipykernel install --user --name=whatsapp-ds --display-name="WhatsApp DS"
```

---

## 📁 Pastas Ignoradas pelo Git

| Pasta | Descrição |
|-------|-----------|
| `venv/` | Ambiente virtual |
| `.env` | Configurações locais |
| `data/` | Dados pessoais |
| `analysis/` | Outputs gerados |
| `_site/` | HTML do Quarto |
| `_freeze/` | Cache do Quarto |
| `.quarto/` | Cache interno |