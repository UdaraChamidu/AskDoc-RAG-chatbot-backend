from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from chatbot.rag_chain import ask_question
import os
import uuid

app = FastAPI()

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update if hosted elsewhere
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "PDF Chatbot backend is live"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext != "pdf":
        return JSONResponse(status_code=400, content={"error": "Only PDF files are allowed"})

    file_id = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(UPLOAD_DIR, file_id)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"file_id": file_id, "filename": file.filename}  # <-- just return ID

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message", "")
    session_id = data.get("session_id", "default")
    file_id = data.get("file_id")

    # Build full path from ID
    file_path = os.path.join(UPLOAD_DIR, file_id)

    if not file_id or not os.path.exists(file_path):
        return JSONResponse(status_code=400, content={"error": "Invalid or missing PDF"})

    answer = ask_question(user_input, file_path, session_id)
    return {"answer": answer}
