import os, httpx

LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"
ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN","")

async def send_line_reply(reply_token: str, message: str):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"replyToken": reply_token, "messages": [{"type":"text","text": message[:4900]}]}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(LINE_REPLY_URL, headers=headers, json=payload)
        if r.status_code != 200:
            print("LINE API Error:", r.status_code, r.text)
