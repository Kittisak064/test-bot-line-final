import os, httpx

LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")

async def send_line_reply(reply_token: str, text: str):
    """ส่งข้อความกลับไปยัง LINE โดยใช้ replyToken"""
    if not LINE_ACCESS_TOKEN:
        return
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }
    async with httpx.AsyncClient(timeout=15) as client:
        await client.post(url, headers=headers, json=payload)
