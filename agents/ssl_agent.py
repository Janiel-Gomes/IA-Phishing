import socket
import ssl
import logging
import time as _time
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SSLAnalysisAgent:
    def __init__(self):
        self.name = "SSL/TLS Certificate Analyzer"
        # Emissores comuns em phishing (gratuitos/automatizados)
        self.suspicious_issuers = ["Let's Encrypt", "ZeroSSL", "Cloudflare Inc", "Google Trust Services LLC"]

    def analyze(self, url, lang='PT'):
        """
        Analisa o certificado SSL/TLS do domínio.
        """
        if not url:
            return None

        parsed = urlparse(url)
        hostname = parsed.netloc.split(':')[0]
        if not hostname:
            return None

        findings = []
        score = 0.0

        try:
            # Configuração do socket e SSL
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()

            if not cert:
                return {
                    "agent": self.name,
                    "score": 0.8,
                    "result": "Phishing" if lang == 'PT' else "Phishing",
                    "findings": ["Certificado SSL não encontrado ou inválido"] if lang == 'PT' else ["SSL certificate not found or invalid"]
                }

            # --- Análise do Emissor ---
            issuer_dict = {}
            for rdn in cert.get('issuer', []):
                for attr in rdn:
                    if isinstance(attr, (list, tuple)) and len(attr) >= 2:
                        issuer_dict[attr[0]] = attr[1]
            
            common_name = issuer_dict.get('commonName', '')
            org_name = issuer_dict.get('organizationName', '')
            
            issuer_str = f"{org_name} ({common_name})" if org_name else str(common_name)
            
            is_suspicious = any(susp in issuer_str for susp in self.suspicious_issuers)
            if is_suspicious:
                score += 0.3
                msg = f"⚠️ Emissor gratuito/comum ({issuer_str})" if lang == 'PT' else f"⚠️ Free/common issuer ({issuer_str})"
                findings.append(msg)
            else:
                msg = f"✅ Emissor confiável: {issuer_str}" if lang == 'PT' else f"✅ Trusted issuer: {issuer_str}"
                findings.append(msg)

            # --- Análise de Datas ---
            not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
            not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            
            # Idade do certificado
            cert_age_days = (datetime.utcnow() - not_before).days
            if cert_age_days < 7:
                score += 0.5
                msg = f"🚨 Certificado emitido há apenas {cert_age_days} dias" if lang == 'PT' else f"🚨 Certificate issued only {cert_age_days} days ago"
                findings.append(msg)
            elif cert_age_days < 30:
                score += 0.2
                msg = f"⚠️ Certificado recente ({cert_age_days} dias)" if lang == 'PT' else f"⚠️ Recent certificate ({cert_age_days} days)"
                findings.append(msg)

            # Duração total
            duration_days = (not_after - not_before).days
            if duration_days <= 90:
                score += 0.1
                msg = f"ℹ️ Certificado de curta duração ({duration_days} dias)" if lang == 'PT' else f"ℹ️ Short-term certificate ({duration_days} days)"
                findings.append(msg)

        except socket.timeout:
            logger.warning(f"Timeout ao conectar em {hostname} para SSL")
            return None
        except Exception as e:
            logger.info(f"Falha na análise SSL para {hostname}: {e}")
            return None

        # Normalizar
        final_score = min(max(score, 0), 1.0)
        
        if lang == 'PT':
            result = "Phishing" if final_score > 0.6 else ("Suspeito" if final_score > 0.3 else "Legítima")
            suggested_q = "Como posso saber se um certificado SSL é realmente confiável?"
        else:
            result = "Phishing" if final_score > 0.6 else ("Suspect" if final_score > 0.3 else "Legit")
            suggested_q = "How can I tell if an SSL certificate is truly trustworthy?"

        return {
            "agent": self.name,
            "score": round(final_score, 3),
            "result": result,
            "findings": findings,
            "suggested_question": suggested_q
        }
