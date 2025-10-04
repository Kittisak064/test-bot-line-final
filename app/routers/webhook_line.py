import hmac, hashlib, base64, os, json, asyncio
from fastapi import APIRouter, Header, Request, HTTPException
from app.services.respond import generate_reply
from app.utils.line_api import send_line_reply

router = APIRouter(tags=["line"])

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")

@router.post("/line")
async def line_webhook(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()

    if not LINE_CHANNEL_SECRET:
        raise HTTPException(status_code=500, detail="LINE_CHANNEL_SECRET not set")

    # Signature verify
    hash_ = hmac.new(LINE_CHANNEL_SECRET.encode("utf-8"), body, hashlib.sha256).digest()
    signature = base64.b64encode(hash_).decode()
    if x_line_signature != signature:
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = json.loads(body.decode("utf-8"))
    events = payload.get("events", [])
    tasks = []
    for ev in events:
        if ev.get("type") == "message" and ev["message"]["type"] == "text":
            user_text = ev["message"]["text"].strip()
            reply_token = ev["replyToken"]
            bot_text = generate_reply(user_text)  # returns string
            tasks.append(send_line_reply(reply_token, bot_text))
    if tasks:
        await asyncio.gather(*tasks)
    return {"status": "ok"}
