import fitz  # PyMuPDF
import json
import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

# LangChain & Groq Imports
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from app.core.database import get_db
from app.models.inventory import SparePart
from app.models.tenant import Factory
from app.core.config import settings

router = APIRouter()

# --- 1. Define the AI Extraction Schemas ---
class ExtractedPart(BaseModel):
    sku: str = Field(description="The unique model number or SKU of the part")
    name: str = Field(description="The descriptive name of the part")
    quantity: int = Field(description="The exact quantity in stock. Default to 0 if not found.")
    category: str = Field(description="The general category (e.g., Motors, Mechanical, Electronics, Conveyors)")

class PartCreate(BaseModel):
    name: str = Field(..., description="Name of the part")
    sku: Optional[str] = Field(None, description="SKU or Model Number")
    current_stock: int = Field(0, description="Exact quantity in stock")
    minimum_threshold: Optional[int] = Field(5, description="Low stock warning level")
    category: Optional[str] = Field(None, description="General category")
    location_bin: Optional[str] = Field(None, description="Warehouse location")
    
class InventoryExtraction(BaseModel):
    parts: List[ExtractedPart]

class PartUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Updated name of the part")
    quantity: Optional[int] = Field(None, description="Updated stock quantity")
    category: Optional[str] = Field(None, description="Updated category")
    location_bin: Optional[str] = Field(None, description="Updated warehouse location")

# --- 2. The Standard List Endpoint (READ) ---
@router.get("/parts", tags=["Warehouse & Inventory Operations"])
async def list_spare_parts(db: AsyncSession = Depends(get_db)):
    """Fetches all spare parts from the PostgreSQL database."""
    result = await db.execute(select(SparePart))
    parts = result.scalars().all()
    return {"status": "success", "count": len(parts), "data": parts}

# --- 3. The Modification Endpoint (UPDATE) ---
@router.put("/parts/{part_id}", tags=["Warehouse & Inventory Operations"])
async def update_spare_part(
    part_id: uuid.UUID,
    update_data: PartUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Allows a user to manually modify any field of an existing spare part."""
    result = await db.execute(select(SparePart).where(SparePart.id == part_id))
    part = result.scalar_one_or_none()

    if not part:
        raise HTTPException(status_code=404, detail="Spare part not found.")

    if update_data.name is not None:
        part.name = update_data.name
    if update_data.quantity is not None:
        part.current_stock = update_data.quantity
    if update_data.category is not None:
        part.category = update_data.category
    if update_data.location_bin is not None:
        part.location_bin = update_data.location_bin

    await db.commit()
    await db.refresh(part)
    
    return {
        "status": "success", 
        "message": f"Part {part.sku} successfully updated.",
        "data": part
    }

# --- 4. The AI PDF Ingestion Endpoint (CREATE) ---
@router.post("/parts/upload", tags=["Warehouse & Inventory Operations"])
async def upload_inventory_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Accepts a PDF inventory list, extracts the raw text in memory, 
    uses Llama 3 to structure the data, and saves it to PostgreSQL.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    try:
        # Step A: Read the PDF directly from memory
        pdf_bytes = await file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        raw_text = ""
        for page in doc:
            raw_text += page.get_text()
            
        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract any text from the PDF.")

        # Step B: Initialize the Groq Llama 3 Model
        llm = ChatGroq(
            temperature=0, 
            model_name="llama-3.3-70b-versatile", 
            api_key=settings.GROQ_API_KEY
        )
        structured_llm = llm.with_structured_output(InventoryExtraction)

        # Step C: Prompt the AI
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert industrial data extraction agent. Extract all spare parts from the provided raw text. Ignore unrelated text, headers, and footers."),
            ("human", "Extract the inventory data from this messy PDF text:\n\n{text}")
        ])
        
        chain = prompt | structured_llm
        
        print("Sending raw text to Llama 3 for structured extraction...")
        extraction_result = await chain.ainvoke({"text": raw_text})
        
        # Step D: Save the Extracted Data to PostgreSQL
        factory_result = await db.execute(select(Factory).limit(1))
        target_factory = factory_result.scalar_one_or_none()
        
        if not target_factory:
            raise HTTPException(status_code=400, detail="No factory exists in the database to assign these parts to. Please run the seed script.")

        new_parts = []
        for part_data in extraction_result.parts:
            new_part = SparePart(
                factory_id=target_factory.id,
                sku=part_data.sku,
                name=part_data.name,
                current_stock=part_data.quantity,
                category=part_data.category,
                minimum_threshold=5, 
                location_bin="Unassigned Upload"
            )
            db.add(new_part)
            new_parts.append(new_part)

        await db.commit()

        return {
            "status": "success", 
            "message": f"AI successfully extracted and saved {len(new_parts)} parts.",
            "data": [p.name for p in new_parts]
        }
        

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Extraction pipeline failed: {str(e)}")
    

@router.post("/parts", tags=["Warehouse & Inventory Operations"])
async def create_spare_part(
    part_data: PartCreate,
    db: AsyncSession = Depends(get_db)
):
    """Allows a user to manually create a new spare part."""
    
    # We must assign the part to the active factory
    factory_result = await db.execute(select(Factory).limit(1))
    target_factory = factory_result.scalar_one_or_none()
    
    if not target_factory:
        raise HTTPException(status_code=400, detail="No factory exists. Please run the seed script.")

    new_part = SparePart(
        factory_id=target_factory.id,
        sku=part_data.sku,
        name=part_data.name,
        current_stock=part_data.current_stock,
        minimum_threshold=part_data.minimum_threshold,
        location_bin=part_data.location_bin,
        category=part_data.category
    )
    
    db.add(new_part)
    await db.commit()
    await db.refresh(new_part)
    
    return {
        "status": "success", 
        "message": f"Part {new_part.name} successfully created.",
        "data": new_part
    }
    

@router.delete("/parts/{part_id}", tags=["Warehouse & Inventory Operations"])
async def delete_spare_part(part_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Deletes a spare part from the database."""
    result = await db.execute(select(SparePart).where(SparePart.id == part_id))
    part = result.scalar_one_or_none()

    if not part:
        raise HTTPException(status_code=404, detail="Spare part not found.")

    await db.delete(part)
    await db.commit()
    
    return {
        "status": "success", 
        "message": f"Part {part.sku} successfully deleted."
    } 