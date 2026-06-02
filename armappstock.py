import streamlit as st
from google import genai

# ==========================================
# 1. การตั้งค่าหน้าตาเว็บ (UI Setup)
# ==========================================
st.set_page_config(page_title="โอเลี้ยง - Lazy Investor", page_icon="🥤", layout="wide")

st.title("🥤 โอเลี้ยง — Lazy Long-term Holder Edition")
st.markdown("""
**นักวิเคราะห์หุ้นสไตล์ "สายขี้เกียจถือยาว" (Lazy Long-term Holder)**
> *"อย่าเด็ดดอกไม้แล้วไปรดน้ำวัชพืช — ถือหุ้นดีต่อ ขายหุ้นแย่ออก แล้วทำอย่างอื่นต่อไป"*
""")
st.divider()

# ==========================================
# 2. ส่วนรับข้อมูลจากผู้ใช้งาน (User Input)
# ==========================================
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.subheader("🔑 1. ระบบสมองกล")
    api_key = st.text_input("ใส่ Gemini API Key", type="password", help="เอา API Key จาก Google AI Studio มาใส่")
    
with col2:
    st.subheader("💰 2. งบประมาณ (บังคับ)")
    budget = st.number_input("ใส่งบลงทุน (เช่น 500 หรือ 10000)", min_value=1)
    currency = st.selectbox("สกุลเงิน", ["USD", "THB"])

with col3:
    st.subheader("🎯 3. ชื่อหุ้น / ธีม (ตัวเลือก)")
    stock_name = st.text_input("ชื่อหุ้น (เช่น AAPL) หรือ ธีม (เช่น AI)", placeholder="ปล่อยว่างเพื่อให้ระบบหาให้...")

# ==========================================
# 3. System Prompt (สมองกลของโอเลี้ยง)
# ==========================================
oliang_prompt = """
คุณคือ **โอเลี้ยง** — นักวิเคราะห์หุ้นสไตล์ **"สายขี้เกียจถือยาว" (Lazy Long-term Holder)**
ผสมผสานระหว่าง William O'Neil (CANSLIM), Peter Lynch (Buy what you know), และ Stan Weinstein (Stage Analysis) 
วิเคราะห์โดยอ้างอิงหลักการจากไฟล์ CL.AI.docx อย่างเคร่งครัด

ภารกิจพิเศษ:
- ถ้าระบุชื่อหุ้นมา: ให้วิเคราะห์หุ้นตัวนั้นเทียบกับงบประมาณว่าซื้อได้กี่หุ้น
- ถ้าไม่ได้ระบุชื่อหุ้นมา (หรือระบุแค่ธีม): ให้คุณทำหน้าที่ค้นหาและคัดเลือกหุ้นมา 1 ตัว ที่มีราคาต่อหน่วย "ต่ำกว่างบประมาณ" ที่ให้ไว้ (เพื่อให้ซื้อได้อย่างน้อย 1 หุ้นเต็ม) และต้องเป็นหุ้นที่มีโอกาสผ่านเกณฑ์ CANSLIM และอยู่ Stage 2

วิเคราะห์ตามโครงสร้าง 10 ขั้นตอนนี้อย่างเคร่งครัด:
### STEP 1 — CANSLIM Scan (Pass/Fail ก่อนเลย)
ประเมิน C, A, N, S, L, I, M ตามเกณฑ์ หากไม่ผ่าน ≥5/7 ให้บอกตรงๆ ว่าไม่น่าสนใจ
### STEP 2 — Stage Analysis (Stan Weinstein)
วิเคราะห์ว่าหุ้นอยู่ใน Stage 1 (สะสม), 2 (ขาขึ้น), 3 (แจกจ่าย), หรือ 4 (ขาลง)
### STEP 3 — New Story Check (N ใน CANSLIM)
หาเรื่องใหม่ที่ตลาดยัง Underprice ใน 2-3 ประโยค
### STEP 4 — Lazy Fundamental Check (20% ของการตัดสินใจ)
เช็ค Revenue Growth, Gross Margin, Cash Position, Debt Load, Insider Ownership
### STEP 5 — Valuation Reality Check (แพงเกินไปไหม?)
เช็คราคาใน 52-Week Range, P/S เทียบ Peer, และ Reverse DCF สั้นๆ
### STEP 6 — Entry Zone & Holding Strategy (สำหรับสายขี้เกียจ)
บอกจุดเข้าที่ชัดเจน และจุด Stop Loss (เช่น ใต้ SMA 30 Weekly)
### STEP 7 — Risk Map (สั้น ๆ แต่ครบ)
ประเมินความเสี่ยง Market, Story, Competition, Valuation, Execution, Liquidity
### STEP 8 — 3 Scenarios (แบบสายขี้เกียจ)
Bull (+100% to +300%), Base (+30% to +80%), Bear (-30% to -60%)
### STEP 9 — Lazy Verdict (คำตัดสินชัดเจน)
สรุปคำตัดสิน: 🟢 เข้าได้เลย, 🔵 รอ Pullback, 🟡 ถือต่อ, ⚠️ เริ่มระวัง, 🔴 ขายหนี
### STEP 10 — One-Page Summary (ภาษาคนธรรมดา)
สรุปสั้นๆ เข้าใจง่าย 1 หน้าจบ พร้อมสรุปว่า งบประมาณที่ให้มา ซื้อหุ้นตัวนี้ได้ประมาณกี่หุ้น

**กฎเหล็ก:** ห้ามกุข้อมูล ค้นหาข้อมูลจริงเสมอ, ต้องบอก Stage ทุกครั้ง, และถ้า CANSLIM ไม่ผ่านให้หยุดวิเคราะห์ลึก
"""

# ==========================================
# 4. ระบบประมวลผลและแสดงผล (Execution)
# ==========================================
if st.button("🔍 สั่งโอเลี้ยงเสาะหาและวิเคราะห์หุ้น", use_container_width=True):
    if not api_key:
        st.error("🚨 กรุณาใส่ API Key ก่อนครับ!")
    elif budget <= 0:
        st.warning("🚨 กรุณาใส่งบประมาณก่อนครับ ระบบจะได้หาหุ้นที่ราคาเหมาะสมให้!")
    else:
        # กำหนดคำสั่งตามเงื่อนไขที่ผู้ใช้กรอก
        if stock_name:
            user_instruction = f"วิเคราะห์หุ้น/ธีม '{stock_name}' โดยมีงบประมาณ {budget} {currency}"
        else:
            user_instruction = f"ฉันไม่รู้จะซื้อหุ้นอะไรดี ช่วยหาหุ้นพื้นฐานดี 1 ตัวที่ราคาต่อหุ้นต่ำกว่างบประมาณ {budget} {currency} และทำการวิเคราะห์ให้หน่อย"

        try:
            with st.spinner("🥤 โอเลี้ยงกำลังค้นหาข้อมูลและชงรายงาน (ใช้เวลาสักครู่)..."):
                client = genai.Client(api_key=api_key)
                
                # เปิดใช้ Google Search เป็นเครื่องมือหาข้อมูลจริง
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"{oliang_prompt}\n\nคำสั่งจากผู้ใช้: {user_instruction}",
                    config={"tools": [{"google_search": {}}]}
                )
                
                st.success("✅ วิเคราะห์เสร็จสิ้น!")
                
                with st.container(border=True):
                    st.markdown(response.text)
                    
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {e}")
            st.info("คำแนะนำ: ตรวจสอบ API Key ว่าถูกต้องหรือไม่ หรือลองกดปุ่มวิเคราะห์ใหม่อีกครั้งครับ")
