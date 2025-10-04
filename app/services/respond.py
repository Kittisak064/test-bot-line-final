import os, asyncio, datetime
from typing import Dict, List
from app.services.classify import classify
from app.services.llm import ask_llm
from app.utils.excel_loader import (
    load_all, search_products, search_faq, active_promotions_text,
    company_info_text, persona_text, search_knowledge, find_order_status, find_service_status
)

HUMAN_LABEL = os.getenv("HUMAN_ESCALATION_LABEL", "ขอคุยกับแอดมิน")

DATA = load_all()  # preload

def render_product_facts(items: List[Dict]) -> str:
    lines = []
    for p in items:
        line = (
            f"- รหัส: {p.get('รหัสสินค้าในระบบขาย','')} | "
            f"ชื่อ: {p.get('ชื่อสินค้าในระบบขาย','')} (aka {p.get('ชื่อสินค้าที่มักถูกเรียก','')}) | "
            f"ขนาด: {p.get('ขนาด','')}{p.get('หน่วย','')} | "
            f"ราคาเต็ม: {p.get('ราคาเต็ม','')} | "
            f"ราคาขาย: {p.get('ราคาขาย','')} | "
            f"ค่าส่ง: {p.get('ราคาค่าขนส่ง','')} | "
            f"หมวด: {p.get('หมวดหมู่','')}"
        )
        lines.append(line)
    return "\n".join(lines) if lines else ""

async def generate_reply(user_text: str) -> str:
    intent = classify(user_text)
    persona = persona_text(DATA)
    company = company_info_text(DATA)

    # Handover
    if intent == "handover":
        return f"หนูโอนให้แอดมินช่วยต่อให้นะคะ พิมพ์ '{HUMAN_LABEL}' ได้เลยค่ะ หรือทิ้งเบอร์ติดต่อไว้ เดี๋ยวทีมงานโทรกลับค่ะ 🙏"

    # Order / Tracking
    if intent == "เช็กออเดอร์":
        status = find_order_status(DATA, user_text)
        if status:
            facts = "\n".join(f"- {k}: {v}" for k,v in status.items())
            return await asyncio.to_thread(ask_llm, user_text, facts, persona, company)
        return "หนูขอเลขออเดอร์/ชื่อผู้สั่งซื้อเพิ่มเติมหน่อยค่ะ เพื่อเช็กสถานะให้นะคะ 🙂"
    if intent == "เช็กพัสดุ":
        status = find_order_status(DATA, user_text)  # reuse (ค้นหาเลขพัสดุใน Orders)
        if status and ("เลขพัสดุ" in status or "Carrier" in status):
            facts = "\n".join(f"- {k}: {v}" for k,v in status.items())
            return await asyncio.to_thread(ask_llm, user_text, facts, persona, company)
        return "หนูขอเลขพัสดุ/ชื่อผู้รับเพิ่มเติมหน่อยค่ะ จะได้ช่วยตามให้ถูกค่านะคะ 📦"

    # Promotions
    if intent == "ถามโปร":
        facts = active_promotions_text(DATA, today=datetime.date.today())
        return await asyncio.to_thread(ask_llm, user_text, facts, persona, company)

    # Product / Price / Shipping
    prods = search_products(DATA, user_text)
    if prods:
        facts = render_product_facts(prods[:6])
        return await asyncio.to_thread(ask_llm, user_text, facts, persona, company)

    # FAQ
    faq = search_faq(DATA, user_text)
    if faq:
        facts = "\n".join([f"- Q: {faq.get('คำถาม','')}", f"- A: {faq.get('คำตอบ','')}"])
        return await asyncio.to_thread(ask_llm, user_text, facts, persona, company)

    # Knowledge base
    know = search_knowledge(DATA, user_text)
    if know:
        facts = "\n".join([f"- {k}: {v}" for k,v in know.items() if v])
        return await asyncio.to_thread(ask_llm, user_text, facts, persona, company)

    # Fallback: company/perona context
    base = (company or "") + "\n" + (persona or "")
    return await asyncio.to_thread(ask_llm, user_text, base, persona, company)
