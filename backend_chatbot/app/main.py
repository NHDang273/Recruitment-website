from fastapi import FastAPI
from app.routers import chatbot

app = FastAPI()

# Đăng ký router cho chatbot
app.include_router(chatbot.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Chatbot API"}
