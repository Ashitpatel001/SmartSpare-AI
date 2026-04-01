from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from app.agents.state import AgentState
from app.agents.tools import PROCUREMENT_TOOLS

# 1. Initialize the Specialist LLM
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
procurement_agent_llm = llm.bind_tools(PROCUREMENT_TOOLS)

# 2. The Cognitive Prompt
system_prompt = """You are the Procurement Specialist for SmartSpare AI 2.0.
Your responsibility is to draft Purchase Orders (POs) when factory inventory is critically low or depleted.

Context:
Factory ID: {factory_id}
User ID: {current_user_id}
Active SKU Context: {active_sku}

Strict Operational Rules:
1. You DO NOT have the authority to finalize purchases. You only DRAFT the PO using the draft_po_tool.
2. Determine the 'suggested_quantity' logically based on standard industrial minimums (usually 5 to 10 units unless specified).
3. Determine 'urgency' (Standard, Expedited, Critical) based on the user's situation. If a machine is actively down, it is Critical.
4. After drafting, inform the user clearly that the PO has been routed to the Plant Supervisor dashboard for final approval.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
])

procurement_chain = prompt | procurement_agent_llm

# 3. The Node Execution Function
async def procurement_specialist_node(state: AgentState) -> dict:
    """
    Executes the procurement logic and intercepts tool calls to flag Human-in-the-Loop constraints.
    """
    response = await procurement_chain.ainvoke({
        "messages": state["messages"],
        "factory_id": state["factory_id"],
        "current_user_id": state["current_user_id"],
        "active_sku": state.get("active_sku", "Unknown")
    })
    
    # State update payload
    state_update = {
        "messages": [response],
        "next_node": ""
    }
    
    # ADVANCED STATE INTERCEPTION:
    # If the LLM decided to draft a PO, we catch the tool call before it even executes.
    # We update the global state so our FastAPI router knows to flag the UI for manager approval.
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call["name"] == "draft_po_tool":
                state_update["requires_human_approval"] = True
                state_update["pending_po_draft"] = tool_call["args"]
                
    return state_update