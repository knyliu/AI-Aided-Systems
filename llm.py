# llm.py

from llama_index.llms.ollama import Ollama

# 初始化 Ollama，統一管理 LLM 參數
ollama_for_answers = Ollama(model="llama3.1", request_timeout=180.0)

def get_llm_response(prompt: str) -> str:
    """使用 LLM (Ollama) 產生回應"""
    return str(ollama_for_answers.complete(prompt))
