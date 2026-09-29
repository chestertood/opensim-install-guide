# OpenSim + AI: ทำนายแรงกระแทกที่ข้อต่อ

โปรเจกต์นี้ใช้ OpenSim จำลองการกระแทก แล้วนำผลที่ได้ไปสร้างโมเดล AI ทำนายแรงที่ข้อต่อ

## ขั้นที่ 1: ติดตั้ง OpenSim 4.6

ไฟล์ทั้งหมดดาวน์โหลดจาก repo ทางการ [opensim-org/opensim-gui](https://github.com/opensim-org/opensim-gui/releases/tag/4.6_beta)
ไม่ต้องสมัครบัญชี GitHub หรือ simtk.org

| ระบบ | กดโหลด | ขนาด |
|---|---|---|
| **Windows** | [OpenSim-4.6-2026-04-11-a0637fa-win64.exe](https://github.com/opensim-org/opensim-gui/releases/download/4.6_beta/OpenSim-4.6-2026-04-11-a0637fa-win64.exe) | 505 MB |
| **Mac** (Intel และ M1–M4) | [OpenSim-4.6-Signed-Notarized.pkg](https://github.com/opensim-org/opensim-gui/releases/download/4.6_beta/OpenSim-4.6-Signed-Notarized.pkg) | 466 MB |

> ⚠️ **Mac:** ต้องโหลดไฟล์ที่ชื่อมีคำว่า `Signed-Notarized` เท่านั้น
> อย่าโหลดไฟล์ `OpenSim-4.6-2026-04-11-a0637fa.pkg` เพราะตัวนั้นไม่ได้ sign และ macOS จะบล็อก

---

## Windows

1. กดลิงก์ `.exe` ในตารางด้านบน
2. ถ้า browser บล็อกไฟล์:
   - **Edge:** กด `...` แล้วเลือก **Keep** จากนั้นเลือก **Keep anyway**
   - **Chrome:** กด **Keep**
3. ดับเบิลคลิกไฟล์ ถ้าขึ้นหน้า **"Windows protected your PC"** ให้กด **More info** แล้วกด **Run anyway**
4. กด Next ไปจนจบ (ใช้ค่าเริ่มต้นทั้งหมด)
5. เปิดโปรแกรมจาก Start menu โดยเลือก **OpenSim 4.6**

> Windows จะเตือนเพราะไฟล์ติดตั้งไม่มี digital signature ไม่ได้แปลว่าไฟล์เป็นไวรัส
> ตรวจว่าเป็นไฟล์ของแท้ได้จากหัวข้อ [ตรวจไฟล์](#ตรวจไฟล์ไม่บังคับ) ด้านล่าง

## Mac

1. กดลิงก์ `.pkg` ในตารางด้านบน
2. ดับเบิลคลิกไฟล์ แล้วกด Continue ไปจนจบ (ระบบจะถามรหัสผ่านเครื่อง)
3. ถ้าขึ้นว่า "cannot be opened" ให้ไปที่ **System Settings > Privacy & Security** เลื่อนลงไป แล้วกด **Open Anyway**
4. เปิดโปรแกรมจาก Applications โดยเลือก **OpenSim 4.6**

## ทดลองเปิดโมเดล

ในโปรแกรม OpenSim ไปที่ **File > Open Model** แล้วเลือกไฟล์ในโฟลเดอร์ `Documents/OpenSim/4.6/Models`

---

## ถ้าโหลดไม่ได้

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| ไม่มีปุ่ม Keep หรือ Run anyway ให้กด | เครื่องของมหาวิทยาลัยหรือแล็บล็อกไว้ | ให้ IT ติดตั้งให้ |
| ไฟล์หายไปหลังโหลดเสร็จ | antivirus ลบไฟล์หรือกักไฟล์ไว้ | ไปที่ Windows Security > Protection history แล้วกด Restore |
| กดโหลดแล้วไม่ขึ้นอะไรเลย หรือค้างอยู่ | เครือข่ายของมหาวิทยาลัยบล็อก | ลองโหลดผ่าน hotspot มือถือ |
| ขึ้นว่าต้องใช้สิทธิ์ admin | ไม่มีสิทธิ์ติดตั้งโปรแกรมบนเครื่องนี้ | ให้ IT ติดตั้งให้ |

ถ้ายังแก้ไม่ได้ ให้ส่ง screenshot หน้าจอมาให้อาจารย์ดู

---

## ตรวจไฟล์ (ไม่บังคับ)

ใช้ตรวจว่าไฟล์ที่โหลดมาครบและเป็นไฟล์ของแท้ ค่าที่ได้ต้องตรงกับค่าด้านล่างทุกตัวอักษร

**Windows** (เปิด PowerShell):
```powershell
Get-FileHash "$HOME\Downloads\OpenSim-4.6-2026-04-11-a0637fa-win64.exe"
```
ค่าที่ต้องได้: `180E2A5CE4CB7449792D0EC6AAA1B9E93DA8C329A665F63606E2485C392524D9`

**Mac** (เปิด Terminal):
```bash
shasum -a 256 ~/Downloads/OpenSim-4.6-Signed-Notarized.pkg
```
ค่าที่ต้องได้: `8774bf486d1d16cf821bf405cccafdf86eec282d9906767c1a854ea93c3ccb98`

---

## Python API (เฉพาะคนที่ต้องเขียนโค้ด)

สิ่งที่ต้องมี:
- Python **3.11–3.13**
- ถ้าใช้ Mac ต้องเป็น **macOS 15 (Sequoia) ขึ้นไป**

> ⚠️ ต้องติดตั้งใน venv เสมอ ถ้าติดตั้งลง Python หลักของเครื่อง numpy จะถูกอัปเกรดเป็น 2.x และทำให้ library อื่นพัง

**Windows:**
```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install opensim
python -c "import opensim; print(opensim.GetVersion())"
```

**Mac:**
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install opensim
python -c "import opensim; print(opensim.GetVersion())"
```

ถ้าบรรทัดสุดท้ายแสดง `4.6` แปลว่าติดตั้งสำเร็จ

หมายเหตุ: ตัวที่ติดตั้งผ่าน pip ไม่มีไฟล์โมเดล (`.osim`) มาด้วย ต้องติดตั้งโปรแกรม OpenSim ข้างบนก่อนจึงจะมีไฟล์โมเดลให้ใช้

---

## ไฟล์โจทย์และตัวอย่าง

โฟลเดอร์ [`impact_biomechanics/`](impact_biomechanics/) มีไฟล์โมเดล, ไฟล์ setup และสคริปต์ Python ตัวอย่าง
โหลดทั้งหมด: กดปุ่ม **Code** สีเขียว > **Download ZIP** แล้วเปิดไฟล์ [`impact_biomechanics/README.md`](impact_biomechanics/README.md) ก่อน
