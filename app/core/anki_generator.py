import os
import logging
import google.generativeai as genai
import genanki
from app.schema import *
from typing import List

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL")
class AnkiGenerator:
    def __init__(self, deck_name: str):
        self.deck_name = deck_name
        self.model = genanki.Model(
            1607392319,
            'Creative Pro Model',
            fields=[{'name': 'Question'}, {'name': 'Answer'}],
            templates=[{
                'name': 'Card 1',
                'qfmt': '<div class="card-container front">{{Question}}</div>',
                'afmt': """
                    <div class="card-container front">{{Question}}</div>
                    <div class="divider"></div>
                    <div class="card-container back">{{Answer}}</div>
                """,
            }],
            css="""
            /* THE BACKGROUND */
            .card {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f0f2f5;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
            }

            /* THE CARD CONTAINER */
            .card-container {
                background-color: #ffffff;
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
                padding: 30px;
                width: 90%;
                max-width: 500px;
                text-align: center;
                line-height: 1.5;
                transition: transform 0.2s ease;
            }

            /* FRONT SPECIFIC */
            .front {
                font-size: 24px;
                color: #1a202c;
                font-weight: 600;
                border-bottom: 4px solid #4a90e2;
            }

            /* BACK SPECIFIC */
            .back {
                font-size: 20px;
                color: #2d3748;
                margin-top: 10px;
                background: linear-gradient(to bottom right, #ffffff, #f7fafc);
            }

            /* CUSTOM DIVIDER */
            .divider {
                height: 2px;
                background: linear-gradient(to right, transparent, #cbd5e0, transparent);
                width: 100%;
                margin: 20px 0;
            }

            /* KEYWORD HIGHLIGHTING (Used if Gemini adds <b> tags) */
            b { color: #4a90e2; }
            """
        )
        self.gemini_model = genai.GenerativeModel(
            model_name=GEMINI_MODEL_NAME,
            system_instruction=(
                """
                        You are an expert Anki creator. Convert the text into 'Atomic' flashcards.
                        Rules:
                            1. One fact per card.
                            2. If a fact has multiple parts, create multiple cards.
                            3. Avoid 'What is...' questions if a more specific question can be asked.
                            4. Focus on high-yield, testable facts (dates, names, mechanisms, causes).

                            Example:
                                Bad: What is the Mitochondria? | The powerhouse of the cell that makes ATP.
                                Good: Where is ATP produced in the cell? | Mitochondria.
                    """
            )
        )

    async def generate_cards_from_text(self, text: str) -> FlashcardCollection:
        """Uses OpenAI Structured Outputs to guarantee valid JSON."""
        try:
            response = self.gemini_model.generate_content(f"Convert this text into flashcards:\n\n{text}",
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=FlashcardCollection,
                    temperature=0.2,
                ),)
            return FlashcardCollection.model_validate_json(response.text)
        except Exception as e:
            logger.error(f"LLM Failure: {e}")
            raise

    def create_package(self, deck_id: int, collections: List[FlashcardCollection], output_filepath):
        deck = genanki.Deck(deck_id=deck_id, name=self.deck_name)
        for card in collections:
            note = genanki.Note(model=self.model, fields=[card.front, card.back])
            deck.add_note(note)

        genanki.Package(deck).write_to_file(str(output_filepath))