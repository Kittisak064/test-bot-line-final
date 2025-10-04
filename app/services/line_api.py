import os
import httpx

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def send_text_message(user_id: str, text: str):
    """ส่งข้อความธรรมดากลับไปยัง LINE"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "to": user_id,
        "messages": [{"type": "text", "text": text}]
    }
    try:
        with httpx.Client() as client:
            client.post("https://api.line.me/v2/bot/message/push",
                        headers=headers, json=body)
    except Exception as e:
        print(f"LINE API error: {e}")
