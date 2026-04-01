from pydantic import BaseModel, Field

# ==========================================
# Query Agent Schemas
# ==========================================
class CheckInventoryInput(BaseModel):
    factory_id: str = Field(description="The UUID of the current factory. Extract this from your system state.")
    query: str = Field(description="The name, brand, or SKU of the spare part to search for in the database.")

class CheckInventoryOutput(BaseModel):
    status: str = Field(description="The result of the database search.")
    quantity: int = Field(default=0, description="The current stock level available.")
    location: str = Field(default="Unknown", description="The warehouse location of the item.")

# ==========================================
# Procurement Agent Schemas
# ==========================================
class DraftPOInput(BaseModel):
    factory_id: str = Field(description="The UUID of the current factory. Extract this from your system state.")
    part_name: str = Field(description="The exact name of the part to order.")
    quantity: int = Field(description="The quantity to order.")
    urgency: str = Field(default="normal", description="The urgency of the order (normal or critical).")

# ==========================================
# Diagnosis Agent Schemas
# ==========================================
class SearchManualsInput(BaseModel):
    factory_id: str = Field(description="The UUID of the current factory. Extract this from your system state.")
    symptom_or_error: str = Field(description="The error code or symptom to look up in the RAG system.")