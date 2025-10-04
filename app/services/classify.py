from typing import Literal

Intent = Literal[
    "ถามสินค้า","ถามราคา","ถามค่าส่ง","ถามโปร",
    "ถามใช้งาน","ถามเงื่อนไข","ถามรับประกัน",
    "เช็กออเดอร์","เช็กพัสดุ","smalltalk","handover","unknown"
]

KEYS_PRICE = {"ราคา","เท่าไร","กี่บาท","โปร","ลด","ผ่อน","ส่วนลด"}
KEYS_SHIP  = {"ส่ง","ค่าส่ง","ขนส่ง","เก็บปลายทาง","ส่งฟรี","ดิลิเวอรี่"}
KEYS_PROMO = {"โปร","โปรโมชั่น","โค้ด","คูปอง"}
KEYS_USE   = {"ใช้งาน","วิธีใช้","คู่มือ","ชาร์จ","แบต","ดูแล","บำรุง"}
KEYS_WAR   = {"ประกัน","เคลม","ซ่อม","ศูนย์","เซอร์วิส"}
KEYS_ORDER = {"ออเดอร์","สั่งซื้อ","ใบสั่ง","เลขออเดอร์","สถานะคำสั่งซื้อ"}
KEYS_TRACK = {"เลขพัสดุ","พัสดุ","tracking","ขนส่ง"} 
KEYS_HAND  = {"แอดมิน","พนักงาน","ติดต่อ","โทร","คุยกับคน","ขอคุยกับแอดมิน"}

def classify(text: str) -> Intent:
    t = (text or "").lower()
    if any(k in t for k in KEYS_HAND):  return "handover"
    if any(k in t for k in KEYS_PROMO): return "ถามโปร"
    if any(k in t for k in KEYS_SHIP):  return "ถามค่าส่ง"
    if any(k in t for k in KEYS_PRICE): return "ถามราคา"
    if any(k in t for k in KEYS_USE):   return "ถามใช้งาน"
    if any(k in t for k in KEYS_WAR):   return "ถามรับประกัน"
    if any(k in t for k in KEYS_TRACK): return "เช็กพัสดุ"
    if any(k in t for k in KEYS_ORDER): return "เช็กออเดอร์"
    if len(t) <= 2:                     return "unknown"
    return "ถามสินค้า"
