from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

class NLPTextAgent:
    def __init__(self, model_name="ealvaradob/bert-finetuned-phishing"):
        self.name = "NLP Text Analyzer"
        self.model_name = model_name
        self.pipe = self._load_model()

    def _load_model(self):
        try:
            logger.info(f"Carregando modelo para {self.name}: {self.model_name}...")
            pipe = pipeline("text-classification", model=self.model_name)
            logger.info(f"Modelo {self.model_name} carregado com sucesso.")
            return pipe
        except Exception as e:
            logger.error(f"Erro ao carregar o modelo NLP: {e}")
            return None

    def analyze(self, text):
        """
        Analisa o conteúdo textual (e-mail ou corpo da página) usando NLP.
        """
        if not text or len(text.strip()) < 10:
            return {"agent": self.name, "score": 0, "findings": ["Texto insuficiente para análise NLP"], "result": "Neutral"}

        if self.pipe is None:
            return {"agent": self.name, "score": 0, "findings": ["Modelo NLP não disponível"], "result": "Error"}

        try:
            # Predição usando a pipeline do Transformers
            # Nota: truncamos o texto para o limite do modelo (geralmente 512 tokens)
            prediction = self.pipe(text[:512])[0]
            
            label = prediction['label'].lower()
            confidence = prediction['score']
            
            # Mapeamento (depende do modelo, mas geralmente LABEL_1 ou 'phishing')
            is_phishing = "phishing" in label or "1" in label
            result = "Phishing" if is_phishing else "Legítima"
            
            # Ajustamos o score para ser positivo para phishing
            score = confidence if is_phishing else (1 - confidence)

            return {
                "agent": self.name,
                "score": float(score),
                "result": result,
                "findings": [f"Confiança do modelo ({self.model_name}): {confidence:.2%}"]
            }
        except Exception as e:
            logger.error(f"Erro na análise do NLPTextAgent: {e}")
            return {"agent": self.name, "score": 0, "findings": [f"Erro interno: {str(e)}"], "result": "Error"}
