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
            user_text = ev["message"]["text"]
            reply_token = ev["replyToken"]

            # เรียก AI เพื่อตอบ
            bot = await generate_reply(user_text)

            # ส่งกลับ LINE
            await send_line_reply(reply_token, bot["text"])

            # ถ้า handover → แจ้งว่าให้แอดมิน takeover ได้
            if bot.get("handover"):
                await send_line_reply(reply_token, "👉 ระบบกำลังส่งต่อให้แอดมินดูแลต่อค่ะ")
    return {"status": "ok"}
