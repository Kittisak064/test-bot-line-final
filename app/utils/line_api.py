import os, httpx

LINE_API_REPLY = "https://api.line.me/v2/bot/message/reply"
ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")

async def send_line_reply(reply_token: str, text: str):
    if not ACCESS_TOKEN:
        raise RuntimeError("LINE_CHANNEL_ACCESS_TOKEN not set")
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": (text or '')[:4900]}]
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(LINE_API_REPLY, headers=headers, json=body)
        r.raise_for_status()
