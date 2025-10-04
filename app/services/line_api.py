import os
import httpx

# ดึง Channel Access Token จาก environment variable
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if not LINE_CHANNEL_ACCESS_TOKEN:
    raise ValueError("กรุณาตั้งค่า environment variable: LINE_CHANNEL_ACCESS_TOKEN")

LINE_REPLY_ENDPOINT = "https://api.line.me/v2/bot/message/reply"


async def send_line_reply(reply_token: str, message: str):
    """
    ส่งข้อความตอบกลับไปยังผู้ใช้ผ่าน LINE Messaging API
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    }

    body = {
        "replyToken": reply_token,
        "messages": [
            {"type": "text", "text": message}
        ],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(LINE_REPLY_ENDPOINT, headers=headers, json=body)
        response.raise_for_status()  # ถ้า error จะ raise exception ออกมา
        return response.json()
