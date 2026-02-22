import re
import logging
from agents.llm_client import llm_client

logger = logging.getLogger(__name__)

# Palavras-chave típicas de phishing em e-mails (Mantido para fallback)
PHISHING_KEYWORDS = [
    "urgente", "imediatamente", "expirar", "expira", "bloqueado", "suspensa",
    "suspensão", "bloqueio", "encerrar", "cancelamento", "prazo",
    "clique aqui", "acesse agora", "confirme", "verifique", "atualize",
    "sua conta", "account suspended", "unusual activity",
    "parabéns", "ganhou", "prêmio", "resgate",
    "senha", "password", "cpf", "cartão", "dados bancários"
]

class NLPTextAgent:
    def __init__(self, model_name=None):
        self.name = "NLP Text Analyzer"
        logger.info(f"{self.name} iniciado.")

    def analyze(self, text):
        """
        Analisa o conteúdo textual usando LLM com fallback para heurística.
        """
        if not text or len(text.strip()) < 10:
            return {
                "agent": self.name,
                "score": 0,
                "findings": ["Texto insuficiente para análise"],
                "result": "Neutral"
            }

        # 1. Tentar análise com LLM
        llm_result = llm_client.analyze("prompt_text.txt", {"text": text})
        if llm_result:
            logger.info(f"{self.name}: LLM analysis successful.")
            llm_result["agent"] = self.name
            return llm_result

        # 2. Fallback para heurística se LLM falhar ou não estiver configurado
        logger.info(f"{self.name}: Usando análise heurística (fallback).")
        text_lower = text.lower()
        findings = ["Análise heurística (fallback)"]
        score = 0.0

        matched = [kw for kw in PHISHING_KEYWORDS if kw in text_lower]
        if matched:
            score += min(len(matched) * 0.1, 0.5)
            findings.append(f"Palavras suspeitas: {', '.join(matched[:3])}")

        if re.search(r'https?://[^\s]+', text):
            score += 0.2
            findings.append("Contém links no texto")

        score = min(score, 1.0)
        result = "Phishing" if score >= 0.5 else ("Suspeito" if score >= 0.25 else "Legítima")

        return {
            "agent": self.name,
            "score": round(score, 3),
            "result": result,
            "findings": findings
        }
