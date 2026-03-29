"""Entry point para python -m cli."""

import sys
from pathlib import Path

# Adiciona src/ ao path pra imports de config, cleaning, wrangling, etc.
_src_dir = str(Path(__file__).parent.parent / "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from cli import app

app()
