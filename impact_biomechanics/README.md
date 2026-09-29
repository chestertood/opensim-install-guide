# impact_biomechanics — เริ่มที่นี่

| โฟลเดอร์ / ไฟล์ | ใช้เมื่อไหร่ |
|---|---|
| `02_impact_biomechanics.md` | คู่มือหลักของนักศึกษาคนที่ 2 |
| `1_lesson_opensim_gui/` | **คาบวันอาทิตย์** — ส่งทั้งโฟลเดอร์ให้เด็กล่วงหน้า |
| `2_models_extra/` | โมเดลคนเพิ่มเติม (ไว้ใช้คาบถัดไป) |
| `3_python/` | สคริปต์ Python (คาบถัดไป) — รัน `check_env.py` ก่อน |

## แผนคาบวันอาทิตย์ (ออนไลน์ 1:1, 60 นาที, OpenSim GUI)

ก่อนคาบ: เด็กสมัคร simtk.org → ลง OpenSim → โหลดโฟลเดอร์ `1_lesson_opensim_gui/`

| นาที | ทำอะไร |
|---|---|
| 0–5 | ทดสอบเสียง/แชร์จอ, เปิด OpenSim |
| 5–15 | STEP 1: เปิด `ball.osim` → Navigator (body/joint/contact) → Properties → Coordinates ตั้งความสูง |
| 15–30 | STEP 2–3: Tools > Forward Dynamics (3 s) → Play → Tools > Plot ความสูง vs เวลา |
| 30–50 | STEP 4: ทดลองเปลี่ยน gravity (โลก/ดวงจันทร์), dissipation (เด้ง/แป้ก), ความสูง |
| 50–60 | สรุป + บอกคาบหน้า: กล้ามเนื้อ + โมเดลคน |

สำรอง: ถ้า Forward Dynamics ใน GUI รันไม่ได้ → File > Load Motion → `ball_states.sto`
สร้างไฟล์ลูกบาสใหม่: `cd 3_python && python ball_bounce.py`  (bounce pass 2 แกน: `python ball_bounce_2d.py`)

อัดคลิปไว้ให้เด็กย้อนดู
