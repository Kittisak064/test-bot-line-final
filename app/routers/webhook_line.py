# app/routers/webhook_line.py
from __future__ import annotations
from fastapi import APIRouter, Request
from app.services.respond import generate_reply
from app.utils.line_api import send_line_reply

router = APIRouter()

@router.post("/webhook/line")
async def line_webhook(req: Request):
    body = await req.json()
    events = body.get("events", [])
    for ev in events:
        if ev.get("type") == "message" and ev["message"]["type"] == "text":
            text = ev["message"]["text"]
            bot_text = await generate_reply(text)
            await send_line_reply(ev["replyToken"], bot_text)
    return {"status": "ok"}
