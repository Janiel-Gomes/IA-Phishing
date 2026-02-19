import re
from urllib.parse import urlparse

class URLLexicalAgent:
    def __init__(self):
        self.name = "URL Lexical Analyzer"

    def analyze(self, url):
        """
        Analisa a URL em busca de padrões lexicais suspeitos.
        """
        if not url:
            return {"score": 0, "findings": ["URL não fornecida"], "result": "Neutral"}

        parsed = urlparse(url)
        netloc = parsed.netloc
        path = parsed.path
        
        score = 0
        findings = []

        # 1. Verificar IPs em vez de nomes de domínio
        ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        if re.match(ip_pattern, netloc):
            score += 0.8
            findings.append("Uso de endereço IP em vez de domínio")

        # 2. Comprimento da URL
        if len(url) > 75:
            score += 0.3
            findings.append("URL excessivamente longa")

        # 3. Número de pontos no domínio (subdomínios excessivos)
        dot_count = netloc.count('.')
        if dot_count > 3:
            score += 0.4
            findings.append(f"Número elevado de subdomínios ({dot_count})")

        # 4. Presença de caracteres suspeitos (@ ou hífens excessivos)
        if "@" in url:
            score += 0.7
            findings.append("Uso de símbolo '@' (frequentemente usado para mascarar URLs)")
        
        if netloc.count('-') > 2:
            score += 0.2
            findings.append("Muitos hífens no domínio")

        # 5. Palavras-chave suspeitas no domínio ou path
        suspicious_keywords = ["login", "verify", "update", "secure", "account", "bank", "pay", "paypal", "signin"]
        found_keywords = [kw for kw in suspicious_keywords if kw in url.lower()]
        if found_keywords:
            score += 0.2 * len(found_keywords)
            findings.append(f"Palavras-chave suspeitas encontradas: {', '.join(found_keywords)}")

        # Normalizar score (cap em 1.0)
        final_score = min(max(score, 0), 1.0)
        result = "Phishing" if final_score > 0.5 else "Legítima"

        return {
            "agent": self.name,
            "score": final_score,
            "result": result,
            "findings": findings
        }
