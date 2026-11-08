# nuea.ai House Render — Skill render บ้านให้สมจริงจาก Blender ด้วย Claude

> **For Claude and other AI agents:** to install this skill, follow [INSTALL.md](INSTALL.md)
> (raw: https://raw.githubusercontent.com/HaNorthRich/nuea-ai-house-render-skill/main/INSTALL.md).

จากโมเดล Blender ที่ยังดูเป็นเกม → ภาพและคลิปบ้านที่ดูเหมือนถ่ายจริง โดย**คงผนัง ประตู หน้าต่างไว้ที่เดิม**
แล้วได้หน้าเว็บแผนที่แบบเกม คลิกห้องไหนก็ไปห้องนั้น

## ติดตั้งง่ายที่สุด: ให้ Claude ลงให้

1. ลง [Blender](https://www.blender.org/download/) (4.2 ขึ้นไป) และเปิด [Claude Code](https://claude.com/claude-code)
   Claude Code ใช้กับแพ็กเกจเสียเงินของ Claude (Pro ขึ้นไป) หรือ API key แพ็กเกจฟรีใช้ไม่ได้ (ณ พ.ย. 2569 · [ดูแพ็กเกจ](https://claude.com/pricing))
2. ส่งข้อความนี้ให้ Claude

   ```
   ลง Skill นี้ให้หน่อย https://github.com/HaNorthRich/nuea-ai-house-render-skill
   ```

3. Claude จะเช็ก Blender และ ffmpeg ลง Skill แล้วถามว่าจะทำภาพด้วย **Kling** (เสียเงิน ทำให้อัตโนมัติ)
   หรือ **Google Flow** (มีโควตาฟรีรายวัน คุณกดเองบนเว็บ) ตามขั้นตอนใน [INSTALL.md](INSTALL.md)
   ในโหมดปกติ Claude Code จะขอให้คุณกดอนุญาตก่อนรันแต่ละคำสั่ง อ่านคำสั่งก่อนกด Allow
4. ตอนจบ Claude จะทดสอบกับห้องตัวอย่าง (ไม่เสียเครดิต) แล้วบอกสิ่งที่คุณต้องทำเอง

## Skill นี้ทำอะไร

| ขั้น | ได้อะไร |
|---|---|
| 1. มุมกล้องแบบภาพถ่ายตกแต่งภายใน | กล้องตั้งตรง เลนส์ 16–24 มม. สูง 1 เมตร จัดเฟรมที่หัวเตียง/โซฟา/โต๊ะ — Claude เสนอห้องละ 2 มุมให้เลือก |
| 2. ภาพ 3 แบบต่อมุม | ภาพปกติ · ภาพดินน้ำมัน (ไว้ทำปก before/after) · **Material ID map** สีเรียบบอกว่าพื้นผิวไหนเป็นวัสดุอะไร + ตารางสี |
| 3. ภาพสมจริง | ส่งภาพ + ID map + สไตล์ ให้ AI แต่งห้องเต็มแบบนิตยสาร ของที่เป็นกล่อง (ชักโครก ฝักบัว รถ) กลายเป็นของจริงที่ตำแหน่งเดิม |
| 4. ตรวจว่าเป็นบ้านหลังเดิม | ซ้อนเส้นขอบจาก Blender สีแดงบนภาพ AI ห้องไหน AI แอบเปลี่ยน รู้ทันที |
| 5. คลิป 5 วินาที | กล้องเคลื่อนไม่ซ้ำกันทุกห้อง |
| 6. แผนที่แบบเกม | หน้าเว็บไฟล์เดียว คลิกห้องบนผัง → จุดเดินไปตามทางเดิน → คลิปห้องนั้นเล่น · กด B ค้าง = ภาพ Blender มุมเดียวกัน |

**ทำไมต้องมี Material ID map:** ในบ้านทดลอง AI ขยับมุมกล้องเองและเปลี่ยนพื้นห้องน้ำ พอส่ง ID map ไปด้วย
เส้นแดงทับทุกเส้นตรง วัสดุวางถูกที่ตามสี

## ทำภาพ/คลิปได้ 2 ทาง

| | Kling (ผ่าน MCP) | Google Flow (บนเว็บ) |
|---|---|---|
| ค่าใช้จ่าย | เสียเงิน (ใช้เครดิต Kling) · ที่เราวัดได้บนแพ็กเกจ Standard (พ.ย. 2569): ภาพละ ~2–20 เครดิตตามรุ่น คลิป 5 วิ ~50 | มีโควตาฟรีรายวัน (ประมาณการ ณ 8 พ.ย. 2569): วิดีโอ ~3 ห้อง/วัน ที่ 720p ตามหน้าช่วยเหลือของ Google · ภาพหลายสิบภาพ/วัน ตามการทดสอบของบล็อกภายนอก (Google ไม่ได้ประกาศตัวเลขนี้) |
| ใครกด | Claude ทำให้ทั้งหมด | Claude เตรียมไฟล์ + prompt ให้ คุณอัปโหลดและกดเอง |
| ความละเอียดคลิป | 1080p | 720p (ฟรี) |

ตัวเลขในตารางนี้คือค่าที่เราวัดหรืออ่านได้ ณ พ.ย. 2569 ไม่ใช่ราคาหรือโควตาทางการ Kling และ Google เปลี่ยนได้ทุกเมื่อ
ดูเครดิตบนปุ่ม Generate (Flow) หรือยอดในบัญชี Kling ก่อนกดทุกครั้ง ค่าเครดิตที่ใช้ไปเป็นของบัญชีคุณเอง

## ลองสั่งแบบนี้

- `ทำภาพบ้านหลังนี้ให้สมจริง จัดมุมกล้องแบบภาพ Pinterest ทุกห้อง <path ของไฟล์ .blend>`
- `ทำ Material ID map ของทุกมุมกล้อง แล้วเตรียมไฟล์ไปทำต่อใน Google Flow`
- `เอาภาพสมจริงที่ได้ไปทำคลิป 5 วิ แล้วทำหน้าแผนที่แบบเกมให้หน่อย`

## ในชุดมีอะไร

| ที่อยู่ | คืออะไร |
|---|---|
| `nuea-ai-house-render/SKILL.md` | ขั้นตอนหลัก 7 ขั้นที่ Claude ทำตาม |
| `nuea-ai-house-render/references/` | กฎมุมกล้อง · prompt ที่ใช้ได้ผล · วิธีใช้ Kling · วิธีใช้ Google Flow · วิธีตรวจเส้นแดงและสิ่งที่ AI ชอบแอบเปลี่ยน |
| `nuea-ai-house-render/scripts/` | `cameras.py` (ภาพปกติ/ดินน้ำมัน) · `idmap.py` (Material ID map) · `plan_map.py` (ผังสำหรับแผนที่) · `overlay.sh` (ซ้อนเส้นแดง) · `_common.py` (ส่วนที่ 3 สคริปต์แรกใช้ร่วมกัน) |
| `nuea-ai-house-render/walkthrough/` | หน้าเว็บแผนที่แบบเกม |
| `nuea-ai-house-render/examples/` | ห้องตัวอย่างไว้ทดสอบหลังติดตั้ง |

## ข้อควรรู้

- ภาพที่ได้เป็น**ภาพจำลองจาก AI ไม่ใช่แบบก่อสร้างหรือรายการวัสดุ** ใช้ให้ลูกค้าเห็นภาพได้ แต่ต้องเทียบกับแบบทุกห้อง
  (AI แอบเติมของได้ เช่น หน้าต่างที่แบบไม่มี) อย่าแนบภาพนี้เป็นส่วนหนึ่งของสัญญาหรือสเปกงาน
- ถ้าใช้ในโฆษณาขายบ้าน/คอนโด ภาพถือเป็นข้อความโฆษณา: ของที่ไม่มีจริงในแบบ (หน้าต่าง ทางเดิน สวน วิว) ให้แก้ภาพออก
  การเขียนกำกับใช้แทนไม่ได้ · เฟอร์นิเจอร์และของตกแต่งที่ไม่รวมในราคา ให้เขียนกำกับบนภาพหรือติดภาพ
- ตอนโพสต์ให้เปิดป้ายเนื้อหา AI ของแพลตฟอร์ม (เช่น YouTube: Altered or synthetic content · Instagram/Facebook: ป้าย AI —
  ชื่อเมนูอาจเปลี่ยน) และใส่คำว่า "ภาพจำลองจาก AI" บนภาพด้วย เพราะป้ายของแพลตฟอร์มไม่ติดไปเมื่อภาพถูกส่งต่อใน LINE
  หรือโบรชัวร์ · อย่าตัดหรือลบลายน้ำของผู้ให้บริการ
- ภาพสไตล์ที่ใช้อ้างอิง ใช้เฉพาะรูปที่คุณมีสิทธิ์ใช้ (ถ่ายเอง ซื้อสิทธิ์ หรือเจ้าของอนุญาต) การอัปโหลดรูปของคนอื่นขึ้น
  Kling/Google ก็นับเป็นการทำสำเนาแล้ว และอย่าให้รูปนั้นติดในงานที่เผยแพร่
- ไฟล์ที่ส่งไป Kling หรือ Google จะอยู่บนเซิร์ฟเวอร์ของผู้ให้บริการตามเงื่อนไขของเขา ถ้าเป็นแบบบ้านของลูกค้า ให้ขออนุญาตลูกค้าก่อน
- สิทธิ์นำภาพ/คลิปไปใช้เชิงพาณิชย์ (โฆษณา ขายบ้าน งานลูกค้า) ขึ้นกับเงื่อนไขของ Kling/Google และแพ็กเกจที่คุณใช้
  ตรวจเงื่อนไขเองก่อนใช้ แพ็กเกจฟรีบางแบบไม่ให้สิทธิ์เชิงพาณิชย์
- คลิปเดินตามเส้นทางกล้อง เดินอิสระไม่ได้ (แผนที่ = เลือกห้องแล้วเล่นคลิป)
- Skill ออกแบบมาไม่ให้เซฟทับไฟล์ `.blend` ของคุณ แต่ควรสำรองไฟล์ไว้ก่อนใช้
- แจกฟรีตามสภาพ (MIT License) ไม่รับประกันผลลัพธ์ ค่าแพ็กเกจและเครดิตของ Claude, Kling และ Google เป็นของบัญชีผู้ใช้เอง
- nuea.ai ไม่ได้เป็นพันธมิตรหรือได้รับการรับรองจาก Anthropic, Google, ผู้ให้บริการ Kling หรือ Blender Foundation · Claude,
  Claude Code, Google Flow, Nano Banana, Veo, Kling, Blender และชื่ออื่นในหน้านี้เป็นเครื่องหมายการค้าของเจ้าของแต่ละราย
  ใช้เพียงเพื่อบอกว่า Skill ทำงานร่วมกับอะไร

## English

A Claude Code skill that turns a furnished Blender house into photoreal stills, 5 s clips and a game-style map page
without the AI moving the walls: interior-photo camera rules, a normal/clay/Material ID map pass per camera (the ID map
tells the image model which surface is which material), stills through Kling's MCP (paid) or Google Flow (free daily
quota, by hand), a red edge-overlay check against the model, and a single-file walkthrough page. Install by sending
Claude Code the repository link; see [INSTALL.md](INSTALL.md). MIT licence.
Requires a paid Claude plan (Pro or above) or an API key. Kling costs credits; Google Flow has a free daily quota that
Google can change. Not affiliated with or endorsed by Anthropic, Google, Kling or the Blender Foundation; product names
are their owners' trademarks. Provided as is, without warranty.
