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
```

| Variável | Descrição |
|----------|-----------|
| `PROJECT_ROOT` | Caminho absoluto da pasta do projeto |
| `DATA_FOLDER` | Nome da pasta em `data/raw/` com seus dados |

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