import os
from dotenv import load_dotenv
import asyncio
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 載入 .env 檔案中的環境變數
load_dotenv()

async def main():
 
    model_client = OpenAIChatCompletionClient(
        model="llama3.2:latest",
        base_url="http://localhost:11434/v1",
        api_key="placeholder",
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": False,
            "family": "unknown",
        },
    )
    response = await model_client.create([UserMessage(content="What is the capital of France?", source="user")])
    print("Agent response:", response)

if __name__ == '__main__':
    asyncio.run(main())