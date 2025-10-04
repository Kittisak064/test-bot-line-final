# LINE Excel Chatbot

บอท LINE ที่อ่านข้อมูลจากไฟล์ Excel ใน repo โดยตรง (ไม่ใช้ Google API)
- ชื่อชีท: **ข้อมูลสินค้าและราคา**
- หัวคอลัมน์ (ต้องตรงตามนี้):
  `รหัสสินค้าในระบบขาย, ชื่อสินค้าในระบบขาย, ชื่อสินค้าที่มักถูกเรียก, ขนาด, หน่วย, ราคาเต็ม, ราคาขาย, ราคาค่าขนส่ง, หมวดหมู่`

## Run (Local/Mac)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export EXCEL_FILE=./data/เทสบอท รอบท้าย_UPGRADED.xlsx
uvicorn app.main:app --reload --port 8000
```

## Deploy (Render)
- Push โปรเจกต์ขึ้น GitHub
- Create Web Service → Render จะอ่าน `render.yaml` (Python 3.10.14)
- ตั้ง ENV: `LINE_CHANNEL_SECRET`, `LINE_CHANNEL_ACCESS_TOKEN`, `EXCEL_FILE=./data/เทสบอท รอบท้าย_UPGRADED.xlsx`
- LINE Webhook URL: `https://<your-app>.onrender.com/webhook/line`

## Intent ที่รองรับ
- ราคา (`ราคา/เท่าไร/กี่บาท/โปร`)
- ค่าส่ง (`ค่าส่ง/ขนส่ง/ส่งฟรี`)
- สเปก (`สเปก/ขนาด/วิธีใช้/ชาร์จ`)
- หมวด (`หมวด/ประเภท`)
- small talk
```
