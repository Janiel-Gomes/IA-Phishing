from bs4 import BeautifulSoup
import requests
import logging
from agents.llm_client import llm_client

logger = logging.getLogger(__name__)

class HTMLStructuralAgent:
    def __init__(self):
        self.name = "HTML Structural Analyzer"

    def _fetch_html(self, url):
        try:
            response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            return response.text
        except Exception as e:
            logger.warning(f"Não foi possível buscar HTML: {e}")
            return None

    def analyze(self, html_content=None, url=None):
        """
        Analisa a estrutura do HTML usando LLM com fallback para heurística.
        """
        if not html_content and url:
            html_content = self._fetch_html(url)

        if not html_content:
            return {"agent": self.name, "score": 0, "findings": ["HTML indisponível"], "result": "Neutral"}

        # Limitar tamanho do HTML para o prompt
        snippet = html_content[:5000]

        # 1. Tentar análise com LLM
        llm_result = llm_client.analyze("prompt_html.txt", {"url": url or "Desconhecida", "html": snippet})
        if llm_result:
            logger.info(f"{self.name}: LLM analysis successful.")
            llm_result["agent"] = self.name
            return llm_result

        # 2. Fallback Heurístico
        logger.info(f"{self.name}: Usando fallback heurístico.")
        soup = BeautifulSoup(html_content, 'html.parser')
        score = 0.1
        findings = ["Análise heurística básica (fallback)"]
        
        if soup.find('form'):
            score += 0.2
            findings.append("Formulário detectado")
        
        return {
            "agent": self.name,
            "score": score,
            "result": "Suspeito" if score > 0.4 else "Legítima",
            "findings": findings
        }
