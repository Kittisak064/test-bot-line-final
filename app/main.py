from fastapi import FastAPI
from app.routers.webhook_line import router as line_router

app = FastAPI(title="LINE Excel Chatbot", version="1.0.0")

@app.get("/")
def root():
    return {"ok": True, "service": "LINE Excel Chatbot"}

app.include_router(line_router, prefix="/webhook")
