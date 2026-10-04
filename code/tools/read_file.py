from pathlib import Path

from config import (
    ALLOW_SYMLINKS,
    ALLOWED_SUFFIXES,
    MAX_READ_BYTES,
    READ_ROOT,
)


def _ensure_read_root() -> None:
    """确认配置的读取根目录可用。"""
    if not READ_ROOT.exists():
        raise RuntimeError(f"读取根目录不存在: {READ_ROOT}")

    if not READ_ROOT.is_dir():
        raise RuntimeError(f"读取根目录不是目录: {READ_ROOT}")


def _reject_symlink_components(relative_path: Path) -> None:
    """当策略禁止符号链接时，检查相对路径中的每个组件。"""
    current = READ_ROOT

    for part in relative_path.parts:
        if part in ("", "."):
            continue

        if part == "..":
            current = current.parent
            continue

        current = current / part

        if current.is_symlink():
            raise PermissionError(
                f"不允许访问符号链接: {current}"
            )


def _resolve_read_path(file_name: str) -> Path:
    """验证并解析一个安全可读路径。

    该函数只负责路径检查，不打开和读取文件。
    """
    _ensure_read_root()

    if not isinstance(file_name, str):
        raise ValueError("file_name 必须是字符串")

    if not file_name.strip():
        raise ValueError("file_name 不能为空")

    if "\x00" in file_name:
        raise ValueError("file_name 不能包含空字符")

    relative_path = Path(file_name)

    # 只允许相对路径，拒绝盘符路径、UNC 路径和绝对路径
    if relative_path.is_absolute() or relative_path.drive:
        raise ValueError("只允许传入相对路径")

    candidate = (READ_ROOT / relative_path).resolve()

    # 关键边界检查：最终真实路径必须位于 READ_ROOT 内
    try:
        candidate.relative_to(READ_ROOT)
    except ValueError as exc:
        raise PermissionError(
            f"路径超出允许的读取范围: {candidate}"
        ) from exc

    # resolve() 会解析符号链接；如果策略禁止符号链接，
    # 还需要检查原始路径中是否包含链接组件。
    if not ALLOW_SYMLINKS:
        _reject_symlink_components(relative_path)

    return candidate


def read_file(file_name: str) -> str:
    """读取允许目录内的 UTF-8 文本文件。

    参数:
        file_name: 相对于 READ_ROOT 的文本文件路径。

    返回:
        文件的完整文本内容。

    异常:
        ValueError:
            路径无效、文件类型不允许或文件过大。
        PermissionError:
            路径越界或访问了不允许的符号链接。
        FileNotFoundError:
            文件不存在。
        IsADirectoryError:
            传入的是目录。
        UnicodeDecodeError:
            文件不是有效的 UTF-8 文本。
    """
    print("====已调用read_file====")
    path = _resolve_read_path(file_name)

    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")

    if path.is_dir():
        raise IsADirectoryError(f"路径是目录: {path}")

    if not path.is_file():
        raise ValueError(f"路径不是普通文件: {path}")

    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        raise ValueError(
            f"不允许读取该文件类型: {path.suffix or '(无扩展名)'}"
        )

    file_size = path.stat().st_size

    if file_size > MAX_READ_BYTES:
        raise ValueError(
            f"文件过大: {file_size} 字节，"
            f"最大允许 {MAX_READ_BYTES} 字节"
        )

    with path.open(
        "r",
        encoding="utf-8",
        errors="strict",
    ) as file:
        return file.read()