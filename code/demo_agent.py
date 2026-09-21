import asyncio
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama
from llama_index.core.workflow import Context
from tools.calculator import calculator
from tools.read_file import read_file
from tools.write_file import write_file



agent=FunctionAgent(
    tools=[calculator, read_file, write_file],
    llm=Ollama(
        model="gemma4:12b",
        request_timeout=360.0,
        context_window=8000),
        system_prompt="You are a helpful assistant."
)
ctx=Context(workflow="calculator,write_file,read_file")
async def main():
    while True:
        user_input = input("User>> ")
        response=await agent.run(user_msg=user_input,ctx=ctx)
        print(f"AI>>{response}")
        if user_input=="exit":
            print("===已停止运行===")
            break

if __name__=="__main__":
    asyncio.run(main())