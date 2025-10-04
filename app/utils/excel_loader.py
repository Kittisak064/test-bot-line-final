import os, datetime, re
from typing import Dict, List, Any, Optional
from openpyxl import load_workbook

EXCEL_PATH = os.getenv("EXCEL_FILE", "./data/อีกครั้ง.xlsx")

def _sheet_dicts(ws) -> List[Dict[str, Any]]:
    rows = list(ws.iter_rows(values_only=True))
    if not rows: return []
    headers = [str(h).strip() if h is not None else "" for h in rows[0]]
    out = []
    for r in rows[1:]:
        if r is None or all(v is None for v in r): 
            continue
        rec = {}
        for i, h in enumerate(headers):
            if not h: 
                continue
            val = r[i] if i < len(r) else None
            if isinstance(val, datetime.datetime):
                val = val.date()
            rec[h] = "" if val is None else str(val).strip()
        # skip full empty dict
        if any(str(v).strip() for v in rec.values()):
            out.append(rec)
    return out

def load_all() -> Dict[str, Any]:
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"ไม่พบไฟล์ Excel ที่ {EXCEL_PATH}")
    wb = load_workbook(EXCEL_PATH, data_only=True)

    data: Dict[str, Any] = {"_raw": {}}
    for name in wb.sheetnames:
        ws = wb[name]
        data["_raw"][name] = _sheet_dicts(ws)

    # Convenience views
    data["products"] = data["_raw"].get("ข้อมูลสินค้าและราคา", [])
    data["faq"] = data["_raw"].get("FAQ", [])
    data["promotions"] = data["_raw"].get("Promotion", [])
    data["company"] = data["_raw"].get("ข้อมูลบริษัท", [])
    data["persona"] = data["_raw"].get("บุคลิกน้อง A.I.", [])
    data["knowledge"] = data["_raw"].get("Knowledge_Base", [])
    data["orders"] = data["_raw"].get("Orders", [])
    data["service"] = data["_raw"].get("Service_Record", [])
    data["config"] = data["_raw"].get("Config", [])
    data["training"] = data["_raw"].get("Training Doc", [])

    return data

def _contains(hay: str, needle: str) -> bool:
    return needle in hay

def search_products(DATA: Dict[str, Any], query: str) -> List[Dict[str,str]]:
    q = (query or "").lower()
    res = []
    for p in DATA.get("products", []):
        text = " ".join([
            p.get("รหัสสินค้าในระบบขาย",""),
            p.get("ชื่อสินค้าในระบบขาย",""),
            p.get("ชื่อสินค้าที่มักถูกเรียก",""),
            p.get("หมวดหมู่",""),
        ]).lower()
        if _contains(text, q):
            res.append(p)
    return res

def search_faq(DATA: Dict[str, Any], query: str) -> Optional[Dict[str,str]]:
    q = (query or "").lower()
    for row in DATA.get("faq", []):
        keys = " ".join([row.get("คำถาม",""), row.get("คีย์เวิร์ด","")]).lower()
        if q and q in keys:
            return row
    # fallback: simple contains on answer
    for row in DATA.get("faq", []):
        if q in (row.get("คำตอบ","").lower()):
            return row
    return None

def active_promotions_text(DATA: Dict[str, Any], today: Optional[datetime.date] = None) -> str:
    today = today or datetime.date.today()
    lines = []
    for promo in DATA.get("promotions", []):
        start = promo.get("วันที่เริ่ม","")
        end   = promo.get("วันที่สิ้นสุด","")
        # we keep as text to avoid date parsing pitfalls
        line = f"- {promo.get('ชื่อโปรโมชั่น','')}: {promo.get('รายละเอียด','')} (เงื่อนไข: {promo.get('เงื่อนไข','')}, ช่วง: {start} - {end})"
        lines.append(line)
    return "\n".join(lines) if lines else "(ยังไม่มีโปรโมชันในระบบ)"

def company_info_text(DATA: Dict[str, Any]) -> str:
    parts = []
    for row in DATA.get("company", []):
        h = row.get("หัวข้อ","")
        d = row.get("รายละเอียด","")
        if h or d:
            parts.append(f"{h}: {d}")
    return "\\n".join(parts)

def persona_text(DATA: Dict[str, Any]) -> str:
    # Concatenate persona details
    texts = []
    for row in DATA.get("persona", []):
        h = row.get("หัวข้อ","")
        d = row.get("รายละเอียด","")
        if h or d:
            texts.append(f"{h}: {d}")
    return "\\n".join(texts)

def search_knowledge(DATA: Dict[str, Any], query: str) -> Optional[Dict[str,str]]:
    q = (query or "").lower()
    for row in DATA.get("knowledge", []):
        blob = " ".join([row.get("หมวดหมู่",""), row.get("หัวข้อ",""), row.get("เนื้อหา/คำแนะนำ","")]).lower()
        if q in blob:
            return row
    return None

def find_order_status(DATA: Dict[str, Any], query: str) -> Optional[Dict[str,str]]:
    q = (query or "").lower()
    for row in DATA.get("orders", []):
        # Try common keys seen in the sheet end headers
        keys = []
        for k in row.keys():
            v = str(row.get(k,""))
            if v:
                keys.append(v.lower())
        if any(q in v for v in keys if q):
            # Return only useful status fields
            pick = {}
            for k in row.keys():
                if any(x in k for x in ["สถานะ","วันที่สั่งซื้อ","เลขพัสดุ","Carrier","ราคารวม","จำนวน","สินค้า","รหัส"]):
                    pick[k] = row.get(k,"")
            return pick
    return None

def find_service_status(DATA: Dict[str, Any], query: str) -> Optional[Dict[str,str]]:
    q = (query or "").lower()
    for row in DATA.get("service", []):
        blob = " ".join([row.get("รหัสเคส",""), row.get("Serial Number",""), row.get("ลูกค้า",""), row.get("สถานะการซ่อม","")]).lower()
        if q in blob:
            return row
    return None
