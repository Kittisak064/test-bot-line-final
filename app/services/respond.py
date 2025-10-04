from typing import List
from app.services.classify import classify_intent
from app.utils.excel_loader import ExcelCache, Product
import os

BOT_NAME = os.getenv("BOT_DISPLAY_NAME", "แอดมินบอท")
ESCALATE_LABEL = os.getenv("HUMAN_ESCALATION_LABEL", "ขอคุยกับแอดมิน")

def fmt_price(v):
    if v is None: return "—"
    try:
        return f"{int(v):,} บาท" if float(v).is_integer() else f"{v:,.2f} บาท"
    except Exception:
        return str(v)

def product_card(p: Product) -> str:
    return (
        f"• {p.name} ({p.sku})\n"
        f"  - ราคา: {fmt_price(p.sale_price) if p.sale_price else fmt_price(p.list_price)}\n"
        f"  - ค่าส่ง: {fmt_price(p.shipping_fee)}\n"
        f"  - ขนาด/หน่วย: {p.size or '-'} {p.unit or ''}\n"
        f"  - หมวดหมู่: {p.category or '-'}"
    )

def ask_price(products: List[Product]) -> str:
    if not products:
        sample = "\n".join([f"• {p.name}" for p in ExcelCache.top_k(5)])
        return f"หนูยังหาไม่เจอสินค้าเลยค่ะ ลองพิมพ์ชื่อให้ชัดขึ้นนิดนึงได้ไหมคะ 🙂\nตัวอย่างสินค้า:\n{sample}"
    parts = [product_card(p) for p in products[:5]]
    return "รายการราคาที่พบค่ะ ✨\n" + "\n\n".join(parts)

def ask_shipping(products: List[Product]) -> str:
    if not products:
        return "ค่าส่งขึ้นกับรุ่นสินค้าและปลายทางค่ะ ลองระบุชื่อสินค้าที่ต้องการด้วยนะคะ 🙂"
    lines = []
    for p in products[:5]:
        lines.append(f"• {p.name} ({p.sku}) → ค่าส่ง {fmt_price(p.shipping_fee)}")
    return "ค่าส่งสินค้าที่พบค่ะ 📦\n" + "\n".join(lines)

def ask_spec(products: List[Product]) -> str:
    if not products:
        return "ขอชื่อสินค้าที่อยากทราบสเปกด้วยนะคะ เช่น “สเปกรถเข็นไฟฟ้าไต่บันได รุ่น X”"
    lines = []
    for p in products[:5]:
        lines.append(f"• {p.name} ({p.sku}) → ขนาด: {p.size or '-'} {p.unit or ''}")
    return "สรุปสเปกเบื้องต้นค่ะ 🧾\n" + "\n".join(lines)

def ask_category(products: List[Product]) -> str:
    if not products:
        cats = sorted({p.category for p in ExcelCache.all_products() if p.category})
        return "หมวดหมู่สินค้าที่มีตอนนี้:\n" + "\n".join([f"• {c}" for c in cats]) if cats else "ยังไม่มีหมวดหมู่ในไฟล์ค่ะ"
    cats = sorted({p.category for p in products if p.category})
    if not cats:
        return "รุ่นนี้ยังไม่ได้ระบุหมวดหมู่ไว้ค่ะ"
    return "หมวดหมู่ที่เกี่ยวข้อง:\n" + "\n".join([f"• {c}" for c in cats])

def smalltalk() -> str:
    return f"สวัสดีค่ะ หนู {BOT_NAME} ยินดีดูแลคุณลูกค้านะคะ ✨ สนใจสินค้าอะไรอยู่คะ"

def unknown(q: str) -> str:
    hint = "เช่น “ราคา + ชื่อสินค้า”, “ค่าส่ง + ชื่อสินค้า”, หรือ “สเปก + ชื่อสินค้า”"
    return f"หนูยังไม่แน่ใจคำถามเลยค่ะ ลองพิมพ์ระบุสินค้า/รุ่นให้ชัดขึ้นได้ไหมคะ 🙂\n{hint}\nหากต้องการคุยกับทีมงานกด: {ESCALATE_LABEL}"

def generate_reply(user_text: str) -> str:
    intent = classify_intent(user_text or "")
    prods = ExcelCache.find(user_text or "")

    if intent == "ask_price":
        return ask_price(prods)
    if intent == "ask_shipping":
        return ask_shipping(prods)
    if intent == "ask_spec":
        return ask_spec(prods)
    if intent == "ask_category":
        return ask_category(prods)
    if intent == "smalltalk":
        return smalltalk()
    return unknown(user_text or "")
