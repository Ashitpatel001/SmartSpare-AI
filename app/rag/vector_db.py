import logging
from uuid import UUID
from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma  # Upgraded from langchain_community
from langchain_huggingface import HuggingFaceEmbeddings  # Swapped from OpenAI
from langchain_core.documents import Document

from app.core.config import settings

logger = logging.getLogger(__name__)

embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

try:
    chroma_client = chromadb.HttpClient(
        host="localhost", # Use localhost since Python is running outside Docker right now
        port=8000,
        settings=ChromaSettings(allow_reset=False)
    )
    logger.info("Successfully connected to Dockerized ChromaDB.")
except Exception as e:
    logger.error(f"Failed to connect to ChromaDB container. Is Docker running? Error: {e}")
    chroma_client = None


# Multi-Tenant Vector Store Manager
def get_factory_vector_store(factory_id: UUID) -> Chroma | None:
    """
    Retrieves or creates a specific ChromaDB collection for a given factory.
    This guarantees that Vector searches never cross-pollinate tenant data.
    """
    if not chroma_client:
        logger.error("ChromaDB client is offline.")
        return None
        
    collection_name = f"factory_{str(factory_id).replace('-', '_')}"
    
    return Chroma(
        client=chroma_client,
        collection_name=collection_name,
        embedding_function=embedding_function
    )

# Asynchronous Document Ingestion
async def ingest_documents(factory_id: UUID, documents: List[Document]) -> bool:
    """
    Takes chunked documents (from PDFs or OCR) and embeds them into the factory's vector index.
    """
    try:
        vector_store = get_factory_vector_store(factory_id)
        if not vector_store:
            return False
        
        # In actual deployment, consider running this in a background executor
        vector_store.add_documents(documents=documents)
        logger.info(f"Successfully ingested {len(documents)} chunks for factory {factory_id}")
        return True
    except Exception as e:
        logger.error(f"Vector ingestion failed for factory {factory_id}: {str(e)}")
        return False


# 5. Semantic Search Engine
async def search_industrial_manuals(factory_id: UUID, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Performs a semantic similarity search against the factory's manuals.
    Returns the top K most relevant text chunks along with their source metadata.
    """
    try:
        vector_store = get_factory_vector_store(factory_id)
        if not vector_store:
            return []
        
        # Execute a similarity search returning both the document and the relevance score
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