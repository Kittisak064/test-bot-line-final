from fastapi import APIRouter, Request, HTTPException
from app.services.respond import generate_reply
from app.services.line_api import send_line_reply

router = APIRouter()

@router.post("/webhook/line")
async def line_webhook(request: Request):
    """
    รับ webhook จาก LINE Messaging API (ไม่บังคับ verify signature เพื่อความง่ายในการต่อใช้งาน)
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    events = body.get("events", [])
    for ev in events:
        if ev.get("type") == "message" and ev["message"]["type"] == "text":
            user_text = ev["message"]["text"]
            reply_token = ev["replyToken"]

            bot_resp = await generate_reply(user_text)

            # รองรับทั้ง str และ dict
            if isinstance(bot_resp, str):
                await send_line_reply(reply_token, bot_resp)
            elif isinstance(bot_resp, dict):
                if "text" in bot_resp:
                    await send_line_reply(reply_token, bot_resp["text"])
                if bot_resp.get("handover"):
                    await send_line_reply(reply_token, "👉 กำลังส่งต่อให้แอดมินดูแลต่อค่ะ")
            else:
                await send_line_reply(reply_token, "ขออภัยค่ะ ระบบไม่สามารถตอบได้ในขณะนี้ 🙏")

    return {"status": "ok"}
