# app/utils/excel_loader.py
from __future__ import annotations
import os
from typing import List, Dict, Any
from openpyxl import load_workbook

EXCEL_PATH = os.getenv("FAQ_EXCEL_PATH", "./app/data/อีกครั้ง.xlsx")  # ปรับ path ได้จาก env

def _norm(s: str) -> str:
    return (s or "").strip().lower()

def load_products() -> List[Dict[str, Any]]:
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"ไม่พบไฟล์ Excel ที่ {EXCEL_PATH}")

    wb = load_workbook(EXCEL_PATH, data_only=True)

    # ====== ชีท “ข้อมูลสินค้าและราคา” (คอลัมน์ภาษาไทยตามที่คุณให้)
    # รหัสสินค้าในระบบขาย | ชื่อสินค้าในระบบขาย | ชื่อสินค้าที่มักถูกเรียก | ขนาด | หน่วย | ราคาเต็ม | ราคาขาย | ราคาค่าขนส่ง | หมวดหมู่
    ws = wb["ข้อมูลสินค้าและราคา"]

    headers = {cell.value: idx for idx, cell in enumerate(next(ws.iter_rows(min_row=1, max_row=1))[0:50])}
    need_cols = [
        "รหัสสินค้าในระบบขาย","ชื่อสินค้าในระบบขาย","ชื่อสินค้าที่มักถูกเรียก",
        "ขนาด","หน่วย","ราคาเต็ม","ราคาขาย","ราคาค่าขนส่ง","หมวดหมู่"
    ]
    for col in need_cols:
        if col not in headers:
            raise ValueError(f"ชีท 'ข้อมูลสินค้าและราคา' ไม่มีคอลัมน์: {col}")

    products: List[Dict[str, Any]] = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or all(v in (None, "") for v in row):  # เว้นแถวว่าง
            continue
        item = {
            "sku": row[headers["รหัสสินค้าในระบบขาย"]],
            "name": (row[headers["ชื่อสินค้าในระบบขาย"]] or "").strip(),
            "aliases": [a.strip() for a in str(row[headers["ชื่อสินค้าที่มักถูกเรียก"]] or "").split(",") if a.strip()],
            "size": (row[headers["ขนาด"]] or ""),
            "unit": (row[headers["หน่วย"]] or ""),
            "price_list": row[headers["ราคาเต็ม"]],
            "price_sell": row[headers["ราคาขาย"]],
            "ship_cost": row[headers["ราคาค่าขนส่ง"]],
            "category": (row[headers["หมวดหมู่"]] or "").strip(),
        }
        # สำหรับค้นหาแบบง่าย
        item["keywords"] = {_norm(item["name"])} | {_norm(a) for a in item["aliases"]}
        products.append(item)

    # ====== (ถ้ามี) โปรโมชัน / คำถามพบบ่อย / วิธีใช้ ฯลฯ เพิ่มเติมในอนาคต
    # แค่สร้างชีทใหม่ตามที่วางแผนไว้ ชื่อคอลัมน์ไทย แล้วเพิ่ม parser คล้ายๆ กัน

    return products

def load_all() -> Dict[str, Any]:
    return {
        "products": load_products(),
    }

# โหลดไว้ล่วงหน้าเพื่อลดดีเลย์
DATA = load_all()

def search_products(text: str, top_k: int = 3) -> List[Dict[str, Any]]:
    q = _norm(text)
    if not q:
        return []
    hits = []
    for p in DATA["products"]:
        score = 0
        # ตรงชื่อ/alias
        if any(k and k in q for k in p["keywords"]):
            score += 3
        # หมวดหมู่
        if p["category"] and _norm(p["category"]) in q:
            score += 1
        # คำว่ารุ่น/ขนาดตัวเลขในข้อความ
        if p["size"] and str(p["size"]).lower() in q:
            score += 1
        if score > 0:
            hits.append((score, p))
    hits.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in hits[:top_k]]
