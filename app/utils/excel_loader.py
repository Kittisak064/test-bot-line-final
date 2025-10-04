import os
from dataclasses import dataclass
from typing import List, Optional, Dict
from openpyxl import load_workbook
import time

EXCEL_FILE = os.getenv("EXCEL_FILE", "./data/เทสบอท รอบท้าย_UPGRADED.xlsx")

COLS = [
    "รหัสสินค้าในระบบขาย",
    "ชื่อสินค้าในระบบขาย",
    "ชื่อสินค้าที่มักถูกเรียก",
    "ขนาด",
    "หน่วย",
    "ราคาเต็ม",
    "ราคาขาย",
    "ราคาค่าขนส่ง",
    "หมวดหมู่",
]
SHEET_NAME = "ข้อมูลสินค้าและราคา"

@dataclass
class Product:
    sku: str
    name: str
    alias: str
    size: str
    unit: str
    list_price: Optional[float]
    sale_price: Optional[float]
    shipping_fee: Optional[float]
    category: str

class ExcelCache:
    _last_loaded = 0.0
    _ttl = 300  # seconds
    _products: List[Product] = []

    @classmethod
    def load(cls):
        now = time.time()
        if cls._products and now - cls._last_loaded < cls._ttl:
            return
        if not os.path.exists(EXCEL_FILE):
            raise RuntimeError(f"ไม่พบไฟล์ Excel: {EXCEL_FILE}")
        wb = load_workbook(EXCEL_FILE, data_only=True)
        if SHEET_NAME not in wb.sheetnames:
            raise RuntimeError(f"ไม่พบชีท '{SHEET_NAME}' ในไฟล์ {EXCEL_FILE}")
        ws = wb[SHEET_NAME]

        # Read headers from first row
        header_cells = next(ws.iter_rows(min_row=1, max_row=1))
        headers = [c.value if c.value is not None else "" for c in header_cells]

        # Build index map for required columns
        idx: Dict[str, int] = {}
        for col_name in COLS:
            if col_name in headers:
                idx[col_name] = headers.index(col_name)

        missing = [c for c in COLS if c not in idx]
        if missing:
            raise RuntimeError(f"หัวคอลัมน์หาย: {missing}")

        products: List[Product] = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not any(row):
                continue
            def get(col):
                i = idx[col]
                return row[i] if i < len(row) else None
            p = Product(
                sku=str(get("รหัสสินค้าในระบบขาย") or "").strip(),
                name=str(get("ชื่อสินค้าในระบบขาย") or "").strip(),
                alias=str(get("ชื่อสินค้าที่มักถูกเรียก") or "").strip(),
                size=str(get("ขนาด") or "").strip(),
                unit=str(get("หน่วย") or "").strip(),
                list_price=float(get("ราคาเต็ม")) if get("ราคาเต็ม") not in (None, "") else None,
                sale_price=float(get("ราคาขาย")) if get("ราคาขาย") not in (None, "") else None,
                shipping_fee=float(get("ราคาค่าขนส่ง")) if get("ราคาค่าขนส่ง") not in (None, "") else None,
                category=str(get("หมวดหมู่") or "").strip(),
            )
            if p.sku or p.name:
                products.append(p)

        cls._products = products
        cls._last_loaded = now

    @classmethod
    def all_products(cls) -> List[Product]:
        cls.load()
        return cls._products

    @classmethod
    def find(cls, q: str) -> List[Product]:
        cls.load()
        t = (q or "").lower()
        out = []
        for p in cls._products:
            if p.sku and p.sku.lower() in t: out.append(p)
            elif p.name and p.name.lower() in t: out.append(p)
            elif p.alias and p.alias.lower() in t: out.append(p)
        if not out:
            for p in cls._products:
                if p.sku and t in p.sku.lower(): out.append(p)
                elif p.name and t in p.name.lower(): out.append(p)
                elif p.alias and t in p.alias.lower(): out.append(p)
        return out

    @classmethod
    def top_k(cls, k=5) -> List[Product]:
        cls.load()
        return cls._products[:k]
