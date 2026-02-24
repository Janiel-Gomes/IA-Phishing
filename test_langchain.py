import os
import sys

# Ensure current dir is in python path to load our agents module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.llm_client import llm_client
from agents.rag_manager import rag_manager

# Test LangChain & Structured Output
print("1. Testando chamada ao LLM (Qwen3) usando Langchain Structured Output...")
res = llm_client.analyze("prompt_text.txt", {"text": "http://g00gle.com-login-update.ru"})
print(f"Resultado estruturado retornado pelo LLM: {res}")

# Test RAG retrieval and Chat
print("\n2. Testando RAG (Chat)...")
chat_res = llm_client.chat_with_rag("Por que essa URL é considerada phishing?", {"url": "http://g00gle.com-login-update.ru", "verdict": "Phishing", "score": 0.9, "summary": "URL usa typo-squatting"})
print(f"Resposta do Chat RAG: {chat_res}")

print("\nConcluído!")
