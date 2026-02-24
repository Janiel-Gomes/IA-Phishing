import re
import logging
import time as _time
from urllib.parse import urlparse
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Tenta importar whois — graceful fallback se não disponível
try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False
    logger.warning("python-whois não instalado. Análise WHOIS desativada.")

# Cache WHOIS com TTL de 1 hora (evita lookups repetidos)
_whois_cache = {}
_WHOIS_CACHE_TTL = 3600


class URLLexicalAgent:
    def __init__(self):
        self.name = "URL Lexical Analyzer"

    def _whois_analysis(self, domain):
        """
        Consulta WHOIS para verificar idade e dados do domínio.
        Retorna (score_adicional, findings_adicionais).
        Usa cache com TTL de 1h para evitar lookups repetidos.
        """
        # Verificar cache primeiro
        if domain in _whois_cache:
            cached_time, cached_result = _whois_cache[domain]
            if _time.time() - cached_time < _WHOIS_CACHE_TTL:
                logger.info(f"WHOIS cache hit para {domain}")
                return cached_result

        findings = []
        score = 0.0

        if not WHOIS_AVAILABLE:
            return score, findings

        try:
            w = whois.whois(domain)

            # --- Idade do domínio ---
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]

            if creation_date:
                if creation_date.tzinfo is None:
                    creation_date = creation_date.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                age_days = (now - creation_date).days

                if age_days < 30:
                    score += 0.5
                    findings.append(f"⚠️ Domínio extremamente recente ({age_days} dias) — alto risco")
                elif age_days < 180:
                    score += 0.3
                    findings.append(f"⚠️ Domínio recente ({age_days} dias)")
                elif age_days < 365:
                    score += 0.1
                    findings.append(f"Domínio criado há {age_days} dias (menos de 1 ano)")
                else:
                    years = age_days // 365
                    findings.append(f"✅ Domínio estabelecido há {years} ano(s)")

            # --- Expiração próxima ---
            expiration_date = w.expiration_date
            if isinstance(expiration_date, list):
                expiration_date = expiration_date[0]

            if expiration_date:
                if expiration_date.tzinfo is None:
                    expiration_date = expiration_date.replace(tzinfo=timezone.utc)
                days_to_expire = (expiration_date - datetime.now(timezone.utc)).days
                if 0 < days_to_expire < 60:
                    score += 0.2
                    findings.append(f"⚠️ Domínio expira em {days_to_expire} dias")

            # --- Registrador ---
            registrar = w.registrar
            if registrar:
                findings.append(f"Registrador: {registrar}")

            # --- País do registrante ---
            country = w.country
            if country:
                findings.append(f"País do registrante: {country}")

        except Exception as e:
            logger.info(f"WHOIS indisponível para {domain}: {e}")
            findings.append("Informações WHOIS não disponíveis para este domínio")

        result = (min(score, 0.6), findings)
        # Salvar no cache
        _whois_cache[domain] = (_time.time(), result)
        return result

    def analyze(self, url):
        """
        Analisa a URL em busca de padrões lexicais suspeitos + dados WHOIS.
        """
        if not url:
            return {"agent": self.name, "score": 0, "findings": ["URL não fornecida"], "result": "Neutral"}

        parsed = urlparse(url)
        netloc = parsed.netloc.split(':')[0]  # remove porta se houver
        path = parsed.path

        score = 0.0
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

        # 3. Número de pontos (subdomínios excessivos)
        dot_count = netloc.count('.')
        if dot_count > 3:
            score += 0.4
            findings.append(f"Número elevado de subdomínios ({dot_count})")

        # 4. Caracteres suspeitos
        if "@" in url:
            score += 0.7
            findings.append("Uso de símbolo '@' (frequentemente usado para mascarar URLs)")

        if netloc.count('-') > 2:
            score += 0.2
            findings.append("Muitos hífens no domínio")

        # 5. Palavras-chave suspeitas
        suspicious_keywords = ["login", "verify", "update", "secure", "account", "bank",
                                "pay", "paypal", "signin", "password", "credential"]
        found_keywords = [kw for kw in suspicious_keywords if kw in url.lower()]
        if found_keywords:
            score += 0.2 * len(found_keywords)
            findings.append(f"Palavras-chave suspeitas: {', '.join(found_keywords)}")

        # 6. Protocolo HTTP (sem HTTPS)
        if parsed.scheme == 'http':
            score += 0.15
            findings.append("Conexão não segura (HTTP sem SSL)")

        # 7. WHOIS — idade e dados do domínio
        if netloc and not re.match(ip_pattern, netloc):
            # Extrair domínio raiz (ex: sub.exemplo.com → exemplo.com)
            domain_parts = netloc.split('.')
            root_domain = '.'.join(domain_parts[-2:]) if len(domain_parts) >= 2 else netloc
            whois_score, whois_findings = self._whois_analysis(root_domain)
            score += whois_score
            findings.extend(whois_findings)

        # Normalizar score
        final_score = min(max(score, 0), 1.0)

        if final_score >= 0.5:
            result = "Phishing"
        elif final_score >= 0.25:
            result = "Suspeito"
        else:
            result = "Legítima"

        if not findings:
            findings.append("Nenhum padrão suspeito detectado na URL")

        return {
            "agent": self.name,
            "score": round(final_score, 3),
            "result": result,
            "findings": findings
        }
