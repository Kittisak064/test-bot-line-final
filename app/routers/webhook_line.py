import hmac, hashlib, base64, os, json
from fastapi import APIRouter, Request, HTTPException
from app.services.respond import generate_reply
from app.services.line_api import send_line_reply

router = APIRouter()
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")

def verify_signature(body_bytes: bytes, signature: str) -> bool:
    if not LINE_CHANNEL_SECRET:
        return False
    mac = hmac.new(LINE_CHANNEL_SECRET.encode("utf-8"), msg=body_bytes, digestmod=hashlib.sha256)
    expected = base64.b64encode(mac.digest()).decode("utf-8")
    return hmac.compare_digest(expected, signature)

@router.post("/webhook/line")
async def line_webhook(request: Request):
    body_bytes = await request.body()
    signature = request.headers.get("X-Line-Signature", "")
    if not verify_signature(body_bytes, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    body = json.loads(body_bytes.decode("utf-8"))
    events = body.get("events", [])
    for ev in events:
        if ev.get("type") == "message" and ev["message"]["type"] == "text":
            user_text = ev["message"]["text"].strip()
            reply_token = ev["replyToken"]
            reply_text = await generate_reply(user_text)
            await send_line_reply(reply_token, reply_text)
    return {"status": "ok"}
