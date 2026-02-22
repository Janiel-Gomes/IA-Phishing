import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERRO: GEMINI_API_KEY não encontrada no arquivo .env")
    exit()

genai.configure(api_key=api_key)

print("--- Modelos Disponíveis ---")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"Name: {m.name}")
        print(f"Description: {m.description}")
        print(f"Capabilities: {m.supported_generation_methods}")
        print("-" * 30)
