import asyncio
import sqlite3

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.workflow import Context
from llama_index.llms.ollama import Ollama

from tools.calculator import calculator
from tools.read_file import read_file
from tools.write_file import write_file
from config import DB_PATH
db_path = DB_PATH

def init_db():
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''create table if not exists memorise(
                          id integer primary key,
                          content text not null,
                          create_time timestamp default current_timestamp
                          )
                       ''')
        conn.commit()
    except sqlite3.Error:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()


def memorise(text):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO memorise (content) VALUES (?)", (text,))
    conn.commit()
    conn.close()

def read_memory() -> str:
    """
    工具用途：读取此前保存的对话记忆。
    参数：无。
    返回：按时间顺序排列的记忆文本。
    失败：数据库异常会向上抛出。
    成功返回不是错误文本。
    """
    print("===正在读取记忆===\n")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM memorise ORDER BY id ")
    rows = cursor.fetchall()
    conn.close()
    return "\n".join([row[0] for row in rows])



agent=FunctionAgent(
    tools=[calculator, read_file, write_file,read_memory],
    llm=Ollama(
        model="qwen2.5:3b",
        request_timeout=360.0,
        context_window=8000),
        system_prompt="你是一个私人助手，可以回答用户的任何问题。在回答用户问题之前请先调用read_memory工具读取历史记忆，read_memory 成功返回文本时，必须将其视为读取成功，并基于返回内容回答。只有工具明确抛出异常时，才能说明读取失败，不得自行编造读取失败。"
)
ctx=Context(workflow=agent)
async def main():
    try:
        init_db()
    except sqlite3.Error as e:
        print(e)
        return
    while True:
        user_input = input("User>> ")
        memorise(user_input)
        response=await agent.run(user_msg=user_input,ctx=ctx)
        memorise(str(response))
        print(f"AI>>{response}")
        if user_input=="exit":
            print("===已停止运行===")
            break

if __name__=="__main__":
    asyncio.run(main())
