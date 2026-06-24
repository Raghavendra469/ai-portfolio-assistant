from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from chatbot import clear_memory

from chatbot import ask_raghav_ai

app = FastAPI(
    title="Raghav AI"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

@app.get("/")
def home():
    return {
        "message": "Raghav AI is running"
    }

@app.post("/chat")
def chat(request: ChatRequest):

    answer = ask_raghav_ai(
        request.question
    )

    return {
        "answer": answer
    }

@app.post("/reset")
def reset_chat():

    clear_memory()

    return {
        "message": "Chat history cleared"
    }