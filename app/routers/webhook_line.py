from fastapi import APIRouter, Request
from app.services.respond import generate_reply
from app.services.line_api import send_line_reply  # ใช้จาก services

router = APIRouter()

@router.post("/webhook/line")
async def line_webhook(req: Request):
    """
    Webhook สำหรับรับ event จาก LINE Messaging API
    """
    body = await req.json()
    events = body.get("events", [])

    for ev in events:
        # ตรวจสอบว่าเป็นข้อความจากผู้ใช้
        if ev.get("type") == "message" and ev["message"]["type"] == "text":
            user_text = ev["message"]["text"]
            reply_token = ev["replyToken"]

            # สร้างข้อความตอบด้วย AI
            bot_resp = await generate_reply(user_text)

            # ถ้า AI ส่งข้อความมาเป็น string
            if isinstance(bot_resp, str):
                await send_line_reply(reply_token, bot_resp)

            # ถ้า AI ส่งมาเป็น dict (มี text และ handover)
            elif isinstance(bot_resp, dict):
                if "text" in bot_resp:
                    await send_line_reply(reply_token, bot_resp["text"])
                if bot_resp.get("handover"):
                    await send_line_reply(reply_token, "👉 ระบบกำลังส่งต่อให้แอดมินดูแลต่อค่ะ")

    return {"status": "ok"}
