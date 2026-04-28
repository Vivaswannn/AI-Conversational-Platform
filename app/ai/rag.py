import logging
import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from app.config import get_settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "mental_health_kb"


class RAGEngine:
    def __init__(self):
        self._query_engine = self._build_query_engine()

    def _build_query_engine(self):
        settings = get_settings()
        embed_model = OpenAIEmbedding(
            model=settings.OPENAI_EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )

        chroma_client = chromadb.PersistentClient(path=settings.VECTOR_STORE_PATH)
        collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=collection)

        if collection.count() > 0:
            logger.info("Loading existing RAG index (%d chunks)", collection.count())
            index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
        else:
            logger.info("Building RAG index from knowledge base documents...")
            documents = SimpleDirectoryReader(settings.KNOWLEDGE_BASE_PATH).load_data()
            splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                embed_model=embed_model,
                transformations=[splitter],
            )
            logger.info("RAG index built with %d documents", len(documents))

        return index.as_query_engine(similarity_top_k=3, embed_model=embed_model)

    def query(self, user_message: str) -> list[str]:
        """Return top-k relevant text chunks for the given user message."""
        try:
            response = self._query_engine.query(user_message)
            return [node.node.text for node in response.source_nodes]
        except Exception:
            logger.exception("RAG query failed; returning empty context")
            return []


_rag_engine: RAGEngine | None = None


def get_rag_engine() -> RAGEngine:
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine
