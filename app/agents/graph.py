from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from typing import Literal

from app.agents.state import AgentState

# Import routing nodes
from app.agents.nodes.supervisor import supervisor_node

# Import specialist nodes
from app.agents.nodes.query import query_specialist_node
from app.agents.nodes.diagonosis import diagnosis_specialist_node
from app.agents.nodes.procurement import procurement_specialist_node

# Import tools
from app.agents.tools import QUERY_TOOLS, DIAGNOSIS_TOOLS, PROCUREMENT_TOOLS

# Define Tool Nodes for each specialist
query_tools_node = ToolNode(QUERY_TOOLS)
diagnosis_tools_node = ToolNode(DIAGNOSIS_TOOLS)
procurement_tools_node = ToolNode(PROCUREMENT_TOOLS)

# Define the Conditional Routing Functions
def supervisor_router(state: AgentState) -> Literal["query_specialist", "diagnosis_specialist", "procurement_specialist", "__end__"]:
    next_route = state.get("next_node")
    if next_route == "FINISH":
        return "__end__"
    if next_route == "query_specialist": 
        return "query_specialist"
    if next_route == "diagnosis_specialist":
        return "diagnosis_specialist"
    if next_route == "procurement_specialist":
        return "procurement_specialist" 
    return "__end__"

# We build dedicated routers for each specialist
def query_router(state: AgentState) -> Literal["query_tools", "supervisor"]:
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None
    if last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "query_tools"
    return "supervisor"

def diagnosis_router(state: AgentState) -> Literal["diagnosis_tools", "supervisor"]:
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None
    if last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "diagnosis_tools"
    return "supervisor"

def procurement_router(state: AgentState) -> Literal["procurement_tools", "supervisor"]:
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None
    if last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "procurement_tools"
    return "supervisor"

# Construct the State Machine
workflow = StateGraph(AgentState)

# Add all nodes to the graph
workflow.add_node("supervisor", supervisor_node)

# Pair each specialist with their dedicated tools
workflow.add_node("query_specialist", query_specialist_node)
workflow.add_node("query_tools", query_tools_node)

workflow.add_node("diagnosis_specialist", diagnosis_specialist_node) 
workflow.add_node("diagnosis_tools", diagnosis_tools_node)

workflow.add_node("procurement_specialist", procurement_specialist_node)
workflow.add_node("procurement_tools", procurement_tools_node)

# Define the Execution Edges
workflow.add_edge(START, "supervisor")

# Supervisor conditional routing
workflow.add_conditional_edges(
    "supervisor",
    supervisor_router,
    {
        "query_specialist": "query_specialist",
        "diagnosis_specialist": "diagnosis_specialist", 
        "procurement_specialist": "procurement_specialist",
        "__end__": END
    }
)

# Specialist routing to their dedicated tools
workflow.add_conditional_edges(
    "query_specialist",
    query_router,
    {"query_tools": "query_tools", "supervisor": "supervisor"}
)
workflow.add_conditional_edges(
    "diagnosis_specialist",
    diagnosis_router,
    {"diagnosis_tools": "diagnosis_tools", "supervisor": "supervisor"}
)
workflow.add_conditional_edges(
    "procurement_specialist",
    procurement_router,
    {"procurement_tools": "procurement_tools", "supervisor": "supervisor"}
)

workflow.add_edge("query_tools", "query_specialist")
workflow.add_edge("diagnosis_tools", "diagnosis_specialist")
workflow.add_edge("procurement_tools", "procurement_specialist")

smartspare_graph = workflow.compile()