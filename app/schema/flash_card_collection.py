from pydantic import BaseModel, Field
from typing import List

from app.schema import Flashcard

class FlashcardCollection(BaseModel):
    cards: List[Flashcard]