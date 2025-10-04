from app.utils.excel_loader import load_all, search_products

def test_load():
    data = load_all()
    assert isinstance(data, dict)
    assert "_raw" in data

def test_product_search():
    data = load_all()
    res = search_products(data, "รถเข็น")
    assert isinstance(res, list)
