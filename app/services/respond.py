from app.utils.excel_loader import DATA

def normalize(text: str) -> str:
    return str(text).strip().lower()

def search_products(message: str):
    message_norm = normalize(message)
    results = []

    for sheet_name, df in DATA.items():
        for _, row in df.iterrows():
            keywords = [
                str(row.get("ชื่อสินค้าในระบบขาย", "")),
                str(row.get("ชื่อสินค้าที่มักถูกเรียก", "")),
                str(row.get("หมวดหมู่", "")),
            ]
            if any(k and normalize(k) in message_norm for k in keywords):
                results.append({
                    "name": row.get("ชื่อสินค้าในระบบขาย", ""),
                    "price": row.get("ราคาขาย", row.get("ราคาเต็ม", "")),
                    "size": row.get("ขนาด", ""),
                    "sheet": sheet_name
                })
    return results

def generate_reply(user_message: str) -> str:
    products = search_products(user_message)

    if products:
        reply_lines = ["สวัสดีค่ะ คุณลูกค้า 😊", "นี่คือสินค้าที่เรามีค่ะ:\n"]
        for i, p in enumerate(products, 1):
            line = f"{i}. {p['name']} ราคา {p['price']} บาท"
            if p["size"]:
                line += f" (ขนาด {p['size']})"
            reply_lines.append(line)
        reply_lines.append("\nคุณลูกค้าสนใจดูรายละเอียดรุ่นไหนเพิ่มเติมคะ? 😃")
        return "\n".join(reply_lines)

    return (
        "สวัสดีค่ะ คุณลูกค้า 😊 ตอนนี้ยังไม่พบข้อมูลสินค้าที่คุณถามมา\n"
        "รบกวนแจ้งชื่อสินค้าให้ละเอียดขึ้น หรือพิมพ์คุยกับแอดมินได้เลยค่ะ 🙏"
    )
