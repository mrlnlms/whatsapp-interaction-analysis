#!/usr/bin/env python3
"""
Script para transcrição de áudios/vídeos do WhatsApp usando Groq Whisper API.

Uso:
    python scripts/transcribe_media.py

Requisitos:
    - pip install groq python-dotenv
    - GROQ_API_KEY configurada no .env

Comportamento:
    - Detecta arquivos de áudio/vídeo na pasta de mídia
    - Pula arquivos já transcritos (resume)
    - Salva progresso a cada 10 arquivos
    - Gera: data/processed/{DATA_FOLDER}/transcriptions.csv
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Carrega .env
from dotenv import load_dotenv
load_dotenv()

# Configuração de paths
PROJECT_ROOT = Path(os.getenv('PROJECT_ROOT', '.'))
DATA_FOLDER = os.getenv('DATA_FOLDER', 'export_2024-10_2025-10')

# Paths derivados
MEDIA_DIR = PROJECT_ROOT / 'data' / 'raw' / DATA_FOLDER / 'media'
OUTPUT_DIR = PROJECT_ROOT / 'data' / 'processed' / DATA_FOLDER
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Arquivos de saída
PROGRESS_FILE = OUTPUT_DIR / 'transcriptions_progress.csv'
COMPLETE_FILE = OUTPUT_DIR / 'transcriptions.csv'

# API Key (obrigatória no .env)
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Formatos suportados
SUPPORTED_FORMATS = ['.opus', '.mp3', '.wav', '.mp4', '.m4a', '.webm', '.mpeg', '.mpga']


def setup_groq():
    """Configura cliente Groq."""
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY não configurada!")
        print()
        print("   Adicione no arquivo .env:")
        print("   GROQ_API_KEY=sua_chave_aqui")
        print()
        print("   Obtenha sua chave em: https://console.groq.com/keys")
        sys.exit(1)
    
    try:
        from groq import Groq
    except ImportError:
        print("❌ Groq não instalado. Execute: pip install groq")
        sys.exit(1)
    
    client = Groq(api_key=GROQ_API_KEY)
    
    # Teste rápido
    try:
        test = client.chat.completions.create(
            messages=[{"role": "user", "content": "Diga apenas: OK"}],
            model="llama-3.3-70b-versatile",
            max_tokens=10
        )
        print(f"✅ Groq API conectada: {test.choices[0].message.content.strip()}")
        return client
    except Exception as e:
        print(f"❌ Erro na API Groq: {e}")
        sys.exit(1)


def scan_media_files(media_dir: Path) -> list:
    """Escaneia diretório em busca de arquivos de áudio/vídeo."""
    files = []
    
    if not media_dir.exists():
        print(f"❌ Diretório não encontrado: {media_dir}")
        return files
    
    for file_path in media_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_FORMATS:
            # Extrai tipo do nome (AUDIO, VIDEO)
            parts = file_path.name.split('-')
            media_type = parts[1].lower() if len(parts) >= 2 else 'unknown'
            
            files.append({
                'file_path': file_path.name,
                'full_path': str(file_path),
                'media_type': media_type,
                'size_mb': file_path.stat().st_size / (1024 * 1024)
            })
    
    return files


def transcribe_audio(client, file_path: Path) -> dict:
    """Transcreve um arquivo de áudio/vídeo."""
    try:
        if not file_path.exists():
            return {
                'transcription': '',
                'transcription_status': 'error',
                'transcription_language': None,
                'error_message': 'Arquivo não encontrado'
            }
        
        # Verifica tamanho (limite: 25MB)
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 25:
            return {
                'transcription': '',
                'transcription_status': 'error',
                'transcription_language': None,
                'error_message': f'Arquivo muito grande: {file_size_mb:.1f}MB (max 25MB)'
            }
        
        # Transcreve
        with open(file_path, 'rb') as audio_file:
            result = client.audio.transcriptions.create(
                file=(file_path.name, audio_file.read()),
                model="whisper-large-v3",
                language="pt",
                response_format="verbose_json",
                temperature=0.0
            )
        
        return {
            'transcription': result.text.strip(),
            'transcription_status': 'completed',
            'transcription_language': getattr(result, 'language', 'pt'),
            'error_message': None
        }
    
    except Exception as e:
        return {
            'transcription': '',
            'transcription_status': 'error',
            'transcription_language': None,
            'error_message': str(e)
        }


def load_or_create_dataframe(media_files: list):
    """Carrega progresso existente ou cria novo DataFrame."""
    import pandas as pd
    
    # Prioridade: complete > progress > novo
    if COMPLETE_FILE.exists():
        print(f"✅ Encontrado arquivo COMPLETO: {COMPLETE_FILE.name}")
        return pd.read_csv(COMPLETE_FILE), True
    
    if PROGRESS_FILE.exists():
        print(f"⚠️  Encontrado arquivo de PROGRESSO: {PROGRESS_FILE.name}")
        return pd.read_csv(PROGRESS_FILE), False
    
    # Cria novo
    print("🆕 Criando nova base de transcrições...")
    df = pd.DataFrame(media_files)
    df['transcription'] = None
    df['transcription_status'] = 'pending'
    df['transcription_language'] = None
    df['transcription_confidence'] = None
    df['is_synthetic'] = False
    df['error_message'] = None
    
    return df, False


def main():
    """Executa pipeline de transcrição."""
    import pandas as pd
    
    print()
    print("=" * 70)
    print("🎙️  TRANSCRIÇÃO DE MÍDIAS DO WHATSAPP")
    print("=" * 70)
    print()
    print(f"📁 Projeto: {PROJECT_ROOT}")
    print(f"📂 Pasta de dados: {DATA_FOLDER}")
    print(f"🎬 Diretório de mídia: {MEDIA_DIR}")
    print(f"💾 Saída: {COMPLETE_FILE}")
    print()
    
    # Setup API
    client = setup_groq()
    print()
    
    # Escaneia arquivos
    print("🔍 Escaneando arquivos de mídia...")
    media_files = scan_media_files(MEDIA_DIR)
    
    if not media_files:
        print("❌ Nenhum arquivo de áudio/vídeo encontrado!")
        return
    
    print(f"   Encontrados: {len(media_files)} arquivos")
    
    # Carrega ou cria DataFrame
    df, is_complete = load_or_create_dataframe(media_files)
    
    # Status atual
    completed = (df['transcription_status'] == 'completed').sum()
    errors = (df['transcription_status'] == 'error').sum()
    pending = (df['transcription_status'] == 'pending').sum()
    
    print()
    print("📊 Status atual:")
    print(f"   ✅ Completos: {completed:,}")
    print(f"   ❌ Erros: {errors:,}")
    print(f"   ⏳ Pendentes: {pending:,}")
    print()
    
    # Se já está completo, só mostra estatísticas
    if is_complete or pending == 0:
        print("=" * 70)
        print("✅ TRANSCRIÇÕES JÁ COMPLETAS!")
        print()
        print("Para reprocessar, delete os arquivos:")
        print(f"   - {COMPLETE_FILE}")
        print(f"   - {PROGRESS_FILE}")
        print("=" * 70)
        return
    
    # Processa pendentes
    print("=" * 70)
    print("🎙️  INICIANDO PROCESSAMENTO")
    print(f"   Estimativa: ~{pending * 3 // 60} minutos")
    print("=" * 70)
    print()
    
    df_pending = df[df['transcription_status'] == 'pending']
    processed = 0
    start_time = datetime.now()
    
    for idx in df_pending.index:
        row = df.loc[idx]
        file_path = MEDIA_DIR / row['file_path']
        
        # Transcreve
        result = transcribe_audio(client, file_path)
        
        # Atualiza DataFrame
        df.at[idx, 'transcription'] = result['transcription']
        df.at[idx, 'transcription_status'] = result['transcription_status']
        df.at[idx, 'transcription_language'] = result['transcription_language']
        df.at[idx, 'error_message'] = result['error_message']
        
        processed += 1
        
        # Progress bar simples
        pct = processed / pending * 100
        status = "✅" if result['transcription_status'] == 'completed' else "❌"
        print(f"   [{processed:3d}/{pending}] {pct:5.1f}% {status} {row['file_path'][:50]}")
        
        # Salva a cada 10
        if processed % 10 == 0:
            df.to_csv(PROGRESS_FILE, index=False)
            elapsed = (datetime.now() - start_time).seconds
            rate = processed / elapsed if elapsed > 0 else 0
            remaining = (pending - processed) / rate if rate > 0 else 0
            print(f"   💾 Progresso salvo | ⏱️  ~{remaining/60:.0f} min restantes")
    
    # Salva versão final
    df.to_csv(COMPLETE_FILE, index=False)
    
    # Remove arquivo de progresso
    if PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()
    
    # Estatísticas finais
    elapsed = (datetime.now() - start_time).seconds
    completed_final = (df['transcription_status'] == 'completed').sum()
    errors_final = (df['transcription_status'] == 'error').sum()
    
    print()
    print("=" * 70)
    print("✅ PROCESSAMENTO CONCLUÍDO!")
    print("=" * 70)
    print()
    print("📊 Resultado:")
    print(f"   ✅ Transcritos: {completed_final:,}")
    print(f"   ❌ Erros: {errors_final:,}")
    print(f"   ⏱️  Tempo: {elapsed // 60}min {elapsed % 60}s")
    print()
    print(f"💾 Salvo em: {COMPLETE_FILE}")
    print()
    
    # Mostra erros se houver
    if errors_final > 0:
        print("⚠️  Arquivos com erro:")
        error_df = df[df['transcription_status'] == 'error']
        for _, row in error_df[['file_path', 'error_message']].head(10).iterrows():
            print(f"   - {row['file_path']}: {row['error_message']}")
    
    print("=" * 70)


if __name__ == '__main__':
    main()