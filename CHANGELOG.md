# Changelog

## 1.0.1 — 9 พ.ย. 2569

- README: วิธีใช้ทีละขั้นสำหรับคนเพิ่งโหลด พร้อมรูปของทุกขั้นจากบ้านทดลองในคลิป EP6 (`docs/images/`) · ตาราง prompt ไว้ก๊อป ·
  วิธีกดเองใน Google Flow · prompt ภาษาอังกฤษที่ Claude ส่งให้ AI · ตารางปัญหาที่เจอบ่อย
- Skill ไม่เปลี่ยน: ไม่ต้องอัปเดตตัวที่ลงไว้แล้ว

## 1.0.0 — 8 พ.ย. 2569

ตัวแรก จากงานจริงบ้านชั้นเดียว 9 จุด (ภายนอก โรงจอดรถ และ 7 ห้อง)

- มุมกล้องแบบภาพถ่ายตกแต่งภายใน (`references/camera-rules.md`) และ `cameras.json` ไฟล์เดียวใช้ได้ทุก pass
- `scripts/cameras.py` ภาพปกติ / ดินน้ำมัน · `scripts/idmap.py` Material ID map + ตารางสี · `scripts/plan_map.py` ผังสำหรับแผนที่
- ทำภาพ/คลิปได้ 2 ทาง: Kling ผ่าน MCP หรือ Google Flow บนเว็บ (ข้อมูลโควตาฟรี ณ 8 พ.ย. 2569)
- ตรวจเส้นแดง `scripts/overlay.sh` และตารางสิ่งที่ AI แอบเปลี่ยนพร้อมวิธีแก้ (`references/checking.md`)
- หน้าเว็บแผนที่แบบเกม `walkthrough/index.html` (อ่านห้องจาก `plan.js`)
- ห้องตัวอย่าง `examples/sample_room.py` สำหรับทดสอบหลังติดตั้ง
