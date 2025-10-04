import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
EXCEL_PATH = os.path.join(BASE_DIR, "data", "เทสบท รอบท้าย_UPGRADED.xlsx")

# โหลด Excel เข้าหน่วยความจำ
def load_excel_data():
    try:
        df = pd.read_excel(EXCEL_PATH)
        return df.fillna("")
    except Exception as e:
        print(f"❌ Error loading Excel: {e}")
        return pd.DataFrame()

# เก็บข้อมูลใน memory
PRODUCTS_DF = load_excel_data()

# ค้นหาสินค้าตามชื่อที่พิมพ์มา
def find_product(query: str):
    if PRODUCTS_DF.empty:
        return None
    
    for _, row in PRODUCTS_DF.iterrows():
        if query in str(row["ชื่อสินค้าในระบบขาย"]) or query in str(row["ชื่อสินค้าที่มักถูกเรียก"]):
            return row.to_dict()
    return None
