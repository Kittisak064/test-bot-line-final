from app.services.utils.excel_loader import find_product

async def generate_reply(user_text: str) -> str:
    # 1) หาสินค้า
    product = find_product(user_text)
    if product:
        return (
            f"📦 {product['ชื่อสินค้าในระบบขาย']}\n"
            f"💡 ขนาด: {product['ขนาด']} {product['หน่วย']}\n"
            f"💰 ราคาเต็ม: {product['ราคาเต็ม']} | ราคาขาย: {product['ราคาขาย']}\n"
            f"🚚 ค่าขนส่ง: {product['ราคาค่าขนส่ง']}\n"
            f"🏷️ หมวดหมู่: {product['หมวดหมู่']}"
        )

    # 2) ถ้าไม่เจอสินค้า → ตอบ fallback
    return "❓ ขออภัยค่ะ ฟักแฟงยังหาสินค้านี้ไม่เจอ คุณลูกค้าลองพิมพ์ชื่อสินค้าที่ถูกต้องอีกครั้งนะคะ 💕"
