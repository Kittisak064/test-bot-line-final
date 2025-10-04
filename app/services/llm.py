import os
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

_client = OpenAI(api_key=OPENAI_API_KEY)

BASE_SYSTEM = """คุณคือแอดมินขายของที่สุภาพ พูดไทยเป็นธรรมชาติ 🙂
กฎเหล็ก: ตอบโดยอ้างอิง 'facts' ที่ให้เท่านั้น หากไม่มีข้อมูล ห้ามเดา ให้บอกอย่างสุภาพและชวนถามเพิ่ม
ห้ามสรุปยอด/ยืนยันออเดอร์เอง ให้ชวนคุยกับแอดมินถ้าพร้อมสั่งซื้อ
คำแทน: เรียกผู้ใช้ 'คุณลูกค้า/คุณพี่', เรียกตัวเอง 'หนู/แอดมิน' ตามบริบท
"""

def build_system_prompt(persona: str = "", company: str = "") -> str:
    extra = []
    if persona:
        extra.append("บุคลิก/สไตล์: " + persona.strip())
    if company:
        extra.append("ข้อมูลบริษัท: " + company.strip())
    return BASE_SYSTEM + ("\n" + "\n".join(extra) if extra else "")

def ask_llm(user_text: str, facts: str, persona: str = "", company: str = "") -> str:
    system_prompt = build_system_prompt(persona, company)
    content = [
        {"role":"system","content": system_prompt},
        {"role":"user","content": f"ข้อความลูกค้า: {user_text}\n\nFacts (ใช้เท่านี้ ห้ามเดา):\n{facts}\n\nจงตอบแบบแชตสั้น กระชับ เป็นมิตร และยึด facts เท่านั้น"},
    ]
    resp = _client.chat.completions.create(model=MODEL, messages=content, temperature=0.3, max_tokens=700)
    return resp.choices[0].message.content.strip()
