# LINE Excel Chatbot (Grounded by Excel + OpenAI)

## Quick Start
1) ใส่ข้อมูลใน `data/เทสบอท รอบท้าย.xlsx` (หัวคอลัมน์เป็นภาษาไทยตามที่ให้มา)
2) สร้างไฟล์ `.env` จาก `.env.example` และใส่ค่า LINE/OPENAI
3) รันบนเครื่อง:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
4) Render: push repo แล้ว deploy (มี `render.yaml` แล้ว)
5) ตั้ง Webhook LINE: `https://<your-service>.onrender.com/webhook/line`

## Columns (ต้องมีตรงตัว)
- รหัสสินค้าในระบบขาย
- ชื่อสินค้าในระบบขาย
- ชื่อสินค้าที่มักถูกเรียก
- ขนาด
- หน่วย
- ราคาเต็ม
- ราคาขาย
- ราคาค่าขนส่ง
- หมวดหมู่
