import json
import uuid
from uuid import UUID
from langchain_core.tools import tool
from sqlalchemy import select

# Import your database session factory and models
from app.core.database import AsyncSessionLocal 
from app.models.inventory import SparePart, InventoryTransaction
from app.schemas.mcp_tools import CheckInventoryInput, CheckInventoryOutput, DraftPOInput, SearchManualsInput
from app.rag.vector_db import search_industrial_manuals


@tool("check_inventory", args_schema=CheckInventoryInput)
async def check_inventory(factory_id: str, query: str) -> str:
    """Use this tool to search the PostgreSQL database for spare parts and stock levels. Returns all matching parts."""
    print(f"\n---> [TOOL START] check_inventory triggered by Agent")
    print(f"---> [INPUTS] Factory: {factory_id} | Query: {query}")
    
    try:
        valid_tenant_id = UUID(factory_id)
        
        async with AsyncSessionLocal() as db:
            stmt = select(SparePart).where(
                SparePart.factory_id == valid_tenant_id,
                SparePart.name.ilike(f"%{query}%")
            )
            result = await db.execute(stmt)
            parts = result.scalars().all()
            
            if not parts:
                # Also try searching by SKU
                stmt_sku = select(SparePart).where(
                    SparePart.factory_id == valid_tenant_id,
                    SparePart.sku.ilike(f"%{query}%")
                )
                result_sku = await db.execute(stmt_sku)
                parts = result_sku.scalars().all()
            
            if not parts:
                msg = f"No parts matching '{query}' found in the database. Stock is 0. Ask the user if they would like to draft a Purchase Order."
                print(f"---> [TOOL RESULT] {msg}\n")
                return msg
            
            # Format all matching parts into a readable summary
            parts_summary = []
            for part in parts:
                parts_summary.append(
                    f"- {part.name} (SKU: {part.sku}) | Stock: {part.current_stock} units | "
                    f"Category: {part.category or 'N/A'} | Location: {part.location_bin or 'Unassigned'}"
                )
            
            result_text = f"Found {len(parts)} matching part(s):\n" + "\n".join(parts_summary)
            print(f"---> [TOOL RESULT] {result_text}\n")
            return result_text
            
    except Exception as e:
        return f"Database query failed: {str(e)}. Stop and ask human for help."

QUERY_TOOLS = [check_inventory]



@tool("draft_po", args_schema=DraftPOInput)
async def draft_po(factory_id: str, part_name: str, quantity: int, urgency: str = "normal") -> str:
    """Use this tool to draft a purchase order when parts are out of stock."""
    print(f"\n---> [TOOL START] draft_po triggered by Agent")
    print(f"---> [INPUTS] Drafting PO for {quantity}x {part_name}")
    
    try:
        valid_tenant_id = UUID(factory_id)
        
        async with AsyncSessionLocal() as db:
            # 1. Look for the part first
            stmt = select(SparePart).where(
                SparePart.factory_id == valid_tenant_id,
                SparePart.name.ilike(f"%{part_name}%")
            )
            result = await db.execute(stmt)
            part = result.scalar_one_or_none()
            
            # 2. If the part does not exist, autonomously create a placeholder
            if not part:
                part = SparePart(
                    factory_id=valid_tenant_id,
                    sku=f"REQ-{uuid.uuid4().hex[:6].upper()}",
                    name=part_name,
                    current_stock=0,
                    category="Requested New Part",
                    minimum_threshold=5,
                    location_bin="Pending Arrival"
                )
                db.add(part)
                await db.flush()
            
            # 3. Create the PO with status and urgency fields
            new_po = InventoryTransaction(
                factory_id=valid_tenant_id,
                part_id=part.id, 
                user_id=None,
                transaction_type="PO_DRAFT", 
                quantity=quantity,
                status="pending",
                urgency=urgency
            )
            db.add(new_po)
            await db.commit()
            
        success_msg = f"SUCCESS: PO Drafted for {quantity}x {part.name} (Urgency: {urgency}). Status: Pending Human Approval on the Procurement Console."
        print(f"---> [TOOL RESULT] {success_msg}\n")
        return success_msg
        
    except Exception as e:
        err = f"PO creation failed: {str(e)}"
        print(f"---> [TOOL ERROR] {err}\n")
        return err

PROCUREMENT_TOOLS = [draft_po]



@tool("search_manuals", args_schema=SearchManualsInput)
async def search_manuals(factory_id: str, symptom_or_error: str) -> str:
    """Use this tool to securely search the ChromaDB vector store for troubleshooting guides."""
    try:
        valid_tenant_id = UUID(factory_id)
        
        results = await search_industrial_manuals(
            factory_id=valid_tenant_id, 
            query=symptom_or_error, 
            top_k=3
        )
        
        if not results:
            return (
                f"No manuals found regarding: {symptom_or_error}. "
                f"The RAG manual database may be offline or no documents have been indexed yet. "
                f"Please provide your best diagnosis based on general industrial maintenance knowledge, "
                f"and recommend the user consult their OEM manual for specific procedures."
            )
            
        formatted_results = "\n\n".join([r["content"] for r in results])
        return f"Found the following manual excerpts:\n{formatted_results}"
        
    except ValueError:
        return "System Error: Invalid Factory ID provided. Authentication blocked."
    except Exception as e:
        return (
            f"Vector search encountered an issue: {str(e)}. "
            f"Proceed with your general maintenance knowledge to help the user."
        )

DIAGNOSIS_TOOLS = [search_manuals]