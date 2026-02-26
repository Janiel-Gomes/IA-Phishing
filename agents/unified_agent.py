import re
import logging
import requests
from bs4 import BeautifulSoup
from agents.llm_client import llm_client

logger = logging.getLogger(__name__)

# Palavras-chave típicas de phishing (para fallback heurístico)
PHISHING_KEYWORDS = [
    "urgente", "imediatamente", "expirar", "expira", "bloqueado", "suspensa",
    "suspensão", "bloqueio", "encerrar", "cancelamento", "prazo",
    "clique aqui", "acesse agora", "confirme", "verifique", "atualize",
    "sua conta", "account suspended", "unusual activity",
    "parabéns", "ganhou", "prêmio", "resgate",
    "senha", "password", "cpf", "cartão", "dados bancários"
]


class UnifiedTextHTMLAgent:
    """
    Agente unificado que analisa texto E HTML em uma única chamada LLM,
    reduzindo pela metade o tempo de resposta.
    """
    def __init__(self):
        self.name = "NLP Text Analyzer"  # Mantém o nome para compatibilidade com os pesos do orquestrador

    def _fetch_html(self, url):
        try:
            response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            return response.text
        except Exception as e:
            logger.warning(f"Não foi possível buscar HTML: {e}")
            return None

    def analyze(self, text=None, html_content=None, url=None, model_pref=None, lang='PT'):
        """
        Analisa texto + HTML em uma única chamada LLM.
        """
        # Obter HTML se não fornecido
        if not html_content and url:
            html_content = self._fetch_html(url)

        # Preparar texto para análise
        analysis_text = text or url or ""
        html_snippet = (html_content or "Não disponível")[:1500]  # Limitar HTML para caber no contexto
        analysis_url = url or "Não fornecida"

        if len(analysis_text.strip()) < 5 and not html_content:
            return {
                "agent": self.name,
                "score": 0,
                "findings": ["Dados insuficientes para análise"],
                "result": "Neutral"
            }

        # 1. Tentar análise unificada com LLM
        llm_result = llm_client.analyze("prompt_unified.txt", {
            "text": analysis_text,
            "url": analysis_url,
            "html": html_snippet,
            "lang": lang
        }, model_pref=model_pref)

        if llm_result:
            logger.info(f"{self.name}: Unified LLM analysis successful.")
            llm_result["agent"] = self.name
            return llm_result

        # 2. Fallback heurístico (combina texto + HTML)
        logger.info(f"{self.name}: Usando análise heurística (fallback).")
        score = 0.0
        findings = ["Análise heurística (fallback)"]

        # Heurística de texto
        text_lower = analysis_text.lower()
        matched = [kw for kw in PHISHING_KEYWORDS if kw in text_lower]
        if matched:
            score += min(len(matched) * 0.1, 0.5)
            findings.append(f"Palavras suspeitas: {', '.join(matched[:3])}")

        if re.search(r'https?://[^\s]+', analysis_text):
            score += 0.2
            findings.append("Contém links no texto")

        # Heurística de HTML
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            if soup.find('form'):
                score += 0.2
                findings.append("Formulário detectado no HTML")
            if soup.find('input', {'type': 'password'}):
                score += 0.15
                findings.append("Campo de senha detectado")

        score = min(score, 1.0)
        result = "Phishing" if score >= 0.5 else ("Suspeito" if score >= 0.25 else "Legítima")

        return {
            "agent": self.name,
            "score": round(score, 3),
            "result": result,
            "findings": findings,
            "suggested_question": "Como posso saber se um link é realmente perigoso?" if lang == 'PT' else "How can I tell if a link is truly dangerous?"
        }
