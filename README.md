# LINE Excel Chatbot (Multi-Sheet, Grounded, No Hallucination)

- ใช้ไฟล์ Excel **ของคุณ**: `data/อีกครั้ง.xlsx` เป็นฐานข้อมูลหลายชีท (ไม่เปลี่ยนชื่อชีท/หัวคอลัมน์เดิม)
- บอทจะอ่านชีท: **ข้อมูลสินค้าและราคา, FAQ, Promotion, ข้อมูลบริษัท, บุคลิกน้อง A.I., Knowledge_Base, Orders, Service_Record, Config, Training Doc** (ถ้ามี)
- Render พร้อมใช้งานด้วย `render.yaml` (บังคับ Python 3.10.14)
- ไม่ใช้ pandas → build ผ่านบน Render

## รัน Local (Mac)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Deploy Render
- push โค้ดขึ้น GitHub แล้วสร้าง Web Service ใหม่ (อ่าน `render.yaml` อัตโนมัติ)
- ตั้ง Webhook LINE = `https://<your-service>.onrender.com/webhook/line`

## ใช้ยังไง
- คุณแก้ไขข้อมูลใน Excel เท่านั้น (บอทอ่านทุกชีทที่ระบุ)
- ถ้าหัวคอลัมน์/ชีทมีเพิ่ม บอทจะพยายาม ingest อัตโนมัติเป็น knowledge เพิ่มเติม
