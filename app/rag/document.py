import os
import logging
from uuid import UUID
from typing import List

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag.vector_db import ingest_documents

logger = logging.getLogger(__name__)

async def process_industrial_manual(file_path: str, factory_id: UUID, equipment_category: str) -> bool:
    """
    Asynchronously loads a PDF manual, splits it into semantic chunks,
    injects tenant metadata, and securely routes it to the vector database.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False

    try:
        logger.info(f"Loading industrial manual via PyMuPDF: {file_path}")
        
        loader = PyMuPDFLoader(file_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)

        # Strict Multi-Tenant Metadata Injection
        for chunk in chunks:
            chunk.metadata["factory_id"] = str(factory_id)
            chunk.metadata["equipment_category"] = equipment_category
            chunk.metadata["source"] = os.path.basename(file_path)

        logger.info(f"Successfully processed {len(chunks)} embedded chunks. Ingesting...")

        # Secure Async Database Insertion
        success = await ingest_documents(factory_id, chunks)
        return success

    except Exception as e:
        logger.error(f"Fatal error processing manual {file_path}: {str(e)}")
        return False