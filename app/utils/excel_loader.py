import os
from openpyxl import load_workbook

# path ไฟล์ Excel
EXCEL_PATH = "./data/อีกครั้ง.xlsx"

def _load_sheet(sheet):
    """
    อ่านข้อมูลจากชีท Excel → list[dict]
    โดยใช้ row แรกเป็น header
    """
    rows = list(sheet.rows)
    if not rows:
        return []

    headers = [str(c.value).strip() if c.value else "" for c in rows[0]]
    data = []

    for row in rows[1:]:
        row_data = {}
        for i, cell in enumerate(row):
            key = headers[i] if i < len(headers) else f"col_{i}"
            row_data[key] = cell.value
        # ข้าม row ที่ว่างทั้งหมด
        if any(v not in [None, ""] for v in row_data.values()):
            data.append(row_data)

    return data


def load_all():
    """
    โหลดข้อมูลทุกชีทจากไฟล์ Excel
    return dict เช่น:
    {
      "ข้อมูลสินค้าและราคา": [...],
      "โปรโมชั่น": [...],
      "FAQ": [...],
      "Intent": [...]
    }
    """
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"ไม่พบไฟล์ Excel ที่ {EXCEL_PATH}")

    wb = load_workbook(EXCEL_PATH, data_only=True)
    data = {}

    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        data[sheet_name] = _load_sheet(sheet)

    return data


# โหลดครั้งเดียวตอน import
DATA = load_all()

# ฟังก์ชันช่วยค้นหาข้อมูล
def get_sheet(sheet_name: str):
    """คืนค่าข้อมูลชีทตามชื่อ"""
    return DATA.get(sheet_name, [])

def search_product(keyword: str):
    """ค้นหาสินค้าจากชื่อ / ชื่อเรียก / รหัส"""
    products = get_sheet("ข้อมูลสินค้าและราคา")
    results = []
    for p in products:
        text_all = " ".join([str(v) for v in p.values() if v])
        if keyword.lower() in text_all.lower():
            results.append(p)
    return results

def search_faq(keyword: str):
    """ค้นหา FAQ โดยเช็คทั้งคำถาม/คำตอบ"""
    faqs = get_sheet("FAQ")
    results = []
    for f in faqs:
        text_all = " ".join([str(v) for v in f.values() if v])
        if keyword.lower() in text_all.lower():
            results.append(f)
    return results
