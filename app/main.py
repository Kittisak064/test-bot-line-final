from fastapi import FastAPI
from app.routers.webhook_line import router as line_router

app = FastAPI(title="LINE Excel Chatbot (Multi-Sheet)", version="1.0.0")

@app.get("/")
def root():
    return {"ok": True, "service": "LINE Excel Chatbot (Multi-Sheet)"}

app.include_router(line_router, tags=["line"])
