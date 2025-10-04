import os
from typing import Dict, Any, List, Union
from openai import OpenAI

from app.utils.excel_loader import (
    search_products,
    list_promotions,
    search_faq,
    list_intent_instructions,
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def _fmt_price(v) -> str:
    try:
        n = float(v)
        if n.is_integer():
            return f"{int(n):,}"
        return f"{n:,.2f}"
    except Exception:
        return str(v) if v is not None else "-"

def _render_product(p: Dict[str, Any]) -> str:
    # หลีกเลี่ยงการโชว์ "รหัสสินค้า" ให้ลูกค้าเห็นตรง ๆ
    name = p.get("ชื่อสินค้าในระบบขาย") or p.get("ชื่อสินค้าที่มักถูกเรียก") or "สินค้า"
    size = p.get("ขนาด")
    unit = p.get("หน่วย")
    price = _fmt_price(p.get("ราคาขาย"))
    price_full = _fmt_price(p.get("ราคาเต็ม"))
    ship = _fmt_price(p.get("ราคาค่าขนส่ง"))
    spec = f" ({size} {unit})" if size or unit else ""
    base = f"คุณลูกค้าสนใจ {name}{spec} ใช่ไหมคะ 🙂\n"
    price_line = f"ราคา {price} บาท" + (f" (ปกติ {price_full} บาท)" if price_full and price_full != price else "")
    ship_line = f"\nค่าจัดส่ง {ship} บาท" if ship and ship != "-" else ""
    return base + price_line + ship_line

def _render_promotions(promos: List[Dict[str, Any]]) -> str:
    if not promos:
        return ""
    lines = []
    for idx, r in enumerate(promos[:5], 1):
        title = r.get("ชื่อโปร") or r.get("หัวข้อ") or r.get("รายการ") or "โปรโมชัน"
        detail = r.get("รายละเอียด") or r.get("เงื่อนไข") or ""
        lines.append(f"{idx}. {title} — {detail}".strip(" —"))
    return "🎉 โปรโมชันปัจจุบัน:\n" + "\n".join(lines)

def _fallback_llm(user_text: str, context: str) -> str:
    if not client:
        # ถ้าไม่มี API key ให้ตอบอย่างสุภาพ โดยไม่มั่ว
        return ("ตอนนี้หนูยังไม่มีข้อมูลเพียงพอจากฐานข้อมูลค่ะ 🙏\n"
                "รบกวนบอกชื่อสินค้าหรือคำถามเพิ่มเติมอีกนิดได้ไหมคะ")

    sys = (
        "คุณคือแอดมินร้านค้าปลีกไทย ให้ข้อมูลตรงตามฐานความรู้เท่านั้น "
        "ห้ามเดาข้อมูลราคา/สต็อก/เงื่อนไข ถ้าไม่แน่ใจให้บอกว่าไม่ทราบและขอข้อมูลเพิ่ม "
        "สื่อสารสุภาพ เรียกลูกค้าว่า 'คุณลูกค้า' มีอีโมจิพอดี ๆ"
    )
    user = (
        f"ข้อความลูกค้า: {user_text}\n\n"
        f"บริบทจากชีท (ถ้ามี):\n{context}\n\n"
        "หากในบริบทไม่มีข้อมูลที่ชัดเจน ให้ถามกลับอย่างสุภาพเพื่อขอรายละเอียดเพิ่ม"
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": user},
            ],
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"ขออภัยค่ะ ระบบตอบช้าชั่วคราว 🙏 ({e})"

async def generate_reply(user_text: str) -> Union[str, Dict[str, Any]]:
    """
    ลำดับการตอบ:
    1) ถามหาแอดมิน → handover
    2) ตรงจากชีท: สินค้า → โปรโมชัน → FAQ
    3) ไม่พบ → ให้ LLM ช่วย แต่ต้อง 'ไม่มั่ว' (ยึด context ที่ส่งให้)
    """
    # 1) Handover
    if any(k in user_text for k in ["แอดมิน", "คนจริง", "ติดต่อ", "โทร", "คุยกับคน"]):
        return {"text": "รับทราบค่ะ หนูส่งต่อให้แอดมินดูแลต่อทันทีนะคะ 📞", "handover": True}

    # 2.1) สินค้า
    products = search_products(user_text)
    if products:
        # โชว์รายการแรกแบบสุภาพ (หลีกเลี่ยงโชว์ 'รหัสสินค้า')
        p = products[0]
        text = _render_product(p)

        # แนบโปรโมชันสั้น ๆ ถ้ามี
        promos = list_promotions()
        promo_text = _render_promotions(promos)
        if promo_text:
            text += "\n\n" + promo_text + "\n\n"
            text += "ถ้าสนใจ หนูเช็คราคาและสต็อกให้เพิ่มได้ค่ะ ✨"
        else:
            text += "\n\nหากสนใจ หนูเช็คสต็อกและนัดจัดส่งให้ได้เลยค่ะ ✨"
        return text

    # 2.2) โปรโมชัน
    promos = list_promotions()
    if any(k in user_text for k in ["โปร", "ส่วนลด", "โปรโมชัน", "promotion"]) and promos:
        return _render_promotions(promos)

    # 2.3) FAQ
    faqs = search_faq(user_text)
    if faqs:
        # ตอบข้อแรกที่แมตช์
        ans = faqs[0].get("คำตอบ") or "ขออภัยค่ะ ยังไม่มีคำตอบในระบบ"
        return f"ℹ️ {ans}"

    # 3) Fallback → LLM (ด้วยบริบทจาก intent instruction ถ้ามี)
    intents = list_intent_instructions()
    ctx = ""
    if intents["before"]:
        ctx += "แนวคำตอบก่อนขาย:\n" + "\n".join(str(r) for r in intents["before"][:5]) + "\n\n"
    if intents["after"]:
        ctx += "แนวคำตอบหลังขาย:\n" + "\n".join(str(r) for r in intents["after"][:5]) + "\n\n"

    return _fallback_llm(user_text, ctx)
