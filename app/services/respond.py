import os
from openai import OpenAI
from app.utils.excel_loader import search_product, search_faq, get_sheet

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
คุณคือแชทบอทผู้ช่วยขายสินค้าออนไลน์:
- พูดคุยสุภาพ เป็นธรรมชาติ
- ไม่ต้องแสดงรหัสสินค้าให้ลูกค้าเห็น
- อธิบายคุณสมบัติ ราคา โปรโมชั่น ให้เข้าใจง่าย
- ถ้าหาคำตอบจาก Excel ได้ → ใช้ข้อมูลนั้น
- ถ้าไม่มีข้อมูล → ตอบอย่างสุภาพว่าขอให้แอดมินช่วย
"""

async def generate_reply(user_message: str) -> str:
    # 1) ตรวจสอบว่าเป็น FAQ ก่อน
    faqs = search_faq(user_message)
    if faqs:
        best = faqs[0]
        return f"{best.get('คำตอบ', 'ขออภัยค่ะ ตอนนี้ยังไม่มีข้อมูล')}"

    # 2) ตรวจสอบว่าเป็นสินค้าหรือไม่
    products = search_product(user_message)
    if products:
        best = products[0]
        name = best.get("ชื่อสินค้าในระบบขาย") or best.get("ชื่อสินค้าที่มักถูกเรียก")
        price = best.get("ราคาขาย") or best.get("ราคาเต็ม")
        size = best.get("ขนาด") or ""
        unit = best.get("หน่วย") or ""
        promo = _find_promotion_for(name)

        reply = f"สินค้า **{name}** ({size}{unit}) ราคา {price} บาท"
        if promo:
            reply += f"\nโปรโมชั่น: {promo}"
        reply += "\nสนใจสั่งซื้อได้เลยนะคะ"
        return reply

    # 3) ถ้าไม่เจอ → ส่งให้ OpenAI ตอบเสริม
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    return completion.choices[0].message.content.strip()


def _find_promotion_for(product_name: str) -> str:
    """ค้นหาโปรโมชั่นที่เกี่ยวข้องกับสินค้า"""
    promotions = get_sheet("โปรโมชั่น")
    for promo in promotions:
        if not promo:
            continue
        text_all = " ".join([str(v) for v in promo.values() if v])
        if product_name and product_name in text_all:
            return promo.get("รายละเอียดโปรโมชั่น") or ""
    return ""
