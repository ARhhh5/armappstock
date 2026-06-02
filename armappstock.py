import streamlit as st
from google import genai
import os

# ==========================================
# 1. การตั้งค่าหน้าตาเว็บ (UI Setup)
# ==========================================
st.set_page_config(page_title="โอเลี้ยง - Lazy Investor", page_icon="🥤", layout="wide")

st.title("🥤 โอเลี้ยง — Lazy Long-term Holder Edition")
st.markdown("""
**นักวิเคราะห์หุ้นสไตล์ "สายขี้เกียจถือยาว"**
> *"อย่าเด็ดดอกไม้แล้วไปรดน้ำวัชพืช — ถือหุ้นดีต่อ ขายหุ้นแย่ออก แล้วทำอย่างอื่นต่อไป"*
""")
st.divider()

# ==========================================
# 2. ส่วนรับข้อมูลจากผู้ใช้งาน (User Input)
# ==========================================
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🔑 ตั้งค่าระบบ")
    api_key = st.text_input("ใส่ Gemini API Key ของคุณที่นี่", type="password", help="รับฟรีได้ที่ Google AI Studio")
    
with col2:
    st.subheader("🎯 หุ้นที่ต้องการวิเคราะห์")
    stock_name = st.text_input("ใส่ชื่อหุ้น (เช่น PTT, AAPL, NVDA, AOT)", placeholder="พิมพ์ชื่อหุ้นตรงนี้...")

# ==========================================
# 3. System Prompt (สมองกลของโอเลี้ยง)
# ==========================================
oliang_prompt = """
คุณคือ **โอเลี้ยง** — นักวิเคราะห์หุ้นสไตล์ **"สายขี้เกียจถือยาว" (Lazy Long-term Holder)**
ผสมผสานระหว่าง William O'Neil (CANSLIM), Peter Lynch (Buy what you know), และ Stan Weinstein (Stage Analysis)

วิเคราะห์ตามโครงสร้างนี้เท่านั้น:
### STEP 1 — CANSLIM Scan (Pass/Fail)
ถ้าไม่ผ่านบอกว่า "ไม่ผ่านกรอง" (ประเมิน C, A, N, S, L, I, M พร้อมให้คะแนน X/7)
### STEP 2 — Stage Analysis (Stan Weinstein)
วิเคราะห์ว่าอยู่ Stage 1 (สะสม), 2 (ขาขึ้น), 3 (แจกจ่าย), หรือ 4 (ขาลง) พร้อมบอก SMA 30/50 Weekly
### STEP 3 — New Story Check
หาเรื่องใหม่ที่ตลาดยัง Underprice
### STEP 4 — Lazy Fundamental Check
เช็ค Revenue Growth, Gross Margin, Cash Position, Debt Load, Insider Ownership
### STEP 5 — Valuation Reality Check
ราคาใน 52-Week Range, P/S เทียบ Peer
### STEP 6 — Entry Zone & Holding Strategy
จุดเข้าซื้อ และจุด Stop Loss (หลุด SMA 30 Weekly)
### STEP 7 — Risk Map
ความเสี่ยง Market, Story, Competition, Valuation 
### STEP 8 — 3 Scenarios
Bull, Base, Bear
### STEP 9 — Lazy Verdict
สรุปคำตัดสิน: 🟢 เข้าได้เลย, 🔵 รอ Pullback, 🟡 ถือต่อ, ⚠️ เริ่มระวัง, 🔴 ขายหนี
### STEP 10 — One-Page Summary
สรุปสั้นๆ 1 หน้าให้คนธรรมดาเข้าใจง่ายๆ

ข้อควรระวัง: ห้ามกุข้อมูล ต้องค้นหาความจริงผ่าน Google Search เสมอ และต้องบอก Stage ทุกครั้ง
"""

# ==========================================
# 4. ระบบประมวลผลและแสดงผล (Execution)
# ==========================================
if st.button("🔍 วิเคราะห์สไตล์โอเลี้ยง", use_container_width=True):
    if not api_key:
        st.error("🚨 กรุณาใส่ API Key ก่อนครับ!")
    elif not stock_name:
        st.warning("🚨 กรุณาใส่ชื่อหุ้นที่ต้องการวิเคราะห์ครับ!")
    else:
        try:
            with st.spinner(f"🥤 โอเลี้ยงกำลังชงข้อมูลหุ้น {stock_name} (ใช้เวลาหาข้อมูลสักครู่)..."):
                # ใช้ Library ใหม่ google-genai
                client = genai.Client(api_key=api_key)
                
                # เรียกใช้ Gemini 2.5 Flash พร้อมเปิดเครื่องมือ Google Search
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"{oliang_prompt}\n\nคำสั่งจากผู้ใช้: วิเคราะห์หุ้น {stock_name}",
                    config={"tools": [{"google_search": {}}]}
                )
                
                st.success("✅ วิเคราะห์เสร็จสิ้น!")
                
                # แสดงผลลัพธ์ในกรอบสวยงาม
                with st.container(border=True):
                    st.markdown(response.text)
                    
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
            st.info("คำแนะนำ: ตรวจสอบ API Key ว่าถูกต้องหรือไม่ หรือโมเดลอาจจะคิวเต็ม ให้ลองกดใหม่อีกครั้งครับ")