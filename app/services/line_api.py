import os
import httpx

LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if not CHANNEL_ACCESS_TOKEN:
    # ไม่ raise ทันทีเพื่อให้ healthz ใช้งานได้ แต่จะส่งข้อความไม่ได้จนกว่าจะตั้งค่า
    print("[WARN] LINE_CHANNEL_ACCESS_TOKEN is not set. Replies will fail.")

async def send_line_reply(reply_token: str, text: str):
    """
    ส่งข้อความตอบกลับผู้ใช้ผ่าน replyToken
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text[:5000]}],  # กันข้อความยาวเกิน
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(LINE_REPLY_URL, headers=headers, json=body)
        # ถ้า token ว่างหรือผิด จะได้ 401/403/400 ควร log แต่ไม่โยนให้ webhook 500
        if resp.status_code >= 400:
            print(f"[LINE ERROR] {resp.status_code}: {resp.text}")
