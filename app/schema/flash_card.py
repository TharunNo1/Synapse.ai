from pydantic import BaseModel, Field

class Flashcard(BaseModel):
    front: str = Field(..., description="The question or concept name")
    back: str = Field(..., description="The concise answer or definition")
