# คาบที่ 1 — ใช้ OpenSim เบื้องต้น

## ก่อนเข้าคาบ
1. สมัครบัญชีที่ simtk.org
2. ดาวน์โหลดและลง OpenSim

## ไฟล์ในโฟลเดอร์นี้
| ไฟล์ | คืออะไร |
|---|---|
| `ball.osim` | **คาบนี้** — ลูกบาส 1 ลูก + พื้น (1 body, 1 joint, 1 contact) |
| `ball_states.sto` | ผลจำลองลูกบาสเด้ง 10 วินาที ไฟล์เดียวครบ: ball_height (m), ball_speed (m/s), ball_accel (m/s²), floor_force (N) — Tools > Plot หรือ File > Load Motion |
| `ball_2d.osim` | **ตัวอย่างเสริม: bounce pass** — ค่าตั้งต้นความเร็ว 0 ทุกแกน (ตกตรงเหมือน ball.osim) ใส่ default speed เช่น ball_x 4, ball_y −3 = bounce pass มีแรงเสียดทาน (μ 0.2/0.15) บอลไม่หมุน coordinates: ball_x, ball_y, ball_z → ปรับทิศโยน ±x ±z ได้ที่ Coordinates > default speed |
| `ball_2d_states.sto` | ผลจำลอง 5 วินาทีของค่าตั้งต้น (ตกตรง: force_x, force_z = 0) — ถ้าโยน (4, −3, 0) จะได้ force_y ≈ 1770 N, force_x ≈ −265 N, ความเร็วไปข้างหน้า 4.0 → 2.6 m/s — File > Load Motion หรือ Tools > Plot |
| `gait2392_simbody.osim` | โมเดลร่างกายคน — คาบหน้า |
| `ball_forward_setup.xml` | ตั้งค่า Forward Dynamics (3 s, Max step size 0.005) — Tools > Forward Dynamics > Load… > Run |
| `ball_id_setup.xml` | ตั้งค่า Inverse Dynamics — Tools > Inverse Dynamics > Load… เลือกไฟล์นี้ > Run ได้ `ball_inverse.sto` (แรงจากพื้น, peak ≈ 1410 N) |

> ถ้าเปิดแล้วมีข้อความว่าหาไฟล์ `.vtp` ไม่เจอ ไม่เป็นไร — แค่ภาพกระดูกไม่แสดง การคำนวณยังถูกต้อง

## Forward Dynamics ใน GUI — ลูกตกกระตุก?
ไม่ใช่บั๊ก: integrator ปรับ step เอง ตอนลอยในอากาศการเคลื่อนที่ง่าย มันเลยก้าวทีละ ~0.3 s → ไฟล์ผลมีแค่ ~5 เฟรมตอนตก ภาพเลยกระตุก (ตัวเลขยังถูก)
แก้: ในหน้าต่าง Forward Dynamics ตั้ง **Maximum step size = 0.005** (หรือ Load… `ball_forward_setup.xml`) → ได้ ~90 เฟรมตอนตก

## Inverse Dynamics ใน GUI
GUI **ไม่อ่าน** `forces_to_exclude` จากไฟล์ setup (ทดสอบแล้ว: ได้ peak แค่ ~7 N) → ต้องปิดแรงพื้นในโมเดลเอง:
1. Navigator > bouncing_ball > Forces > `contact` → Properties: **appliesForce = false**
2. Tools > Inverse Dynamics > **Load…** (ปุ่มล่าง ไม่ใช่ช่อง Motion) > `ball_id_setup.xml` > Run  (~0.2 s)
3. Tools > Plot > `ball_inverse.sto` > `ball_height_force` → peak ≈ 1410 N
4. **เปิด appliesForce = true กลับ** ก่อนรัน Forward Dynamics ไม่งั้นลูกทะลุพื้น

ทำไม: ID ต้อง "หา" แรงจากพื้นเอง ถ้าโมเดลยังมีแรงพื้นอยู่ มันอธิบายการเคลื่อนที่ได้หมดแล้ว → เหลือ ≈ 0
ถ้าตั้งเองในหน้าต่าง: **ติ๊กออก Filter coordinates** (เปิดไว้ แรงกระแทกโดนกรองหาย)
