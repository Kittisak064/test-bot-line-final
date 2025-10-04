import os
from typing import Dict, Any
from openai import OpenAI
from app.utils.excel_loader import DATA, match_products_by_query, match_faq_by_query

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# คำที่ให้สลับหาแอดมิน
ADMIN_KEYWORDS = ["แอดมิน", "คนจริง", "พนักงาน", "เจ้าหน้าที่", "ขอคุยกับคน"]

def _should_handover_to_admin(text: str) -> bool:
    tl = (text or "").lower()
    return any(k in tl for k in ADMIN_KEYWORDS)

def _build_system_prompt() -> str:
    persona = DATA["persona"]
    training = DATA["training_raw"]
    company  = DATA["company"]

    style = [
        f"คุณคือน้องแชทบอทชื่อ: {persona.get('ชื่อพนักงาน','น้องแชทบอท')}",
        f"วิธีเรียกลูกค้า: {persona.get('เรียกลูกค้าว่า','ลูกค้า')}",
        f"โทน: {persona.get('บุคลิก และการตอบกลับลูกค้า','สุภาพ เป็นมิตร เน้นช่วยเหลือ')}",
    ]

    firm_rules = [
        "ห้ามเปิดเผยรหัสสินค้า/SKU ต่อหน้าลูกค้า",
        "อิงข้อมูลจากบริบท (products, FAQ, training doc) เท่านั้น หากไม่พบให้ถามต่อเพื่อเก็บ requirement หรือเสนอคุยแอดมิน",
        "สรุปสั้น กระชับ มี bullet เมื่อเหมาะสม และลงท้ายด้วยคำชวนคุย/CTA ตาม instruction",
    ]

    company_bits = [f"{k}: {v}" for k,v in company.items()][:8]  # เอาสั้น ๆ พอเป็นตัวตน

    return "\n".join([
        "### ROLE",
        *style,
        "",
        "### COMPANY SNAPSHOT",
        *company_bits,
        "",
        "### HARD RULES",
        *[f"- {r}" for r in firm_rules],
        "",
        "### TRAINING GUIDELINE",
        training or "(ไม่มี)",
    ])

def _grounding_context(user_text: str) -> str:
    # ดึงข้อมูลที่ตรงจากสินค้ากับ FAQ
    prod = match_products_by_query(DATA["products"], user_text, top_k=3)
    faqs = match_faq_by_query(DATA["faq"], user_text, top_k=3)

    prod_lines=[]
    for i,p in enumerate(prod,1):
        prod_lines.append(
            f"{i}) ชื่อ: {p['name']} | ขนาด: {p['size']}{p['unit']} | ราคาขาย: {p['sale_price']} บาท | ค่าส่ง: {p['shipping']} | หมวด: {p['category']}"
        )
    faq_lines=[]
    for i,f in enumerate(faqs,1):
        faq_lines.append(f"{i}) Q: {f['question']} | A: {f['answer']}")

    # Intent instruction (ก่อนขาย/หลังการขาย) – ใช้เป็นแนว CTA
    intent_pre  = DATA["intents"]["pre_sale"]
    intent_post = DATA["intents"]["post_sale"]
    pre_hint  = "\n".join([f"- {i['how_to']} (CTA: {i['cta']})" for i in intent_pre[:3]])
    post_hint = "\n".join([f"- {i['how_to']} (CTA: {i['cta']})" for i in intent_post[:3]])

    return "\n".join([
        "### PRODUCT CANDIDATES",
        *(prod_lines or ["(ไม่พบที่เกี่ยวข้อง)"]),
        "",
        "### FAQ CANDIDATES",
        *(faq_lines or ["(ไม่พบที่เกี่ยวข้อง)"]),
        "",
        "### INSTRUCTION HINTS (pre-sale)",
        pre_hint or "(ไม่มี)",
        "",
        "### INSTRUCTION HINTS (post-sale)",
        post_hint or "(ไม่มี)"
    ])

async def generate_reply(user_text: str) -> Dict[str, Any]:
    # ตรวจ admin takeover
    if _should_handover_to_admin(user_text):
        return {
            "text": "รับทราบค่ะ เดี๋ยวน้องประสานให้แอดมินรับช่วงต่อทันที ⏳ หากสะดวกบอกหัวข้อสั้น ๆ ไว้ก่อนได้เลยค่ะ",
            "handover": True
        }

    sys_prompt = _build_system_prompt()
    context    = _grounding_context(user_text)

    prompt = (
        f"### USER\n{user_text}\n\n"
        f"### CONTEXT (ใช้ตอบเท่านั้น ห้ามแต่งเกินจริง)\n{context}\n\n"
        "จงตอบแบบเป็นธรรมชาติ ไม่โชว์รหัส/SKU และหากลูกค้าเลือกสินค้าแล้วให้ยืนยันราคา+ค่าส่ง และเสนอขั้นถัดไป"
    )

    # ไม่มีคีย์ก็ fallback เป็น rule-based
    if not OPENAI_API_KEY:
        # ตอบจาก FAQ ถ้ามี
        faqs = match_faq_by_query(DATA["faq"], user_text, top_k=1)
        if faqs:
            return {"text": faqs[0]["answer"], "handover": False}
        # ตอบจากสินค้า
        prods = match_products_by_query(DATA["products"], user_text, top_k=3)
        if prods:
            lines = ["แอดมินมีรุ่นที่ตรงกับที่สนใจค่ะ ลองดูตัวเลือกด้านล่างนะคะ:"]
            for p in prods:
                lines.append(f"- {p['name']} • {p['sale_price']} บาท • ค่าส่ง {p['shipping']} • หมวด {p['category']}")
            lines.append("ถ้าถูกใจรุ่นไหน พิมพ์บอกรุ่นหรือสเปกเพิ่มเติมได้เลยค่ะ 😊")
            return {"text": "\n".join(lines), "handover": False}
        return {"text": "รับทราบค่ะ รบกวนบอกสเปกหรือการใช้งานที่ต้องการสักนิด เพื่อช่วยแนะนำรุ่นที่คุ้มสุดให้ค่ะ 😊", "handover": False}

    # ใช้ OpenAI แบบตอบอย่างมีกรอบ
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=os.getenv("AI_MODEL","gpt-4o-mini"),
        temperature=0.4,
        messages=[
            {"role":"system","content":sys_prompt},
            {"role":"user","content":prompt}
        ],
    )
    text = resp.choices[0].message.content.strip()
    # safety: กันหลุด SKU
    for bad in ["SKU", "รหัสสินค้า", "รหัส"]:
        if bad in text:
            text = text.replace(bad, "รายละเอียดภายใน")
    return {"text": text, "handover": False}
