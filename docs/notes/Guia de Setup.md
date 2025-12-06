#  Guia de Setup
## WhatsApp DS Analytics - Guia de Setup

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

## ⚙️ Configuração do.env

Copie `.env.example` para `.env` e ajuste:

| `PROJECT_ROOT` | Caminho absoluto da pasta do projeto |
| --- | --- |
| `DATA_FOLDER` | Nome da pasta em `data/raw/` com seus dados |
| `GROQ_API_KEY` | Chave da API Groq para transcrição (opcional) |

### Obter GROQ\_API\_KEY

1. Acesse [console.groq.com](https://console.groq.com/)
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

## ⚠️ Troubleshooting

### Erro: No module named 'profiling'

Verifique: 1. O `.env` existe e tem `PROJECT_ROOT` correto 2. O kernel `whatsapp-ds` está registrado: `jupyter kernelspec list`

### Erro: No module named 'nbformat'

O venv não está ativado:

```bash
source venv/bin/activate
quarto preview
```

### Erro: Missing optional dependency 'pyarrow'

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