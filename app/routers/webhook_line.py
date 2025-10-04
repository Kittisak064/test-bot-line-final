from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.services.respond import generate_reply
from app.services.line_api import send_text_message

router = APIRouter()

@router.post("/webhook/line")
async def line_webhook(request: Request):
    try:
        body = await request.json()
        events = body.get("events", [])

        for event in events:
            if event.get("type") != "message":
                continue

            message = event.get("message", {})
            if message.get("type") != "text":
                continue

            user_id = event.get("source", {}).get("userId")
            user_message = message.get("text", "")

            # ส่งข้อความไปให้ AI ตอบ
            bot_reply = await generate_reply(user_message)

            # ส่งกลับไปที่ LINE
            if user_id and bot_reply:
                send_text_message(user_id, bot_reply)

        return JSONResponse(content={"status": "ok"})

    except Exception as e:
        return JSONResponse(
            content={"status": "error", "detail": str(e)},
            status_code=500
        )
