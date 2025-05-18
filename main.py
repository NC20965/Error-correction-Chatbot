import os
from fastapi import FastAPI
from dotenv import load_dotenv
from models import ChatRequest
from chat_engine import get_response
from crisis import contains_crisis_keywords, SAFETY_MESSAGE
from logger import log_chat
from doc_engine import query_documents
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI()

#Allows cors for frontend to access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")
def read_root():
    return {"Message": "Welcome to the AI-Powered  Mental Health Chatbot Chatbot!"}

@app.post("/chat")
def  chat_with_memory(request: ChatRequest):
    session_id = request.session_id
    user_query = request.query

    # Check for crisis keywords
    if contains_crisis_keywords(user_query):
        log_chat(session_id, user_query, SAFETY_MESSAGE, is_crisis=True)
        return {"response": SAFETY_MESSAGE}
    
    response = get_response(session_id, user_query)
    log_chat(session_id, user_query, response, is_crisis=False) 
    return {"response": response}

@app.post("/doc-chats")
def chat_with_documents(request: ChatRequest):
    response = query_documents(request.query)
    return {"response": response}
