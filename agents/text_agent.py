import re
import logging

logger = logging.getLogger(__name__)

# Palavras-chave típicas de phishing em e-mails
PHISHING_KEYWORDS = [
    # Urgência
    "urgente", "imediatamente", "expirar", "expira", "bloqueado", "suspensa",
    "suspensão", "bloqueio", "encerrar", "cancelamento", "prazo",
    # Ação
    "clique aqui", "acesse agora", "confirme", "verifique", "atualize",
    "click here", "verify now", "confirm", "update your",
    # Ameaças
    "sua conta", "account suspended", "unusual activity", "atividade suspeita",
    "unauthorized access", "acesso não autorizado",
    # Prêmios/golpes
    "parabéns", "ganhou", "prêmio", "congratulations", "winner", "selected",
    "você foi selecionado", "resgate",
    # Financeiro
    "senha", "password", "cpf", "cartão", "credit card", "bank account",
    "dados bancários", "informações bancárias",
]

class NLPTextAgent:
    def __init__(self, model_name=None):
        self.name = "NLP Text Analyzer"
        logger.info(f"{self.name} iniciado com análise heurística.")

    def analyze(self, text):
        """
        Analisa o conteúdo textual usando heurísticas NLP sem dependências pesadas.
        """
        if not text or len(text.strip()) < 10:
            return {
                "agent": self.name,
                "score": 0,
                "findings": ["Texto insuficiente para análise NLP"],
                "result": "Neutral"
            }

        text_lower = text.lower()
        findings = []
        score = 0.0

        # 1. Palavras-chave suspeitas
        matched = [kw for kw in PHISHING_KEYWORDS if kw in text_lower]
        if matched:
            kw_score = min(len(matched) * 0.08, 0.5)
            score += kw_score
            findings.append(f"{len(matched)} palavra(s) suspeita(s): {', '.join(matched[:5])}")

        # 2. Links suspeitos no texto
        urls_in_text = re.findall(r'https?://[^\s]+', text)
        if urls_in_text:
            suspicious_urls = [u for u in urls_in_text if any(
                x in u for x in ['bit.ly', 'tinyurl', 'goo.gl', 'redirect', 'token=', 'verify']
            )]
            if suspicious_urls:
                score += 0.2
                findings.append(f"Links encurtados/suspeitos encontrados: {len(suspicious_urls)}")

        # 3. Abuso de maiúsculas (urgência)
        words = text.split()
        if words:
            caps_ratio = sum(1 for w in words if w.isupper() and len(w) > 2) / len(words)
            if caps_ratio > 0.2:
                score += 0.15
                findings.append("Uso excessivo de maiúsculas (indicador de urgência)")

        # 4. Erros ortográficos comuns de phishing (substituição de letras)
        leet_patterns = re.findall(r'[a@][c\(][e3][s\$][s\$]|[p\|][a@][s\$]{2}[w\/][o0]r[d]', text_lower)
        if leet_patterns:
            score += 0.15
            findings.append("Padrões de ofuscação de texto detectados")

        score = min(score, 1.0)

        if score >= 0.5:
            result = "Phishing"
        elif score >= 0.25:
            result = "Suspeito"
        else:
            result = "Legítima"
            if not findings:
                findings.append("Nenhum padrão suspeito detectado no texto")

        return {
            "agent": self.name,
            "score": round(score, 3),
            "result": result,
            "findings": findings if findings else ["Análise heurística concluída sem alertas"]
        }
