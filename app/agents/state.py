from typing import Annotated, TypedDict, Optional, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from uuid import UUID

class AgentState(TypedDict):
    # Conversational Memory
    messages: Annotated[list[BaseMessage], add_messages]
    factory_id: UUID
    current_user_id: UUID
    user_role: str
    active_sku: Optional[str]
    active_fault_code: Optional[str]
    pending_po_draft: Optional[dict]
    requires_human_approval: bool
    next_node: str