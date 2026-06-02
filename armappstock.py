import streamlit as st
from google import genai
import datetime

# ==========================================
# 1. การตั้งค่าหน้าตาเว็บ (UI Setup)
# ==========================================
st.set_page_config(page_title="โอเลี้ยง - Lazy Investor", page_icon="🥤", layout="wide")

# ระบบความจำ (Session State) สำหรับเก็บประวัติการค้นหา
if 'history' not in st.session_state:
    st.session_state.history = []

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
    st.subheader("🔑 1. ตั้งค่าระบบ")
    # ฝัง API Key ให้เป็นค่าเริ่มต้น (ไม่ต้องพิมพ์ใหม่ทุกครั้ง)
    api_key = st.text_input("Gemini API Key", type="password", value="AIzaSyDXhee0topZSgPv0U_S0UCFgTfPfnpnUvw")
    
with col2:
    st.subheader("💰 2. งบประมาณ (บังคับ)")
    budget = st.number_input("ใส่งบลงทุน (เช่น 5000)", min_value=1.0, value=5000.0, step=100.0)
    currency = st.selectbox("สกุลเงิน", ["USD", "THB"])

with col3:
    st.subheader("🎯 3. ชื่อหุ้น / ธีม (ตัวเลือก)")
    stock_name = st.text_input("ชื่อหุ้น (เช่น NVDA) หรือปล่อยว่าง", placeholder="ปล่อยว่างเพื่อให้ระบบหาให้...")

# ==========================================
# 3. System Prompt (สมองกลของโอเลี้ยง)
# ==========================================
oliang_prompt = """
คุณคือ **โอเลี้ยง** — นักวิเคราะห์หุ้นสไตล์ **"สายขี้เกียจถือยาว" (Lazy Long-term Holder)**
ผสมผสานระหว่าง William O'Neil (CANSLIM), Peter Lynch (Buy what you know), และ Stan Weinstein (Stage Analysis) 
วิเคราะห์โดยอ้างอิงข้อมูลจากไฟล์ CL.AI.docx อย่างเคร่งครัด 

ภารกิจ:
- ถ้าระบุชื่อหุ้น: ให้วิเคราะห์หุ้นตัวนั้นเทียบกับงบประมาณที่ให้มา
- ถ้าไม่ระบุชื่อหุ้น: ค้นหาหุ้น Growth 1 ตัว ที่ราคาต่อหน่วย "ต่ำกว่างบประมาณ" ที่ให้ไว้ และมีโอกาสผ่านเกณฑ์ CANSLIM

วิเคราะห์ตามโครงสร้าง 10 ขั้นตอนนี้อย่างเคร่งครัด:
### STEP 1 — CANSLIM Scan (Pass/Fail)
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
### STEP 10 — สรุปงบประมาณและจำนวนหุ้นที่ซื้อได้ (บังคับรูปแบบเป๊ะๆ)
คุณต้องค้นหาราคาหุ้นล่าสุดแบบ Real-time และคำนวณตามโครงสร้างด้านล่างนี้เป๊ะๆ (ห้ามมโนตัวเลข ต้องหารให้ถูกต้อง):

**สรุปงบประมาณและจำนวนหุ้นที่ซื้อได้:**
* งบประมาณที่ให้มา: [ใส่งบประมาณ] [สกุลเงิน]
* ราคาหุ้น [ชื่อหุ้นย่อ] ปัจจุบันอยู่ที่ประมาณ [ราคาล่าสุด] [สกุลเงิน] ต่อหุ้น

ด้วยงบประมาณ [ใส่งบประมาณ] [สกุลเงิน] คุณจะสามารถซื้อหุ้น [ชื่อหุ้นย่อ] ได้ประมาณ [ใส่จำนวนหุ้นเต็มที่ปัดเศษลง] หุ้นเต็ม ครับ ([ใส่งบประมาณ] / [ราคาล่าสุด] = [ผลหาร] หุ้น)

**กฎเหล็ก:** ห้ามกุข้อมูล ต้องค้นหาความจริงผ่านอินเทอร์เน็ตเสมอ, ต้องบอก Stage ทุกครั้ง, และคำนวณคณิตศาสตร์ใน STEP 10 ให้ถูกต้อง 100%
"""

# ==========================================
# 4. ระบบประมวลผล (Execution)
# ==========================================
if st.button("🔍 สั่งโอเลี้ยงวิเคราะห์", use_container_width=True):
    if not api_key:
        st.error("🚨 กรุณาใส่ API Key ก่อนครับ!")
    elif budget <= 0:
        st.warning("🚨 กรุณาใส่งบประมาณครับ!")
    else:
        if stock_name:
            user_instruction = f"วิเคราะห์หุ้น '{stock_name}' ภายใต้งบประมาณ {budget} {currency}"
            search_target = stock_name
        else:
            user_instruction = f"ช่วยหาหุ้น Growth 1 ตัวที่ราคาต่ำกว่า {budget} {currency} และทำการวิเคราะห์ตามระบบให้หน่อย"
            search_target = f"หาหุ้นงบต่ำกว่า {budget} {currency}"

        try:
            with st.spinner(f"🥤 โอเลี้ยงกำลังวิเคราะห์ข้อมูล (ใช้เวลาสักครู่)..."):
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"{oliang_prompt}\n\nคำสั่งจากผู้ใช้: {user_instruction}\n(ข้อมูลประกอบ: งบ={budget}, สกุลเงิน={currency})",
                    config={"tools": [{"google_search": {}}]}
                )
                
                # แสดงผลการวิเคราะห์
                st.success("✅ วิเคราะห์เสร็จสิ้น!")
                with st.container(border=True):
                    st.markdown(response.text)
                
                # เซฟข้อมูลลงประวัติ (History)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.history.insert(0, {
                    "time": timestamp,
                    "target": search_target,
                    "budget": f"{budget:,.2f} {currency}",
                    "result": response.text
                })
                    
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {e}")
            st.info("ตรวจสอบ API Key หรือรอสักครู่แล้วลองกดวิเคราะห์ใหม่อีกครั้งครับ")

# ==========================================
# 5. ระบบประวัติการค้นหา (Search History)
# ==========================================
if st.session_state.history:
    st.divider()
    st.subheader("📚 ประวัติการวิเคราะห์ของคุณ (Search History)")
    st.markdown("ประวัติจะถูกบันทึกไว้ตลอดการใช้งานในหน้านี้ (หากกดรีเฟรชเบราว์เซอร์ใหม่ประวัติจะหายไป)")
    
    for idx, item in enumerate(st.session_state.history):
        with st.expander(f"🕒 {item['time']} | หุ้น/เป้าหมาย: {item['target']} | งบ: {item['budget']}"):
            st.markdown(item['result'])
