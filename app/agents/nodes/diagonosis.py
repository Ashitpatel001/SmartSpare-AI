from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from app.agents.state import AgentState
from app.agents.tools import DIAGNOSIS_TOOLS

# 1. Initialize the Specialist LLM
# We bind the vector search tool to this specific agent.
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
diagnosis_agent_llm = llm.bind_tools(DIAGNOSIS_TOOLS)

# 2. The Cognitive Prompt
system_prompt = """You are the Fault Diagnosis Specialist for SmartSpare AI 2.0.
Your job is to assist maintenance engineers by looking up error codes, troubleshooting steps, and safety protocols in the factory manuals.

You have access to the following context:
Current Factory ID: {factory_id}
User ID: {current_user_id}

Strict Operational Rules:
1. ALWAYS use the search_manuals_tool to look up information before providing a diagnosis.
2. NEVER guess or hallucinate a repair procedure. If the manual does not contain the answer, tell the user to consult a senior technician.
3. ALWAYS cite the source document name provided by the tool output.
4. If a repair requires a specific spare part mentioned in the manual, highlight that part clearly so the user knows they might need to check inventory next.
5. Prioritize safety warnings above all other instructions.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
])

diagnosis_chain = prompt | diagnosis_agent_llm

# 3. The Node Execution Function
async def diagnosis_specialist_node(state: AgentState) -> dict:
    """
    Executes the fault diagnosis logic, triggering vector searches when necessary.
    """
    response = await diagnosis_chain.ainvoke({
        "messages": state["messages"],
        "factory_id": state["factory_id"],
        "current_user_id": state["current_user_id"]
    })
    
    # Update the state with the new message and clear the routing flag
    return {
        "messages": [response],
        "next_node": "" 
    }