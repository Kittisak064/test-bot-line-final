# app/services/classify.py
from __future__ import annotations

def classify_intent(text: str) -> str:
    t = (text or "").lower()
    pre = ["ราคา","เท่าไร","โปร","มีรุ่น","สเปค","ขนาด","ส่งของ","ค่าส่ง","มีของไหม","สั่งซื้อ"]
    post = ["รับประกัน","เคลม","ซ่อม","ปัญหา","คืน","เปลี่ยน","ใช้งานยังไง","คู่มือ","ติดตั้ง"]
    if any(k in t for k in post):
        return "หลังการขาย"
    if any(k in t for k in pre):
        return "ก่อนการขาย"
    return "ทั่วไป"
