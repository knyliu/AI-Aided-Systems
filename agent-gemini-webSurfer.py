import os
from dotenv import load_dotenv
import asyncio

# 載入 .env 檔案中的環境變數
load_dotenv()

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_core.models import UserMessage
from autogen_ext.models.replay import ReplayChatCompletionClient

# 自動使用 Replay 模型決定回應內容，完全不傳入 prompt
class AutoUserProxyAgent(UserProxyAgent):
    async def get_message(self):
        chat_completions = [
            "exit",
            "keep searching",
        ]
        client = ReplayChatCompletionClient(chat_completions)
        # 直接傳入空訊息列表，讓 Replay 模型依預設順序產生回應
        response = await client.create([])
        decision = response.content.strip().lower()
        print(f"自動決策: {decision}")
        return UserMessage(content=decision, source=self.name)

async def main():
    # 從 .env 讀取 Gemini API 金鑰
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    
    # 使用 Gemini API，指定 model 為 "gemini-1.5-flash-8b"
    model_client = OpenAIChatCompletionClient(
        model="gemini-1.5-flash-8b",
        api_key=gemini_api_key,
    )
    
    # 建立各代理人
    assistant = AssistantAgent("assistant", model_client)
    web_surfer = MultimodalWebSurfer("web_surfer", model_client, start_page="https://www.google.com/")
    user_proxy = AutoUserProxyAgent("user_proxy")
    
    # 當對話中出現 "exit" 時即終止對話
    termination_condition = TextMentionTermination("exit")
    
    # 建立一個循環團隊，讓各代理人依序參與討論
    team = RoundRobinGroupChat(
        [web_surfer, assistant, user_proxy],
        termination_condition=termination_condition
    )
    
    # 啟動團隊對話，任務是「搜尋 Gemini 的相關資訊，並撰寫一份簡短摘要」
    await Console(team.run_stream(task="請搜尋 Gemini 的相關資訊，並撰寫一份簡短摘要。"))

if __name__ == '__main__':
    asyncio.run(main())
