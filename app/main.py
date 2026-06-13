
import os
from pathlib import Path

from fastapi import FastAPI, File, UploadFile

from parsing.make_chunks import build_chunks
from parsing.parser_json import parse_json_file

app = FastAPI(title="Garden API")

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/workspaces/garden/data/upload"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = Path(os.getenv("GARDEN_DB_PATH", "/workspaces/garden/data/garden.db"))


@app.get("/")
async def root():
    return {"message": "Garden Agent API"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api-call/upload")
async def upload_json(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".json"):
        return {"error": "Only .json files are supported"}

    destination = UPLOAD_DIR / file.filename
    with destination.open("wb") as buffer:
        buffer.write(await file.read())

    inserted = parse_json_file(destination, DB_PATH)
    build_chunks(DB_PATH)

    return {
        "filename": file.filename,
        "saved_to": str(destination),
        "inserted_messages": inserted,
    }