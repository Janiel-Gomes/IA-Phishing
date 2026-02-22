import sys
import os

# Adicionar o diretório raiz ao path para importar os agentes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from agents.text_agent import NLPTextAgent
from agents.html_agent import HTMLStructuralAgent
from agents.vision_agent import VisionAgent
from agents.orchestrator import PhishingOrchestrator

def test_agents():
    print("--- Testando Inicializacao dos Agentes ---")
    try:
        text_agent = NLPTextAgent()
        html_agent = HTMLStructuralAgent()
        vision_agent = VisionAgent()
        orchestrator = PhishingOrchestrator()
        print("[OK] Todos os agentes inicializados com sucesso.")
    except Exception as e:
        print(f"[ERROR] Erro na inicializacao: {e}")
        return

    print("\n--- Testando Análise dos Agentes ---")
    text_result = text_agent.analyze("URGENTE: Sua conta será bloqueada! Clique aqui agora.")
    print(f"NLP Text Agent (Fallback): {text_result['result']} (Score: {text_result['score']})")
    
    html_result = html_agent.analyze(html_content="<html><body><form action='http://malicious.com'></form></body></html>", url="http://legit.com")
    print(f"HTML Agent (Fallback): {html_result['result']} (Score: {html_result['score']})")

    vision_result = vision_agent.analyze(image_data=b"fake_image_data")
    print(f"Vision Agent (Fallback): {vision_result['result']} (Score: {vision_result['score']})")

    print("\n--- Testando Orquestrador ---")
    full_analysis = orchestrator.analyze_full(url="http://test-phishing.com", text="Ganhe um prêmio!")
    print(f"Veredito Final: {full_analysis['verdict']} (Score: {full_analysis['risk_score']:.2f})")
    print(f"Resumo: {full_analysis['summary']}")

if __name__ == "__main__":
    test_agents()
