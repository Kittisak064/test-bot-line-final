import os
import openai
from app.utils.excel_loader import (
    search_products,
    search_promotions,
    search_faq,
)

openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_reply(user_text: str):
    """
    ฟังก์ชันหลักที่ใช้ให้ AI ตอบลูกค้า
    - ค้นหาสินค้า / โปร / FAQ จาก Excel
    - ถ้าไม่พบ ส่งให้ OpenAI ช่วยตอบ
    - ถ้าเจอคำขอ handover → ส่งต่อแอดมิน
    """
    # 1) ตรวจสอบว่าผู้ใช้ต้องการให้ส่งต่อแอดมินหรือไม่
    if any(word in user_text for word in ["แอดมิน", "เจ้าหน้าที่", "คนจริง", "โทร"]):
        return {
            "text": "หนูจะส่งต่อให้แอดมินดูแลต่อทันทีค่ะ 📞",
            "handover": True
        }

    # 2) ลองค้นหาจาก Excel
    product_result = search_products(user_text)
    if product_result:
        return f"📦 {product_result}"

    promo_result = search_promotions(user_text)
    if promo_result:
        return f"🎉 โปรโมชั่น: {promo_result}"

    faq_result = search_faq(user_text)
    if faq_result:
        return f"ℹ️ {faq_result}"

    # 3) ถ้าไม่เจออะไรเลย ใช้ OpenAI ช่วยตอบ
    try:
        resp = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "คุณคือแชทบอทผู้ช่วยขายออนไลน์ พูดสุภาพ เรียกลูกค้าว่า 'คุณลูกค้า' ตลอด"},
                {"role": "user", "content": user_text},
            ],
        )
        return resp.choices[0].message["content"]
    except Exception as e:
        return f"ขออภัยค่ะ เกิดข้อผิดพลาดจากระบบ ({str(e)})"
