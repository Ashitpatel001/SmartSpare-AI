import logging
from uuid import UUID
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Lazy-loaded globals — these are initialized on first use, not at import time.
# This prevents the entire intelligence module from crashing if Docker/ChromaDB is offline.
_chroma_client = None
_chroma_initialized = False
_embedding_function = None


def _get_embedding_function():
    """Lazy-load the embedding model on first use."""
    global _embedding_function
    if _embedding_function is None:
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            _embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            logger.info("HuggingFace embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
    return _embedding_function


def _get_chroma_client():
    """Lazy-connect to ChromaDB on first use. Returns None if unavailable."""
    global _chroma_client, _chroma_initialized
    
    if _chroma_initialized:
        return _chroma_client
    
    _chroma_initialized = True  # Only attempt once
    
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        
        _chroma_client = chromadb.HttpClient(
            host="localhost",
            port=8001,
            settings=ChromaSettings(allow_reset=False)
        )
        _chroma_client.heartbeat()
        logger.info("Successfully connected to Dockerized ChromaDB.")
    except Exception as e:
        logger.warning(f"ChromaDB is offline (Docker may not be running). RAG features disabled. Error: {e}")
        _chroma_client = None
    
    return _chroma_client


# Multi-Tenant Vector Store Manager
def get_factory_vector_store(factory_id: UUID):
    """
    Retrieves or creates a specific ChromaDB collection for a given factory.
    This guarantees that Vector searches never cross-pollinate tenant data.
    Returns None if ChromaDB is unavailable.
    """
    client = _get_chroma_client()
    embeddings = _get_embedding_function()
    
    if not client or not embeddings:
        logger.warning("ChromaDB or embeddings unavailable. Vector store cannot be created.")
        return None
        
    try:
        from langchain_chroma import Chroma
        
        collection_name = f"factory_{str(factory_id).replace('-', '_')}"
        
        return Chroma(
            client=client,
            collection_name=collection_name,
            embedding_function=embeddings
        )
    except Exception as e:
        logger.error(f"Failed to create vector store for factory {factory_id}: {e}")
        return None


# Asynchronous Document Ingestion
async def ingest_documents(factory_id: UUID, documents: list) -> bool:
    """
    Takes chunked documents (from PDFs or OCR) and embeds them into the factory's vector index.
    """
    try:
        vector_store = get_factory_vector_store(factory_id)
        if not vector_store:
            return False
        
        vector_store.add_documents(documents=documents)
        logger.info(f"Successfully ingested {len(documents)} chunks for factory {factory_id}")
        return True
    except Exception as e:
        logger.error(f"Vector ingestion failed for factory {factory_id}: {str(e)}")
        return False


# Semantic Search Engine
async def search_industrial_manuals(factory_id: UUID, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Performs a semantic similarity search against the factory's manuals.
    Returns the top K most relevant text chunks along with their source metadata.
    Returns empty list gracefully if ChromaDB is offline.
    """
    try:
        vector_store = get_factory_vector_store(factory_id)
        if not vector_store:
            logger.info("Vector store unavailable. Returning empty results for manual search.")
            return []
        
        results = vector_store.similarity_search_with_score(query, k=top_k)
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "relevance_score": score
            })
            
        return formatted_results
    except Exception as e:
        logger.error(f"Vector search failed for factory {factory_id}: {str(e)}")
        return []