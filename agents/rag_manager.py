import os
import logging
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

logger = logging.getLogger(__name__)

class RAGManager:
    def __init__(self, persist_directory="./chroma_db", data_directory="knowledge_base"):
        self.persist_directory = persist_directory
        self.data_directory = os.path.join(os.path.dirname(__file__), "..", data_directory)
        
        # Use a lightweight embedding model from Ollama, like nomic-embed-text (or just use sentence-transformers if preferred)
        # Using sentence-transformers for local fast embeddings without needing another ollama model explicitly
        from langchain_community.embeddings import HuggingFaceEmbeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = None
        self._initialize_vectorstore()

    def _initialize_vectorstore(self):
        try:
            if not os.path.exists(self.data_directory):
                os.makedirs(self.data_directory)
                logger.info(f"Pasta {self.data_directory} criada. Adicione arquivos para RAG aqui.")
            
            # Checar se já existe um BD Chroma persistido com dados
            if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
                logger.info("Carregando VectorStore existente...")
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
            else:
                logger.info("Criando nova VectorStore vazia...")
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                self.ingest_documents()
        except Exception as e:
            logger.error(f"Erro ao inicializar RAG: {e}")

    def ingest_documents(self):
        """Lê documentos da pasta knowledge_base e os indexa no ChromaDB"""
        try:
            loader = DirectoryLoader(self.data_directory, glob="**/*.txt", show_progress=True)
            documents = loader.load()
            
            if not documents:
                logger.info("Nenhum documento encontrado para ingestão no RAG.")
                return

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = text_splitter.split_documents(documents)
            
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            logger.info(f"{len(chunks)} chunks de texto indexados com sucesso no ChromaDB.")
        except Exception as e:
            logger.error(f"Erro na ingestão de documentos: {e}")

    def get_retriever(self, k=3):
        if self.vectorstore:
            return self.vectorstore.as_retriever(search_kwargs={"k": k})
        return None

rag_manager = RAGManager()
