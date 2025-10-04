import os
from app.utils.excel_loader import ExcelCache

def test_excel_load():
    assert os.path.exists(os.getenv("EXCEL_FILE", "./data/เทสบอท รอบท้าย_UPGRADED.xlsx"))
    products = ExcelCache.all_products()
    assert isinstance(products, list)
