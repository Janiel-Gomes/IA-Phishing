from bs4 import BeautifulSoup
import requests
import logging

logger = logging.getLogger(__name__)

class HTMLStructuralAgent:
    def __init__(self):
        self.name = "HTML Structural Analyzer"

    def _fetch_html(self, url):
        try:
            # Tentar buscar a página com um timeout curto
            response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            return response.text
        except Exception as e:
            logger.warning(f"Não foi possível buscar HTML da URL {url}: {e}")
            return None

    def analyze(self, html_content=None, url=None):
        """
        Analisa a estrutura do HTML em busca de anomalias comuns em phishing.
        Pode receber o HTML diretamente ou uma URL para tentar buscar.
        """
        if not html_content and url:
            html_content = self._fetch_html(url)

        if not html_content:
            return {"agent": self.name, "score": 0, "findings": ["HTML não disponível para análise"], "result": "Neutral"}

        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            score = 0
            findings = []

            # 1. Verificar campos de senha em sites sem HTTPS (se tivermos a URL)
            if url and not url.startswith('https'):
                if soup.find('input', {'type': 'password'}):
                    score += 0.8
                    findings.append("Campo de senha encontrado em conexão não segura (HTTP)")

            # 2. Verificar formulários que apontam para domínios diferentes
            forms = soup.find_all('form')
            for form in forms:
                action = form.get('action', '').lower()
                if action.startswith('http') and url:
                    from urllib.parse import urlparse
                    action_domain = urlparse(action).netloc
                    current_domain = urlparse(url).netloc
                    if action_domain != current_domain:
                        score += 0.5
                        findings.append(f"Formulário enviando dados para domínio externo: {action_domain}")

            # 3. Presença de tags estranhas ou ocultas
            hidden_elements = soup.find_all(style=lambda value: value and ('display:none' in value.replace(' ', '') or 'visibility:hidden' in value.replace(' ', '')))
            if len(hidden_elements) > 5:
                score += 0.2
                findings.append("Muitos elementos ocultos detectados (possível tentativa de ofuscação)")

            # 4. Links externos massivos (muitos links apontando para fora)
            links = soup.find_all('a', href=True)
            if len(links) > 0:
                external_links = [l for l in links if l['href'].startswith('http')]
                if len(external_links) / len(links) > 0.8:
                    score += 0.3
                    findings.append("Alta proporção de links externos")

            # Normalizar score
            final_score = min(max(score, 0), 1.0)
            result = "Phishing" if final_score > 0.4 else "Legítima"

            return {
                "agent": self.name,
                "score": final_score,
                "result": result,
                "findings": findings
            }
        except Exception as e:
            logger.error(f"Erro na análise do HTMLStructuralAgent: {e}")
            return {"agent": self.name, "score": 0, "findings": [f"Erro ao processar HTML: {str(e)}"], "result": "Error"}
