import uvicorn
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException

from app.utils.processor import extract_pdf_text
from .core.anki_generator import AnkiGenerator
import uuid
import random
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

EXPORT_DIR = Path("exports")

app = FastAPI(title="Synapse.ai")
generator = AnkiGenerator("DefaultGenerator")

@app.get("/")
async def root():
    return {"Status": "Synapse.ai is up and running..."}

# Production persistence: Use Redis in real life; dict for this demo
db = {}

@app.post("/v1/generate", status_code=202)
async def create_task(background_tasks: BackgroundTasks, file: UploadFile = File(...), url: str | None = None):
    task_id = str(uuid.uuid4())
    db[task_id] = {"status": "pending"}

    background_tasks.add_task(workflow, task_id, file, url)
    return {"task_id": task_id}

def chunk_text(text: str, chunk_size: int = 4000, overlap: int = 500):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

async def workflow(task_id: str, file: UploadFile, url: str | None):
    try:
        db[task_id]["status"] = "processing"

        # 1. Extraction
        file_bytes = await file.read()
        full_text = extract_pdf_text(file_bytes)# Simplified for demo
        chunks = chunk_text(full_text)

        deck_id = random.randrange(1 << 30, 1 << 31)

        # 2. Generation
        collections = []
        for chunk in chunks:
            collection = await generator.generate_cards_from_text(chunk)
            collections.extend(collection.cards)

        # 3. Packaging
        file_path = EXPORT_DIR / f"{task_id}.apkg"
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        generator.create_package(deck_id, collections, file_path)
        print("package created: ", file_path)
        db[task_id] = {"status": "completed", "url": file_path}
    except Exception as e:
        db[task_id] = {"status": "failed", "error": str(e)}


@app.get("/v1/status/{task_id}")
async def get_status(task_id: str):
    return db.get(task_id, {"error": "Not found"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
