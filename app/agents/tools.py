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
    """Use this tool to search the PostgreSQL database for spare parts and stock levels."""
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
            part = result.scalar_one_or_none()
            
            if not part:
                msg = f"Stock is 0. Part '{query}' not found. DO NOT search again. Immediately proceed to draft a PO."
                print(f"---> [TOOL RESULT] {msg}\n")
                return msg
            
            output = CheckInventoryOutput(
                status="Success",
                quantity=part.current_stock,
                location=part.location_bin or "Unassigned"
            )
            final_json = output.model_dump_json()
            print(f"---> [TOOL RESULT] {final_json}\n")
            return final_json
            
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
            agent_uuid = uuid.uuid4() 
            
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
                await db.flush() # Saves to DB and generates the required part.id
            
            # 3. Create the PO using the valid part_id and a strictly 20-char string
            new_po = InventoryTransaction(
                factory_id=valid_tenant_id,
                part_id=part.id, 
                user_id=agent_uuid, 
                transaction_type="PO_DRAFT", 
                quantity=quantity
            )
            db.add(new_po)
            await db.commit()
            
        success_msg = f"SUCCESS: System Action: PO Drafted for {quantity}x {part.name}. Status: Pending Human Approval."
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
            return f"No manuals found regarding: {symptom_or_error}"
            
        formatted_results = "\n\n".join([r["content"] for r in results])
        return f"Found the following manual excerpts:\n{formatted_results}"
        
    except ValueError:
        return "System Error: Invalid Factory ID provided. Authentication blocked."
    except Exception as e:
        return f"CRITICAL: Vector Database is offline. Stop searching manuals and proceed directly to checking inventory. Error: {str(e)}"

DIAGNOSIS_TOOLS = [search_manuals]