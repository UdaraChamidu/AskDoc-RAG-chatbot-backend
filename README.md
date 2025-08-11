# AskDoc Chatbot - Backend

This is the **FastAPI backend** for the AskDoc chatbot application.  
It serves the API endpoints for uploading PDFs and querying the AI chatbot.

---
<img width="1103" height="831" alt="image" src="https://github.com/user-attachments/assets/cc4ff7d7-811e-4466-91dc-9fdc016ae026" />



## Demo

[![Open Demo](https://img.shields.io/badge/Open-Demo-blue?style=for-the-badge&logo=google-chrome)](http://your-demo-url.com)  
<!-- Replace `http://your-demo-url.com` with your actual deployed backend/demo URL -->

---

## Features

- PDF file upload and storage
- RAG-based AI chatbot answering questions based on PDFs
- Session-based chat history
- CORS enabled for React frontend

---

## Getting Started

### Prerequisites

- Python 
- pip
- langchain
- Faiss
- Gemini API
- pypdf loader
- recursive character splitter
- google generative AI embedding
- dotenv
- FastAPI
- uvicorn

### Installation

```bash
git clone https://github.com/UdaraChamidu/AskDoc-RAG-chatbot-backend.git
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### To Run
```
uvicorn main:app --reload
```
