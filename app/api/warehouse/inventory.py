import fitz  # PyMuPDF
import json
import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, Field

# LangChain & Groq Imports
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.models.inventory import SparePart
from app.core.database import get_db
from app.models.tenant import Factory
from app.core.config import settings

router = APIRouter()

# AI Extraction Schemas
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

# The Standard List Endpoint
@router.get("/parts", tags=["Warehouse & Inventory Operations"])
async def list_spare_parts(db: AsyncSession = Depends(get_db)):
    """Fetches all spare parts from the PostgreSQL database."""
    result = await db.execute(select(SparePart))
    parts = result.scalars().all()
    return {"status": "success", "count": len(parts), "data": parts}

# The Modification Endpoint (UPDATE)
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

# PDF Upload & AI Extraction Endpoint (SMART UPSERT)
@router.post("/parts/upload", tags=["Warehouse & Inventory Operations"])
async def upload_inventory_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Accepts a PDF inventory list, extracts the raw text in memory, 
    uses Llama 3 to structure the data, and UPSERTS it to PostgreSQL.
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
        
        # Step C: Prompt the AI (Added hyper-strict instructions to prevent hallucination)
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a strictly constrained data extraction script. 
Your ONLY function is to convert the user's raw text into a structured JSON array.
CRITICAL RULES:
1. ONLY extract the exact parts explicitly written in the text.
2. DO NOT invent, guess, or hallucinate ANY parts. 
3. DO NOT generate sequential parts like "Industrial Part 6", "Industrial Part 7", etc.
4. If the text has exactly 5 items, your JSON array MUST contain exactly 5 items.
"""),
            ("human", "Extract the exact inventory data from this raw PDF text:\n\n{text}")
        ])
        
        chain = prompt | structured_llm
        
        print("Sending raw text to Llama 3 for structured extraction...")
        extraction_result = await chain.ainvoke({"text": raw_text})
        
        # Step D: SMART UPSERT — Update existing parts, create new ones
        factory_result = await db.execute(select(Factory).limit(1))
        target_factory = factory_result.scalar_one_or_none()
        
        if not target_factory:
            raise HTTPException(status_code=400, detail="No factory exists in the database. Please register a user first to auto-create a factory.")

        # Pre-fetch all existing parts for this factory to avoid N+1 queries and handle session state
        existing_parts_result = await db.execute(
            select(SparePart).where(SparePart.factory_id == target_factory.id)
        )
        existing_parts_list = existing_parts_result.scalars().all()

        # Create dual-lookup dictionaries (case-insensitive) to catch duplicates even if SKU format changed
        existing_by_sku = {p.sku.strip().lower(): p for p in existing_parts_list if p.sku}
        existing_by_name = {p.name.strip().lower(): p for p in existing_parts_list if p.name}

        created_count = 0
        updated_count = 0
        part_names = []

        for part_data in extraction_result.parts:
            extracted_sku = part_data.sku.strip() if part_data.sku else f"UNKNOWN-{uuid.uuid4().hex[:8]}"
            extracted_name = part_data.name.strip() if part_data.name else "Unknown Part"
            
            search_sku = extracted_sku.lower()
            search_name = extracted_name.lower()

            # Smart Match: Try SKU first, then fallback to Name matching
            existing_part = None
            if search_sku in existing_by_sku:
                existing_part = existing_by_sku[search_sku]
            elif search_name in existing_by_name:
                existing_part = existing_by_name[search_name]

            if existing_part:
                # UPDATE existing part with latest PDF data (only quantity and category, preserving existing SKU/Name)
                existing_part.current_stock = part_data.quantity
                if part_data.category:
                    existing_part.category = part_data.category
                updated_count += 1
                part_names.append(f"{existing_part.name} (updated quantity to {part_data.quantity})")
            else:
                # CREATE new part
                new_part = SparePart(
                    factory_id=target_factory.id,
                    sku=extracted_sku,
                    name=extracted_name,
                    current_stock=part_data.quantity,
                    category=part_data.category,
                    minimum_threshold=5, 
                    location_bin="Unassigned Upload"
                )
                db.add(new_part)
                # Add to dictionaries so we catch duplicates WITHIN the same PDF
                existing_by_sku[search_sku] = new_part 
                existing_by_name[search_name] = new_part
                created_count += 1
                part_names.append(f"{extracted_name} (new)")

        await db.commit()

        return {
            "status": "success", 
            "message": f"AI processed {len(extraction_result.parts)} parts: {created_count} created, {updated_count} updated.",
            "data": part_names
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

@router.get("/overview", tags=["Warehouse & Inventory Operations"])
async def get_overview_stats(db: AsyncSession = Depends(get_db)):
    """Fetches live KPI aggregations from the database for the overview dashboard."""
    from sqlalchemy import func
    from sqlalchemy.orm import selectinload
    from app.models.inventory import InventoryTransaction

    # 1. Total Spare Parts Count
    total_parts_result = await db.execute(select(func.count(SparePart.id)))
    total_parts = total_parts_result.scalar() or 0
    
    # 2. Critical Shortages Count
    shortages_result = await db.execute(
        select(func.count(SparePart.id)).where(SparePart.current_stock < SparePart.minimum_threshold)
    )
    critical_shortages = shortages_result.scalar() or 0
    
    # 3. Pending POs Count
    pending_pos_result = await db.execute(
        select(func.count(InventoryTransaction.id)).where(
            and_(
                InventoryTransaction.transaction_type == "PO_DRAFT",
                InventoryTransaction.status == "pending"
            )
        )
    )
    pending_pos = pending_pos_result.scalar() or 0
    
    # 4. Recent Activity (Latest 5 Transactions)
    recent_activity_result = await db.execute(
        select(InventoryTransaction)
        .options(selectinload(InventoryTransaction.part))
        .order_by(InventoryTransaction.timestamp.desc())
        .limit(5)
    )
    recent_txns = recent_activity_result.scalars().all()
    
    activity_feed = []
    for txn in recent_txns:
        part_name = txn.part.name if txn.part else "Unknown Part"
        action = "Drafted PO" if txn.transaction_type == "PO_DRAFT" else txn.transaction_type
        activity_feed.append({
            "id": str(txn.id),
            "action": action,
            "part_name": part_name,
            "quantity": txn.quantity,
            "status": getattr(txn, "status", "completed"),
            "timestamp": txn.timestamp.isoformat() if txn.timestamp else None
        })
        
    return {
        "status": "success",
        "data": {
            "total_parts": total_parts,
            "critical_shortages": critical_shortages,
            "pending_pos": pending_pos,
            "agent_status": "Online",
            "recent_activity": activity_feed
        }
    }