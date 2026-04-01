from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from app.agents.state import AgentState
from app.agents.tools import QUERY_TOOLS

# 1. Initialize the Specialist LLM
# We bind the specific tools this agent is authorized to use.
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
query_agent_llm = llm.bind_tools(QUERY_TOOLS)

# 2. The Specialist Prompt
system_prompt = """You are the Spare Part Query Specialist for SmartSpare AI 2.0.
Your job is to help factory workers find parts, check stock levels, and reserve items.

You have access to the following context:
Current Factory ID: {factory_id}
User ID: {current_user_id}

Instructions:
1. Always use the provided tools to verify inventory before confirming stock to the user.
2. If a user wants to reserve a part, use the reserve tool.
3. Be concise and professional. You are talking to industrial workers who need quick answers.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
])

query_chain = prompt | query_agent_llm

# 3. The Node Execution Function
async def query_specialist_node(state: AgentState) -> dict:
    """
    Executes the query specialist logic and returns the updated state.
    """
    # We invoke the LLM with the current state messages and context variables
    response = await query_chain.ainvoke({
        "messages": state["messages"],
        "factory_id": state["factory_id"],
        "current_user_id": state["current_user_id"]
    })
    
    # LangGraph will automatically append this response to the state['messages']
    # We also reset the next_node so the graph knows to evaluate what to do next
    return {
        "messages": [response],
        # We clear the routing flag so the tool node or supervisor can take over
        "next_node": "" 
    }