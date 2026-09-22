import asyncio
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama
from llama_index.core.workflow import Context
from tools.calculator import calculator
from tools.read_file import read_file
from tools.write_file import write_file
import sqlite3


DB_PATH = "memorise.db"

def init_db():
    conn = sqlite3.connect('memorise.db')
    cursor = conn.cursor()
    cursor.execute('''create table memorise(
                      id integer primary key,
                      content text not null,
                      create_time timestamp default current_timestamp
                      )
                   ''')
    conn.commit()
    conn.close()


def memorise(text):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO memorise (content) VALUES (?)", (text,))
    conn.commit()
    conn.close()

def read_memory() -> str:
    """读取全部历史记忆"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM memorise ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return "\n".join([row[0] for row in rows])



agent=FunctionAgent(
    tools=[calculator, read_file, write_file,read_memory],
    llm=Ollama(
        model="gemma4:12b",
        request_timeout=360.0,
        context_window=8000),
        system_prompt="你是一个私人助手，可以回答用户的任何问题。在回答用户问题之前请先调用read_memory工具读取历史记忆，提取关键信息后再回答用户问题"
)
ctx=Context(workflow=agent)
async def main():
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
