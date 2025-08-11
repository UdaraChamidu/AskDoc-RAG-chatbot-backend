from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from chatbot.rag_chain import ask_question
import os
import uuid

app = FastAPI()

# Update these origins to your frontend URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # local dev
        "https://ask-doc-rag-chatbot-frontend.vercel.app",  # production frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "PDF Chatbot backend is live"}

import logging

# Setup logger at the top of main.py
logging.basicConfig(level=logging.INFO)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext != "pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        file_id = f"{uuid.uuid4()}.pdf"
        file_path = os.path.join(UPLOAD_DIR, file_id)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        logging.info(f"Uploaded file saved as {file_path}")

        return {"file_id": file_id, "filename": file.filename}
    except Exception as e:
        logging.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")


@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message")
        file_id = data.get("file_id")
        session_id = data.get("session_id", "default")

        if not user_input:
            raise HTTPException(status_code=400, detail="Message is required")
        if not file_id:
            raise HTTPException(status_code=400, detail="File ID is required")

        file_path = os.path.join(UPLOAD_DIR, file_id)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=400, detail="Invalid or missing PDF file")

        answer = ask_question(user_input, file_path, session_id)
        logging.info(f"Answered question for session {session_id}")

        return {"answer": answer}
    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
