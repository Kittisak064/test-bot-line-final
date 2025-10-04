import httpx
import os

LINE_API_URL = "https://api.line.me/v2/bot/message/reply"
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

async def send_line_reply(reply_token: str, message: str):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(LINE_API_URL, headers=headers, json=payload)
        if resp.status_code != 200:
            print(f"❌ LINE API Error: {resp.text}")
