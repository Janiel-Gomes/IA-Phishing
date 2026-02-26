import logging
from agents.llm_client import llm_client

logger = logging.getLogger(__name__)

class VisionAgent:
    def __init__(self):
        self.name = "Vision Analysis Agent"

    def analyze(self, image_data=None, image_path=None, model_pref=None, lang='PT'):
        """
        Analisa uma imagem em busca de padrões de phishing usando LLM Vision.
        """
        if not image_data:
            return {
                "agent": self.name, "score": 0, "result": "Neutral",
                "findings": ["Nenhuma imagem fornecida."]
            }

        # 1. Tentar análise com LLM Vision
        llm_result = llm_client.analyze("prompt_vision.txt", {"lang": lang}, image_data=image_data, model_pref=model_pref)
        if llm_result:
            logger.info(f"{self.name}: Vision analysis successful.")
            llm_result["agent"] = self.name
            return llm_result

        # 2. Fallback
        return {
            "agent": self.name,
            "score": 0.1,
            "result": "Legítima",
            "findings": ["Análise visual indisponível (usando modo básico)."]
        }
