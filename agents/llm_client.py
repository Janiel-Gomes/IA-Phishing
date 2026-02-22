import os
import json
import logging
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

logger = logging.getLogger(__name__)

# Configurar API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY não encontrada. Suporte ao Gemini desativado.")

class LLMClient:
    def __init__(self, gemini_model="gemini-1.5-flash", openai_model="gpt-4o-mini-2024-07-18"):
        self.gemini_model_name = gemini_model
        self.openai_model_name = openai_model
        self.system_prompt = self._load_prompt("system_prompt.txt")
        
        # Inicializar modelo Gemini se a chave existir
        self.gemini_model = None
        if GEMINI_API_KEY:
            try:
                self.gemini_model = genai.GenerativeModel(
                    model_name=self.gemini_model_name,
                    system_instruction=self.system_prompt
                )
            except Exception as e:
                logger.error(f"Erro ao inicializar Gemini: {e}")

    def _load_prompt(self, filename):
        path = os.path.join(os.path.dirname(__file__), "..", "prompts", filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Arquivo de prompt não encontrado: {path}")
            return ""

    def analyze(self, prompt_filename, template_vars, image_data=None):
        """
        Executa a análise com prioridade para OpenAI (GPT).
        Fallback: OpenAI -> Gemini -> Groq.
        """
        prompt_template = self._load_prompt(prompt_filename)
        for key, value in template_vars.items():
            prompt_template = prompt_template.replace(f"{{{{{key}}}}}", str(value))

        # 1. Tentar OpenAI (Solicitação expressa do usuário)
        if OPENAI_API_KEY:
            result = self._analyze_openai(prompt_template, image_data)
            if result: return result

        # 2. Tentar Gemini como fallback
        if self.gemini_model:
            result = self._analyze_gemini(prompt_template, image_data)
            if result: return result

        # 3. Tentar Groq (Llama-3) se Gemini falhar
        if GROQ_API_KEY:
            result = self._analyze_groq(prompt_template)
            if result: return result

        logger.error("Nenhuma API Key válida (OpenAI/Gemini/Groq) disponível para análise.")
        return None

    def _analyze_gemini(self, prompt, image_data=None):
        try:
            content = []
            if image_data:
                # Gemini 1.5 Flash suporta imagem via bytes
                content.append({"mime_type": "image/jpeg", "data": image_data})
            content.append(prompt)
            
            response = self.gemini_model.generate_content(
                content,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.0
                )
            )
            return self._parse_json_response(response.text)
        except Exception as e:
            logger.error(f"Falha na chamada ao Gemini: {e}")
            return None

    def _analyze_groq(self, prompt):
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-70b-versatile",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"}
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return self._parse_json_response(result['choices'][0]['message']['content'])
        except Exception as e:
            logger.error(f"Falha na chamada ao Groq: {e}")
        return None

    def _analyze_openai(self, prompt, image_data=None):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        messages = [{"role": "system", "content": self.system_prompt}]
        user_content = [{"type": "text", "text": prompt}]
        
        if image_data:
            import base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })
            
        messages.append({"role": "user", "content": user_content})

        data = {
            "model": self.openai_model_name,
            "messages": messages,
            "temperature": 0.0,
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return self._parse_json_response(result['choices'][0]['message']['content'])
        except Exception as e:
            logger.error(f"Falha na chamada ao OpenAI: {e}")
        return None

    def _parse_json_response(self, text):
        try:
            text = text.strip()
            if text.startswith("```json"):
                text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            logger.error(f"Erro ao parsear JSON LLM: {e}")
            return None

llm_client = LLMClient()
