from langchain_core.messages import SystemMessage, AIMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import Literal

from app.agents.state import AgentState

# 1. Initialize the Fast Model
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# 2. Define the Strict Output Schema
class RouteDecision(BaseModel):
    next_node: Literal["query_specialist", "diagnosis_specialist", "procurement_specialist", "FINISH"] = Field(
        description="The specialist to route to. Choose FINISH for greetings, small talk, or out-of-scope questions."
    )
    direct_response: str = Field(
        description="If next_node is FINISH, write a friendly, concise response to the user here. Otherwise, leave empty.",
        default=""
    )

# 3. Bind the Schema to the LLM
structured_supervisor = llm.with_structured_output(RouteDecision)

# 4. The System Prompt
SUPERVISOR_PROMPT = """You are the Lead Supervisor Agent for SmartSpare AI.
Analyze the user conversation and make a strict routing decision.

ROUTING RULES:
* query_specialist: For inventory, stock, or part number inquiries.
* diagnosis_specialist: For machine faults, error codes, or troubleshooting.
* procurement_specialist: For ordering parts or purchase orders.
* FINISH: Use this IMMEDIATELY for greetings, thank yous, or generic small talk.

If you select FINISH, you MUST provide a helpful 'direct_response'.
"""

async def supervisor_node(state: AgentState):
    """
    Analyzes the chat and either routes to a specialist or terminates the graph.
    """
    messages = state.get("messages", [])
    prompt_messages = [SystemMessage(content=SUPERVISOR_PROMPT)] + messages
    
    # Force the LLM to output the exact JSON structure
    decision: RouteDecision = await structured_supervisor.ainvoke(prompt_messages)
    
    # THE SHORT-CIRCUIT: If it is small talk, answer and end the graph immediately
    if decision.next_node == "FINISH":
        return {
            "next_node": "FINISH",
            "messages": [AIMessage(content=decision.direct_response)]
        }
        
    # THE SPECIALIST PATH: Route to the correct expert
    return {"next_node": decision.next_node}
