from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import asyncio
from typing import List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.agents.output_parsers import JSONAgentOutputParser  # 新增：導入 JSONAgentOutputParser
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os
import time

load_dotenv()
LLM_URL = os.getenv("LLM_URL", "")
LLM_MODEL_PATH = os.getenv("LLM_MODEL_PATH", "")
print(LLM_MODEL_PATH, LLM_URL)
model = ChatOpenAI(
    model=LLM_MODEL_PATH,
    base_url=LLM_URL,
    api_key="EMPTY",  # 自建vllm服務可填任意字串
)

# 使用ChatPromptTemplate替換原來的消息列表
prompt = [
    SystemMessage(content="你是一個會使用工具的AI助手。"),
    HumanMessage(content="你使用的語言是什麼?"),
    AIMessage(content="我只會使用繁體中文和英文，其他語言我都不使用。"),
    HumanMessage(content="你是否會計劃步驟?"),
    AIMessage(content="我會先了解使用者的需求後，再來一步一步計畫步驟，最後依照步驟執行，讓我可以準確完成任務。"),
]

# 初始化聊天記憶，並將 prompt 加入 memory 中
memory = ConversationBufferMemory(return_messages=True)
memory.chat_memory.messages = prompt.copy()

async def main():

    async with MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["servers/math_server.py"],
                "transport": "stdio",
            },
            "database": { 
                "command": "python",
                "args": ["servers/db_server.py"],
                "transport": "stdio",
            },
            "markitdown": {
                "command": "python",
                "args": ["servers/markitdown_server.py"],
                "transport": "stdio",
            },
            "filesystem": {
                "command": "python",
                "args": ["servers/filesystem_server.py"],
                "transport": "stdio",
            },
            "parentrag": {
                "command": "python",
                "args": ["servers/parent_rag_server.py"],
                "transport": "stdio",
            },
            "test": {
                "command": "python",
                "args": ["servers/test_server.py"],
                "transport": "stdio",
            }
        }
    ) as client:
        agent = create_react_agent(model, client.get_tools())

        while True:
            user_input = input("User > ").strip()
            if user_input.lower() in ['exit', 'q']:
                print("結束!")
                return
            else: 
                start = time.time()

                all_messages = memory.chat_memory.messages + [HumanMessage(content=user_input)]
                        
                agent_response = await agent.ainvoke({"messages": all_messages})
                
                # 提取最後一條AI消息作為最終答案
                final_messages = agent_response.get("messages", [])
                final_answer = "無法獲得答案"
                
                # 從最後往前找AI消息
                for msg in reversed(final_messages):
                    if isinstance(msg, AIMessage):
                        final_answer = msg.content
                        break

                print(final_answer)
                # 更新記憶
                memory.save_context({"input": user_input}, {"output": final_answer})

                end = time.time()
                print(f"Take {(end-start) / 60} mins")

# 4. 啟動
if __name__ == "__main__":
    asyncio.run(main())