from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from app.agents.graph import smartspare_graph
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings


router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    factory_id: str

@router.post("/chat")
async def chat_with_agent(request: ChatRequest):
    # Make the State Dynamic
    initial_state = {
        "messages": [("user", request.message)],
        "factory_id": request.factory_id, 
        "current_user_id": "user-9999" 
    }
    
    # Execute the graph with the safety limits
    final_state = await smartspare_graph.ainvoke(initial_state, max_iterations=10)
    
    return {"response": final_state["messages"][-1].content}

class DiagnosisQuery(BaseModel):
    error_code: str

class RequiredPart(BaseModel):
    name: str
    sku: str
    stock: int
    critical: bool

class DiagnosisResult(BaseModel):
    title: str = Field(description="Short title of the detected fault")
    confidence: str = Field(description="Confidence percentage, e.g., '94%'")
    source: str = Field(description="Source of the diagnosis, e.g., 'OEM Manual'")
    root_cause: str = Field(description="Detailed explanation of why this error happens")
    parts: List[RequiredPart] = Field(description="List of parts needed to fix the issue")

@router.post("/diagnose")
async def run_fault_diagnosis(query: DiagnosisQuery):
    try:
        # Initialize the AI (Using 8B model to avoid rate limits)
        llm = ChatGroq(
            temperature=0.2, 
            model_name="llama-3.1-8b-instant", 
            api_key=settings.GROQ_API_KEY
        )
        
        structured_llm = llm.with_structured_output(DiagnosisResult)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert industrial maintenance AI. Diagnose machine error codes, provide a root cause analysis, and recommend standard industrial spare parts to fix it. Always return your findings in the exact required JSON schema."),
            ("human", "Analyze this error code or symptom: {error_code}")
        ])
        
        chain = prompt | structured_llm
        
        result = await chain.ainvoke({"error_code": query.error_code})
        
        return {"status": "success", "data": result.dict()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))