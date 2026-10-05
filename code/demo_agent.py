import asyncio
import sqlite3
from typing import Final

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.workflow import Context
from llama_index.llms.ollama import Ollama

from config import DB_PATH
from tools.calculator import calculator
from tools.read_file import read_file
from tools.write_file import write_file

SESSION_ID: Final = "default"
MEMORY_LIMIT: Final = 20
VALID_MEMORY_ROLES: Final = frozenset({"user", "assistant", "system"})


def init_db() -> None:
    """初始化记忆表，并兼容旧版数据库结构。"""
    conn: sqlite3.Connection | None = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memorise (
                id INTEGER PRIMARY KEY,
                session_id TEXT NOT NULL DEFAULT 'default',
                role TEXT NOT NULL DEFAULT 'legacy',
                content TEXT NOT NULL,
                create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        existing_columns = {
            row[1] for row in cursor.execute("PRAGMA table_info(memorise)")
        }

        if "session_id" not in existing_columns:
            cursor.execute(
                "ALTER TABLE memorise "
                "ADD COLUMN session_id TEXT NOT NULL DEFAULT 'default'"
            )

        if "role" not in existing_columns:
            cursor.execute(
                "ALTER TABLE memorise "
                "ADD COLUMN role TEXT NOT NULL DEFAULT 'legacy'"
            )

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_memorise_session_role_id "
            "ON memorise(session_id, role, id)"
        )
        conn.commit()

    except sqlite3.Error:
        if conn is not None:
            conn.rollback()
        raise

    finally:
        if conn is not None:
            conn.close()


def add_memory(
    role: str,
    content: str,
    session_id: str = SESSION_ID,
) -> None:
    """保存一条带角色和会话标识的记忆。"""
    if role not in VALID_MEMORY_ROLES:
        raise ValueError(f"不支持的记忆角色: {role!r}")

    if not isinstance(content, str):
        raise TypeError("content 必须是字符串")

    text = content.strip()
    if not text:
        raise ValueError("content 不能为空")

    conn: sqlite3.Connection | None = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO memorise (session_id, role, content)
            VALUES (?, ?, ?)
            """,
            (session_id, role, text),
        )
        conn.commit()

    except sqlite3.Error:
        if conn is not None:
            conn.rollback()
        raise

    finally:
        if conn is not None:
            conn.close()


def read_memory() -> str:
    """读取长期记忆。

    工具用途：读取用户和系统保存的长期信息。
    参数：无。
    返回：以成功提示开头的记忆文本。
    失败：数据库异常会向上抛出。
    成功返回不是错误文本。
    """
    print("===正在读取记忆===\n")

    conn: sqlite3.Connection | None = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        rows = cursor.execute(
            """
            SELECT role, content, create_time
            FROM memorise
            WHERE session_id = ?
              AND role IN ('user', 'system')
            ORDER BY id DESC
            LIMIT ?
            """,
            (SESSION_ID, MEMORY_LIMIT),
        ).fetchall()

    except sqlite3.Error:
        raise

    finally:
        if conn is not None:
            conn.close()

    if not rows:
        return "以下是成功读取到的长期记忆，共 0 条。"

    rows.reverse()
    lines = [f"以下是成功读取到的长期记忆，共 {len(rows)} 条："]
    role_labels = {"user": "用户", "system": "系统"}

    for index, (role, content, create_time) in enumerate(rows, start=1):
        label = role_labels.get(role, role)
        lines.append(f"[{index}][{label}][{create_time}] {content}")

    return "\n".join(lines)


agent = FunctionAgent(
    tools=[calculator, read_file, write_file, read_memory],
    llm=Ollama(
        model="qwen2.5:3b",
        request_timeout=360.0,
        context_window=8000,
    ),
    system_prompt=(
        "你是一个私人助手。"
        "涉及用户历史、偏好或长期信息的问题，先调用 read_memory。"
        "read_memory 返回以“以下是成功读取到的长期记忆”开头的文本时，"
        "必须将其视为读取成功并基于该内容回答。"
        "不得声称读取失败；只有工具实际抛出异常时才能说明读取失败。"
    ),
)
ctx = Context(workflow=agent)


async def main() -> None:
    try:
        init_db()
    except sqlite3.Error as exc:
        raise RuntimeError("数据库初始化失败") from exc

    while True:
        user_input = input("User>> ")

        if user_input.strip().lower() == "exit":
            print("===已停止运行===")
            break

        add_memory("user", user_input)
        response = await agent.run(user_msg=user_input, ctx=ctx)
        response_text = str(response)
        print(f"AI>>{response_text}")

        if response_text.strip():
            add_memory("assistant", response_text)


if __name__ == "__main__":
    asyncio.run(main())
