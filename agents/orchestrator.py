from agents.url_agent import URLLexicalAgent
from agents.unified_agent import UnifiedTextHTMLAgent
from agents.vision_agent import VisionAgent
from agents.ssl_agent import SSLAnalysisAgent
from agents.llm_client import llm_client
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import json
import time

logger = logging.getLogger(__name__)

class PhishingOrchestrator:
    def __init__(self):
        logger.info("Inicializando Orquestrador de Agentes...")
        self.url_agent = URLLexicalAgent()
        self.unified_agent = UnifiedTextHTMLAgent()
        self.vision_agent = VisionAgent()
        self.ssl_agent = SSLAnalysisAgent()
        logger.info("Todos os agentes foram inicializados.")

    def analyze_full(self, url=None, text=None, html=None, image_data=None, model_pref=None, lang='PT'):
        """
        Executa uma análise completa usando todos os agentes em PARALELO.
        """
        start_time = time.time()
        results = []
        futures = {}
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # 1. Análise de URL (heurística + WHOIS)
            if url:
                futures[executor.submit(self.url_agent.analyze, url)] = "URL Agent"
            
            # 2. Análise unificada de Texto + HTML (LLM)
            if any([text, html, url]):
                futures[executor.submit(
                    self.unified_agent.analyze,
                    text=text or url,
                    html_content=html,
                    url=url,
                    model_pref=model_pref,
                    lang=lang
                )] = "Unified Agent"

            # 3. Análise de Visão (Imagem) — só executa se há imagem
            if image_data:
                futures[executor.submit(
                    self.vision_agent.analyze, 
                    image_data=image_data,
                    model_pref=model_pref,
                    lang=lang
                )] = "Vision Agent"

            # 4. Análise SSL/TLS
            if url:
                futures[executor.submit(
                    self.ssl_agent.analyze,
                    url=url,
                    lang=lang
                )] = "SSL Agent"

            # Coletar resultados à medida que ficam prontos
            for future in as_completed(futures):
                agent_name = futures[future]
                try:
                    result = future.result(timeout=30)
                    if result:
                        results.append(result)
                        agent_elapsed = time.time() - start_time
                        logger.info(f"  ✓ {agent_name} concluído em {agent_elapsed:.2f}s")
                except Exception as e:
                    logger.error(f"  ✗ {agent_name} falhou: {e}")

        elapsed = time.time() - start_time
        logger.info(f"⏱ Análise completa em {elapsed:.2f}s (paralelo, {len(results)} agentes)")

        # 4. Consolidação (Ensemble)
        final_verdict = self._consolidate(results)
        
        # Obter a primeira sugestão de pergunta disponível dos agentes
        suggested_q = next((res.get("suggested_question") for res in results if res.get("suggested_question")), None)
        
        return {
            "verdict": final_verdict["result"],
            "risk_score": final_verdict["score"],
            "agent_details": results,
            "summary": final_verdict["summary"],
            "suggested_question": suggested_q,
            "model_pref": model_pref
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
            "HTML Structural Analyzer": 0.20,
            "Vision Analysis Agent": 0.10,
            "SSL/TLS Certificate Analyzer": 0.15
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
        Gera uma explicação baseada no contexto da análise, recuperando da VectorStore via RAG.
        """
        # Pass model_pref from context if available
        response = llm_client.chat_with_rag(user_query, analysis_context)
        
        if response:
            return response
        
        return "Opa, meu motor de IA RAG local está um pouco sobrecarregado agora. Por favor, tente me perguntar novamente!"
