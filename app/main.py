from fastapi import FastAPI
from app.routers.webhook_line import router as line_router

app = FastAPI(title="LINE Chatbot", version="1.0.0")

@app.get("/healthz")
def healthcheck():
    return {"status": "ok"}

# หน้าหลักกัน 404 บน Render
@app.get("/")
def root():
    return {"service": "line-chatbot", "docs": "/docs"}

# รวม Router
app.include_router(line_router)
