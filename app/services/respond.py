# app/services/respond.py
from __future__ import annotations
import os
from typing import Dict, Any, List
from openai import OpenAI
from app.services.classify import classify_intent
from app.utils.excel_loader import search_products

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # ปรับได้

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "คุณคือแอดมินขายของออนไลน์ที่พูดสุภาพ เป็นกันเอง เรียก ‘คุณลูกค้า’ ตอบเป็นภาษาไทยเสมอ "
    "หน้าที่คือช่วยขาย/ให้ข้อมูล/บริการหลังการขาย แต่ต้องยึด ‘ข้อเท็จจริง’ "
    "จากข้อมูลที่ส่งให้เท่านั้น ห้ามเดาข้อมูล ห้ามพูดสิ่งที่ไม่มีในข้อมูล "
    "ห้ามเปิดเผยรหัสสินค้า (SKU) ต่อหน้าลูกค้า "
    "คำตอบควรกระชับ อ่านง่าย ใส่ emoji ได้เล็กน้อย และชวนคุยต่อหนึ่งคำถาม"
)

def _facts_from_products(items: List[Dict[str, Any]]) -> str:
    lines = []
    for i, p in enumerate(items, 1):
        # ไม่ใส่ SKU
        price = p["price_sell"] if p["price_sell"] not in (None, "") else p["price_list"]
        line = (
            f"{i}. ชื่อรุ่น: {p['name']} "
            f"(หมวด: {p['category']}; รองรับ: {p['size']}{p['unit']}) "
            f"ราคาขาย: {price} บาท"
        )
        if p["ship_cost"] not in (None, ""):
            line += f" | ค่าส่งโดยประมาณ: {p['ship_cost']} บาท"
        lines.append(line)
    return "\n".join(lines) if lines else "ไม่พบบันทึกสินค้าที่ตรงกับคำค้น"

async def generate_reply(user_text: str) -> str:
    intent = classify_intent(user_text)
    products = search_products(user_text, top_k=3)  # ดึงจากชีท

    facts = (
        f"# บริบทสำหรับ AI\n"
        f"- intent: {intent}\n"
        f"- สินค้าที่เกี่ยวข้อง (ดึงจากชีท):\n{_facts_from_products(products)}\n\n"
        f"# กติกาเข้มงวด\n"
        f"- ตอบเฉพาะจากข้อเท็จจริงด้านบน หากข้อมูลไม่พอ ให้บอกตรงๆ และชวนถามต่อ\n"
        f"- ห้ามแสดงรหัสสินค้า (SKU)\n"
        f"- หากลูกค้าขอ ‘รุ่น’ ให้เสนอได้ไม่เกิน 3 ตัวเลือก พร้อมเหตุผลสั้นๆ\n"
        f"- ถ้าเป็น ‘หลังการขาย’ เน้นขั้นตอนช่วยเหลือ เช่น ส่งหลักฐาน/เลขสั่งซื้อ/วิธีเคลม ฯลฯ\n"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"ข้อความลูกค้า: {user_text}\n\nข้อมูลอ้างอิง:\n{facts}"},
    ]

    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.6,   # เป็นธรรมชาติแต่ยังคุมข้อเท็จจริง
        max_tokens=400,
    )
    return resp.choices[0].message.content.strip()
