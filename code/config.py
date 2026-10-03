from pathlib import Path
from typing import Final

APP_ROOT: Final = Path(__file__).resolve().parent

READ_ROOT: Final = (APP_ROOT / "data").resolve()

MAX_READ_BYTES: Final = 1_000_000

ALLOWED_SUFFIXES: Final = frozenset({".txt", ".md", ".json"})

ALLOW_SYMLINKS: Final = False