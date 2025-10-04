from typing import Literal

# Intent classifier แบบกฎง่าย ๆ
def classify_intent(text: str) -> Literal["ask_price","ask_shipping","ask_spec","ask_category","smalltalk","unknown"]:
    t = (text or "").lower()
    kw_price = ["ราคา","เท่าไร","กี่บาท","ถูกสุด","แพงสุด","ลดไหม","โปร","โปรโมชัน","promotion"]
    kw_ship  = ["ค่าส่ง","ขนส่ง","ส่งฟรี","ค่าขนส่ง","จัดส่ง"]
    kw_spec  = ["สเปก","ขนาด","ชาร์จ","วิธีใช้","รับน้ำหนัก","หน่วย","แรง","รายละเอียด"]
    kw_cat   = ["หมวด","ประเภท","กลุ่มสินค้า"]
    kw_small = ["สวัสดี","ขอบคุณ","ทดสอบ","hello","hi","เฮลโหล"]

    if any(k in t for k in kw_price): return "ask_price"
    if any(k in t for k in kw_ship):  return "ask_shipping"
    if any(k in t for k in kw_spec):  return "ask_spec"
    if any(k in t for k in kw_cat):   return "ask_category"
    if any(k in t for k in kw_small): return "smalltalk"
    return "unknown"
