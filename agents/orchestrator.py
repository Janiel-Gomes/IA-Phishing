from agents.url_agent import URLLexicalAgent
from agents.text_agent import NLPTextAgent
from agents.html_agent import HTMLStructuralAgent
from agents.vision_agent import VisionAgent
from agents.llm_client import llm_client
import logging
import json

logger = logging.getLogger(__name__)

class PhishingOrchestrator:
    def __init__(self):
        logger.info("Inicializando Orquestrador de Agentes...")
        self.url_agent = URLLexicalAgent()
        self.text_agent = NLPTextAgent()
        self.html_agent = HTMLStructuralAgent()
        self.vision_agent = VisionAgent()
        logger.info("Todos os agentes foram inicializados.")

    def analyze_full(self, url=None, text=None, html=None, image_data=None):
        """
        Executa uma análise completa usando todos os agentes disponíveis.
        """
        results = []
        
        # 1. Análise de URL
        if url:
            results.append(self.url_agent.analyze(url))
        
        # 2. Análise de Texto (NLP)
        if text:
            results.append(self.text_agent.analyze(text))
        elif url and not text:
            results.append(self.text_agent.analyze(url))

        # 3. Análise de HTML
        if html or url:
            results.append(self.html_agent.analyze(html_content=html, url=url))

        # 4. Análise de Visão (Imagem)
        if image_data:
            results.append(self.vision_agent.analyze(image_data=image_data))

        # 5. Consolidação (Ensemble)
        final_verdict = self._consolidate(results)
        
        return {
            "verdict": final_verdict["result"],
            "risk_score": final_verdict["score"],
            "agent_details": results,
            "summary": final_verdict["summary"]
        }

    def _consolidate(self, results):
        """
        Consolida os resultados dos agentes em uma decisão final.
        """
        if not results:
            return {"result": "Desconhecido", "score": 0, "summary": "Nenhum dado fornecido."}

        total_score = 0
        weights = {
            "URL Lexical Analyzer": 0.25,
            "NLP Text Analyzer": 0.35,
            "HTML Structural Analyzer": 0.25,
            "Vision Analysis Agent": 0.15
        }
        
        total_weight = 0
        agent_results = []

        for res in results:
            agent_name = res.get("agent", "Unknown Agent")
            weight = weights.get(agent_name, 0.25)
            score = res.get("score", 0)
            total_score += score * weight
            total_weight += weight
            agent_results.append(f"{agent_name}: {res.get('result', 'Unknown')} ({score:.2f})")

        # ... rest of consolidation logic ...

        # Média ponderada
        final_score = total_score / total_weight if total_weight > 0 else 0
        
        # Veredito baseado no score consolidado
        if final_score > 0.6:
            result = "Phishing"
            summary = "Alta probabilidade de fraude detectada por múltiplos agentes."
        elif final_score > 0.4:
            result = "Suspeito"
            summary = "Padrões anômalos detectados. Recomenda-se cautela extrema."
        else:
            result = "Legítima"
            summary = "A análise não encontrou evidências significativas de phishing."

        return {
            "result": result,
            "score": final_score,
            "summary": summary
        }

    def chat_explanation(self, user_query, analysis_context):
        """
        Gera uma explicação baseada no contexto da análise e na pergunta do usuário.
        """
        prompt_vars = {
            "user_query": user_query,
            "context": json.dumps(analysis_context, indent=2, ensure_ascii=False)
        }
        
        # Usamos um prompt específico para o chat
        response = llm_client.analyze("prompt_chat.txt", prompt_vars)
        
        if response and "answer" in response:
            return response["answer"]
        
        return "Opa, minha inteligência (Gemini) está um pouco sobrecarregada agora. Por favor, aguarde uns 30 segundos e tente me perguntar novamente!"
