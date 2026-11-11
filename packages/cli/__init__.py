"""CLI package. Expõe o Kernel local sem alterar o namespace packages."""
from __future__ import annotations

import sys
from pathlib import Path

_CLI_DIR = str(Path(__file__).resolve().parent)
if _CLI_DIR not in sys.path:
    sys.path.insert(0, _CLI_DIR)
