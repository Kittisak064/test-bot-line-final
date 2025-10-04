from fastapi import FastAPI
from app.routers.webhook_line import router as line_router
from app.utils.excel_loader import DATA  # preload และใช้ดู health

app = FastAPI(title="Commerce LINE Bot")

app.include_router(line_router)

@app.get("/")
def root():
    # health + ข้อมูลย่อ
    return {
        "ok": True,
        "sheets_loaded": {
            "company": len(DATA["company"]),
            "products": len(DATA["products"]),
            "faq": len(DATA["faq"]),
            "training_doc": len(DATA["training_doc"]),
        }
    }
