from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID, uuid4

# Import our compiled graph and state definitions
from app.agents.graph import smartspare_graph
from app.api.dependencies import get_current_user, get_current_factory_id
from app.models.tenant import User

router = APIRouter()

# 1. API Contracts (Pydantic Schemas)
class ChatRequest(BaseModel):
    message: str = Field(..., description="The natural language query from the factory worker.")
    thread_id: Optional[str] = Field(None, description="Provide this to continue an existing conversation.")

class ChatResponse(BaseModel):
    thread_id: str
    response: str
    status: str
    metadata: dict[str, Any] = Field(default_factory=dict)

# 2. The Core Execution Endpoint
@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    factory_id: UUID = Depends(get_current_factory_id)
):
    """
    Submits a user query to the SmartSpare multi-agent orchestrator.
    """
    active_thread_id = request.thread_id or str(uuid4())
    config = {"configurable": {"thread_id": active_thread_id}}
    
    initial_state = {
        "messages": [("user", request.message)],
        "factory_id": factory_id,
        "current_user_id": current_user.id,
        "user_role": current_user.role, 
        "active_sku": None,
        "active_fault_code": None,
        "pending_po_draft": None,
        "requires_human_approval": False,
        "next_node": ""
    }

    try:
        final_state = await smartspare_graph.ainvoke(initial_state, config=config)
        
        messages = final_state.get("messages", [])
        if not messages:
            raise HTTPException(status_code=500, detail="Agent failed to generate a response.")
            
        ai_message = messages[-1].content
        
        return ChatResponse(
            thread_id=active_thread_id,
            response=ai_message,
            status="success",
            metadata={
                "requires_approval": final_state.get("requires_human_approval", False),
                "active_sku": final_state.get("active_sku")
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent orchestration failed: {str(e)}"
        )