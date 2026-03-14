# Requirement.md - โปรเจกต์: สร้างสกิล Deep Web Reader

## 🎯 เป้าหมายหลัก
สร้าง Python Script สำหรับดึงข้อมูลหน้าเว็บแบบ **Zero-Dependency** ผ่าน **Browserless API** โดยเน้นความปลอดภัยและประสิทธิภาพในการดึงข้อมูลจากเว็บที่ซับซ้อน (เช่น LinkedIn)

## 🛠️ ข้อกำหนดทางเทคนิค (Technical Requirements)
1. **ภาษา:** Python 3.x
2. **Library:** ใช้ไลบรารีมาตรฐานเท่านั้น (Standard Library) ห้ามใช้ไลบรารีภายนอกที่ต้องติดตั้งผ่าน `pip install`
   - แนะนำ: `urllib.request`, `json`, `os`, `re`, `html`
3. **API Integration:**
   - ดึงข้อมูลผ่าน **Browserless API** (ใช้ endpoint `/content` หรือ `/scrape`)
   - อ่านค่าการเชื่อมต่อจาก Environment Variables เท่านั้น:
     - `BROWSERLESS_HOST`: URL ของ Browserless (เช่น `https://chrome.browserless.io`)
     - `BROWSERLESS_TOKEN`: API Token สำหรับใช้งาน
4. **Data Cleaning:**
   - ใช้ `re` และ `html.unescape` เพื่อคลีนแท็ก HTML ให้เหลือแต่ Text ที่อ่านง่าย
5. **Security:**
   - **ห้าม Hardcode** รหัสผ่านหรือ Token ลงในโค้ดเด็ดขาด
   - โค้ดต้องพร้อมสำหรับการทำเป็น Open Source

## 📝 ภารกิจของทีมงาน (Task Breakdown)

### Step 2: พี่โค้ด (Programmer) - ประเภท: Interactive
1. สร้างโฟลเดอร์ย่อย `/programmer/` ในโปรเจกต์
2. สร้างไฟล์ `deep_web_reader.py` ตามข้อกำหนดทางเทคนิค
3. **บล็อกทดสอบ (Main Block):**
   - ท้ายไฟล์ต้องมี `if __name__ == "__main__":`
   - สั่งรันเทสต์ดึงข้อมูลจาก URL LinkedIn (QA Jobs in Bangkok)
   - Print ผลลัพธ์ออกมา
4. **สร้าง SKILL.md:**
   - คู่มือการใช้งาน Tool นี้อย่างละเอียด
   - ระบุผู้สร้างคือ: **WalnutZtudio**

### Step 3: น้องเทส (QA) - ประเภท: Interactive
1. รับไม้ต่อจากพี่โค้ดเมื่อเขียนเสร็จ
2. รันสคริปต์ด้วยคำสั่ง `python3 .../programmer/deep_web_reader.py`
3. ตรวจสอบ Errors:
   - ถ้า Error → ส่ง Log กลับให้พี่โค้ดแก้
   - ถ้าผ่าน → ตรวจสอบความถูกต้องของข้อมูล (ต้องเห็นรายชื่อตำแหน่งงาน LinkedIn)
4. ส่งสถานะ **"PASSED"** กลับมาให้หยองกรอบ

### Step 4: สรุปงานและ Git (หยองกรอบ & พี่โค้ด)
1. หยองกรอบรายงานคุณนัทเมื่อน้องเทสให้สถานะ PASSED
2. คุณนัทตรวจสอบผลลัพธ์และอนุมัติขึ้น Git
3. พี่โค้ดรันคำสั่ง: `git init`, `git add .`, `git commit -m "feat: Initial commit for Deep Web Reader by WalnutZtudio"`
4. หยองกรอบสรุปผลลัพธ์สุดท้ายและรอคำสั่งรีโมท GitHub URL

---
**จัดทำโดย:** พ่อบ้าน หยองกรอบ
**สถานะ:** กำลังดำเนินการ (Step 1 Complete)
