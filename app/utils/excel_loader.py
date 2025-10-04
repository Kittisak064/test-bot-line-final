import os
import pandas as pd

EXCEL_PATH = "./app/data/อีกครั้ง.xlsx"

def _load_all():
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"ไม่พบไฟล์ Excel ที่ {EXCEL_PATH}")

    # โหลดทุกชีทในไฟล์
    all_sheets = pd.read_excel(EXCEL_PATH, sheet_name=None)

    data = {}
    for sheet, df in all_sheets.items():
        df = df.fillna("")  # กันค่า NaN
        data[sheet] = df
    return data

# preload
DATA = _load_all()
