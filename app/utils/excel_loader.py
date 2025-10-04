import os
from typing import List, Dict, Any
from openpyxl import load_workbook

EXCEL_PATH = "app/data/อีกครั้ง.xlsx"

# ===== Helpers =====
def _safe_str(v) -> str:
    return "" if v is None else str(v).strip()

def _contains(hay: str, needle: str) -> bool:
    return _safe_str(needle).lower() in _safe_str(hay).lower()

def _sheet_to_records(ws) -> List[Dict[str, Any]]:
    """
    แปลงแผ่นงาน openpyxl ให้เป็น list[dict] โดยใช้แถวแรกเป็น header (ภาษาไทย)
    """
    rows = list(ws.rows)
    if not rows:
        return []
    headers = [ _safe_str(c.value) for c in rows[0] ]
    records: List[Dict[str, Any]] = []
    for r in rows[1:]:
        rec = {}
        for h, c in zip(headers, r):
            rec[h] = c.value
        records.append(rec)
    return records

# ===== Loader =====
def _load_all() -> Dict[str, List[Dict[str, Any]]]:
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"ไม่พบไฟล์ Excel ที่ {EXCEL_PATH}")
    wb = load_workbook(EXCEL_PATH, data_only=True)

    data: Dict[str, List[Dict[str, Any]]] = {}

    # อ่านเฉพาะชีทที่คาดว่าจะมี; ถ้าไม่มีจะข้าม (ไม่พัง)
    maybe_sheets = [
        "ข้อมูลสินค้าและราคา",
        "โปรโมชั่น",
        "FAQ",
        "Intent Instruction – ก่อนขาย",
        "Intent Instruction – หลังขาย",
        # ถ้ามีชีทอื่น ๆ ก็เพิ่มได้ในอนาคต
    ]
    for name in maybe_sheets:
        if name in wb.sheetnames:
            ws = wb[name]
            data[name] = _sheet_to_records(ws)
        else:
            data[name] = []  # ไม่มีชีทนี้ก็เก็บเป็นลิสต์ว่าง

    return data

DATA = _load_all()

# ===== Public Queries =====
def search_products(query: str) -> List[Dict[str, Any]]:
    """
    ค้นหาสินค้าจากชีท 'ข้อมูลสินค้าและราคา'
    ใช้หัวคอลัมน์ภาษาไทยตามที่คุณให้:
      - รหัสสินค้าในระบบขาย
      - ชื่อสินค้าในระบบขาย
      - ชื่อสินค้าที่มักถูกเรียก
      - ขนาด
      - หน่วย
      - ราคาเต็ม
      - ราคาขาย
      - ราคาค่าขนส่ง
      - หมวดหมู่
    """
    rows = DATA.get("ข้อมูลสินค้าและราคา", [])
    q = _safe_str(query)
    results: List[Dict[str, Any]] = []
    for r in rows:
        name = _safe_str(r.get("ชื่อสินค้าในระบบขาย"))
        alias = _safe_str(r.get("ชื่อสินค้าที่มักถูกเรียก"))
        code = _safe_str(r.get("รหัสสินค้าในระบบขาย"))
        cat  = _safe_str(r.get("หมวดหมู่"))

        if any([_contains(name, q), _contains(alias, q), _contains(code, q), _contains(cat, q)]):
            results.append(r)
    return results

def list_promotions() -> List[Dict[str, Any]]:
    """
    คืนรายการโปรโมชันทั้งหมดจากชีท 'โปรโมชั่น'
    รูปแบบคอลัมน์ขึ้นกับชีทของคุณ—โค้ดนี้ไม่บังคับชื่อหัวคอลัมน์
    """
    return DATA.get("โปรโมชั่น", [])

def search_faq(query: str) -> List[Dict[str, Any]]:
    """
    ค้นหา FAQ จากชีท 'FAQ'
    คาดหวังคอลัมน์อย่างน้อย: 'คำถาม', 'คำตอบ'
    """
    rows = DATA.get("FAQ", [])
    q = _safe_str(query)
    results: List[Dict[str, Any]] = []
    for r in rows:
        q_text = _safe_str(r.get("คำถาม"))
        a_text = _safe_str(r.get("คำตอบ"))
        if _contains(q_text, q) or _contains(a_text, q):
            results.append(r)
    return results

def list_intent_instructions() -> Dict[str, List[Dict[str, Any]]]:
    """
    คืนคำสั่ง Intent สำหรับ 'ก่อนขาย' และ 'หลังขาย' เพื่อให้ LLM ประกอบคำตอบ (ถ้ามี)
    โครงสร้างภายในชีทคุณสามารถกำหนดเองได้—โค้ดนี้จะคืนทั้งแถวให้คุณ
    """
    return {
        "before": DATA.get("Intent Instruction – ก่อนขาย", []),
        "after":  DATA.get("Intent Instruction – หลังขาย", []),
    }
