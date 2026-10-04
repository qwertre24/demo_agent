from pathlib import Path
from typing import Final


# config.py 位于 code/ 目录，因此 PROJECT_ROOT 就是 code/
PROJECT_ROOT: Final = Path(__file__).resolve().parent

# 只允许读取 code/data 下的文件
READ_ROOT: Final = (PROJECT_ROOT / "data").resolve()

# 单次读取上限，单位是字节
MAX_READ_BYTES: Final = 1_000_000

# 允许读取的文本文件类型
ALLOWED_SUFFIXES: Final[frozenset[str]] = frozenset(
    {".txt", ".md", ".json"}
)

# 默认拒绝符号链接
ALLOW_SYMLINKS: Final = False

# 默认数据库路径
STORAGE_ROOT: Final[Path] = (PROJECT_ROOT / "storage").resolve()
DB_PATH: Final[Path] = STORAGE_ROOT / "memorise.db"