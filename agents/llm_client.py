import os
import json
import logging
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from typing import Optional
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from agents.rag_manager import rag_manager

# Carregar variáveis de ambiente
load_dotenv()

logger = logging.getLogger(__name__)

# Configuração Global
USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"

# Pydantic schema for Structured Output expected by all agents
class AnalysisResult(BaseModel):
    result: str = Field(description="O veredito final: 'Phishing', 'Suspeito' ou 'Legítima'")
    score: float = Field(description="A probabilidade ou score de risco entre 0.0 e 1.0", ge=0.0, le=1.0)
    summary: str = Field(description="Um breve resumo de por que esta decisão foi tomada")

class LLMClient:
    def __init__(self, ollama_model="qwen2.5:0.5b"):
        self.default_model = ollama_model
        self._prompt_cache = {}
        self._models = {} # Cache de instâncias LLM
        self.system_prompt = self._load_prompt("system_prompt.txt")

    def _get_llm(self, model_name, model_pref=None):
        """Retorna ou cria uma instância do modelo solicitado (OpenAI ou Ollama)."""
        # Se o usuário pediu explicitamente openai ou se o padrão global é openai
        is_openai = (model_pref == 'openai') or (model_pref is None and USE_OPENAI)
        model_key = "openai" if is_openai else model_name
        
        if model_key not in self._models:
            logger.info(f"Inicializando modelo: {model_key}")
            
            if is_openai:
                llm = ChatOpenAI(
                    model="gpt-4o",
                    temperature=0.0,
                    max_tokens=300
                )
            else:
                llm = ChatOllama(
                    model=model_name,
                    temperature=0.0,
                    num_ctx=2048 if "llava" in model_name else 1024,
                    num_predict=200,
                    keep_alive="1h"
                )
            
            self._models[model_key] = {
                'llm': llm,
                'structured': llm.with_structured_output(AnalysisResult)
            }
        return self._models[model_key]

    def _load_prompt(self, filename):
        """Carrega prompt do disco com cache em memória."""
        if filename in self._prompt_cache:
            return self._prompt_cache[filename]
        path = os.path.join(os.path.dirname(__file__), "..", "prompts", filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self._prompt_cache[filename] = content
            return content
        except FileNotFoundError:
            logger.error(f"Arquivo de prompt não encontrado: {path}")
            return ""

    def analyze(self, prompt_filename, template_vars, image_data=None, model_pref=None):
        """
        Executa a análise. Tenta OpenAI se configurado ou se model_pref for 'openai'.
        """
        # Se for OpenAI, usamos GPT-4o para tudo. Se for Ollama, usamos o padrão (ou llava para imagem).
        is_openai = (model_pref == 'openai') or (model_pref is None and USE_OPENAI)
        model_name = "gpt-4o" if is_openai else (self.default_model if not image_data else "llava")
        
        prompt_template = self._load_prompt(prompt_filename)
        for key, value in template_vars.items():
            prompt_template = prompt_template.replace(f"{{{{{key}}}}}", str(value))

        logger.info(f"Iniciando análise com {model_name} (Pref: {model_pref})")
        
        try:
            llm_suite = self._get_llm(model_name, model_pref=model_pref)
            
            if image_data:
                import base64
                b64_image = base64.b64encode(image_data).decode("utf-8")
                msg = [
                    ("system", self.system_prompt),
                    ("human", [
                        {"type": "text", "text": prompt_template},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                    ])
                ]
                response = llm_suite['structured'].invoke(msg)
            else:
                msg = [
                    ("system", self.system_prompt),
                    ("human", prompt_template)
                ]
                response = llm_suite['structured'].invoke(msg)

            if isinstance(response, AnalysisResult):
                return response.model_dump()
            return {"result": response.result, "score": response.score, "summary": response.summary}

        except Exception as e:
            logger.error(f"Falha na chamada ao LLM: {e}")
            return None

    def chat_with_rag(self, user_query, analysis_context):
        """
        Usa o sistema RAG para recuperar respostas sobre phishing e contexto atual
        """
        try:
            retriever = rag_manager.get_retriever(k=3)
            
            system_chat_prompt = """Você é um especialista em cibersegurança e Phishing. 
Utilize o seguinte contexto da base de dados (se houver), juntamente com a análise que acabou de ser feita na aba original.
Sua resposta deve ser explicativa, didática e direta.

Contexto da Base de Conhecimento RAG: {context}

Análise Local do Sistema:
{analysis_context}

Gere uma resposta útil baseada nesses contextos e em seu conhecimento."""
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_chat_prompt),
                ("human", "{input}")
            ])

            context_text = "Nenhuma base de conhecimento adicional disponível."
            if retriever:
                docs = retriever.invoke(user_query)
                if docs:
                    context_text = "\n---\n".join([doc.page_content for doc in docs])

            llm_suite = self._get_llm(self.default_model, model_pref=analysis_context.get('model_pref'))
            chain = prompt | llm_suite['llm']
            response = chain.invoke({
                "input": user_query, 
                "context": context_text,
                "analysis_context": json.dumps(analysis_context, indent=2, ensure_ascii=False)
            })
            
            return response.content
            
        except Exception as e:
            logger.error(f"Erro no chat: {e}")
            return "Ocorreu um erro ao conectar ao modelo para o chat."

llm_client = LLMClient()
