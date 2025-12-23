import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="المحاكي الذكي للأعطال", layout="wide", page_icon="🎛️")

# --- 2. القيم الافتراضية (تم تحديث مسميات التيوب) ---
default_values = {
    "الرنين المغناطيسي (MRI)": {
        "helium": 85.0, "chiller_temp": 10.0, "room_temp": 22.0, "humidity": 45.0,
        "cont_hours": 4.0, "total_usage": 20000.0, "total_cases": 15
    },
    "الأشعة المقطعية (CT Scan)": {
        "gantry_temp": 35.0, "voltage": 220.0, "current": 10.0, "room_temp": 22.0,
        "cont_hours": 4.0, "humidity": 40.0, "tube_age": 50000.0 # Scan Seconds
    },
    "الفلورسكوبي (Fluoro)": {
        "voltage": 220.0, "humidity": 45.0, "tube_temp": 30.0,
        "cont_hours": 2.0, "tube_age": 10000.0 # Hours
    },
    "الأشعة السينية (X-Ray)": {
        "tube_temp": 35.0, "voltage": 70.0, "cont_hours": 6.0,
        "tube_age": 15000.0 # Exposures/Hours
    }
}

# --- 3. إدارة الحالة (Session State) ---
if 'device_type' not in st.session_state:
    st.session_state['device_type'] = "الرنين المغناطيسي (MRI)"

def update_state(device):
    defaults = default_values[device]
    for key, val in defaults.items():
        st.session_state[key] = val

def on_device_change():
    update_state(st.session_state.device_selector)

# --- 4. CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;800&display=swap');
* { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
.control-panel { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; }
.group-header { color: #0b3b52; font-weight: 700; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; }
.result-container { padding: 20px; border-radius: 12px; height: 100%; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
.safe-box { background-color: #f0fdf4; border-top: 5px solid #22c55e; }
.warn-box { background-color: #fffbeb; border-top: 5px solid #f59e0b; }
.crit-box { background-color: #fef2f2; border-top: 5px solid #ef4444; }
</style>
""", unsafe_allow_html=True)

# --- 5. الهيدر ---
col_header, col_select, col_reset = st.columns([2, 1, 0.5])
with col_header:
    st.title("🎛️ نظام محاكاة الأعطال")
    st.caption("تم إضافة تحليل: (عمر التيوب + ساعات التشغيل = الإجهاد الحراري)")

with col_select:
    device_type = st.selectbox("🔻 نوع الجهاز:", list(default_values.keys()), key="device_selector", on_change=on_device_change)

with col_reset:
    st.write(""); st.write("")
    if st.button("🔄 استعادة"):
        update_state(device_type)
        st.rerun()

if "helium" not in st.session_state and device_type == "الرنين المغناطيسي (MRI)": update_state(device_type)

# --- 6. لوحة المدخلات ---
inputs = {}
with st.container():
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    st.markdown('<div class="group-header">1️⃣ القراءات الحيوية والبيئية</div>', unsafe_allow_html=True)
    
    if device_type == "الرنين المغناطيسي (MRI)":
        c1, c2, c3, c4 = st.columns(4)
        inputs['helium'] = c1.number_input("🎈 هيليوم (%)", 0.0, 100.0, key="helium", step=0.5)
        inputs['chiller_temp'] = c2.number_input("❄️ حرارة الشيلر (°C)", 0.0, 50.0, key="chiller_temp", step=0.5)
        inputs['room_temp'] = c3.number_input("🌡️ حرارة الغرفة (°C)", 10.0, 45.0, key="room_temp", step=0.5)
        inputs['humidity'] = c4.number_input("💧 الرطوبة (%)", 0.0, 100.0, key="humidity", step=1.0)
        
        st.markdown('<br><div class="group-header">2️⃣ بيانات التشغيل</div>', unsafe_allow_html=True)
        c5, c6, c7 = st.columns(3)
        inputs['cont_hours'] = c5.number_input("⏱️ تشغيل متواصل (ساعة)", 0.0, 24.0, key="cont_hours", step=0.5)
        inputs['total_usage'] = c6.number_input("⏳ عمر الجهاز (ساعة)", 0.0, 200000.0, key="total_usage", step=1000.0)
        inputs['total_cases'] = c7.number_input("busts الحالات", 0, 100, key="total_cases")

    elif device_type == "الأشعة المقطعية (CT Scan)":
        c1, c2, c3, c4 = st.columns(4)
        inputs['gantry_temp'] = c1.number_input("☢️ حرارة الجانتري", 10.0, 120.0, key="gantry_temp", step=0.5)
        inputs['voltage'] = c2.number_input("⚡ جهد (V)", 0.0, 300.0, key="voltage", step=1.0)
        inputs['current'] = c3.number_input("تيار (mA)", 0.0, 50.0, key="current", step=0.5)
        inputs['room_temp'] = c4.number_input("🌡️ حرارة الغرفة", 10.0, 45.0, key="room_temp", step=0.5)

        st.markdown('<br><div class="group-header">2️⃣ بيانات التشغيل والتيوب</div>', unsafe_allow_html=True)
        c5, c6, c7 = st.columns(3)
        inputs['cont_hours'] = c5.number_input("⏱️ تشغيل متواصل (ساعة)", 0.0, 24.0, key="cont_hours", step=0.5)
        # هنا التعديل: عمر التيوب
        inputs['tube_age'] = c6.number_input("⏳ عمر التيوب (Scan Seconds)", 0.0, 500000.0, key="tube_age", step=1000.0)
        inputs['humidity'] = c7.number_input("💧 الرطوبة (%)", 0.0, 100.0, key="humidity", step=1.0)

    elif device_type == "الفلورسكوبي (Fluoro)":
        c1, c2, c3 = st.columns(3)
        inputs['voltage'] = c1.number_input("⚡ جهد (V)", 0.0, 300.0, key="voltage", step=1.0)
        inputs['humidity'] = c2.number_input("💧 الرطوبة (%)", 0.0, 100.0, key="humidity", step=1.0)
        inputs['tube_temp'] = c3.number_input("🔥 حرارة الأنبوب", 10.0, 100.0, key="tube_temp", step=0.5)
        
        st.markdown('<br><div class="group-header">2️⃣ بيانات التشغيل والتيوب</div>', unsafe_allow_html=True)
        c4, c5 = st.columns(2)
        inputs['cont_hours'] = c4.number_input("⏱️ تشغيل متواصل (ساعة)", 0.0, 12.0, key="cont_hours", step=0.5)
        # هنا التعديل
        inputs['tube_age'] = c5.number_input("⏳ عمر التيوب (ساعة)", 0.0, 100000.0, key="tube_age", step=500.0)

    elif device_type == "الأشعة السينية (X-Ray)":
        c1, c2, c3 = st.columns(3)
        inputs['tube_temp'] = c1.number_input("🔥 حرارة الأنبوب", 10.0, 120.0, key="tube_temp", step=0.5)
        inputs['voltage'] = c2.number_input("⚡ جهد عالي (kV)", 0.0, 200.0, key="voltage", step=1.0)
        inputs['cont_hours'] = c3.number_input("⏱️ ساعات العمل", 0.0, 24.0, key="cont_hours", step=0.5)
        
        st.markdown('<br><div class="group-header">2️⃣ بيانات التشغيل والتيوب</div>', unsafe_allow_html=True)
        c4 = st.columns(1)[0]
        # هنا التعديل
        inputs['tube_age'] = c4.number_input("⏳ عمر التيوب (Exposure/Hr)", 0.0, 100000.0, key="tube_age", step=500.0)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. المحرك التحليلي (Physics Engine) ---
def analyze_simulation(dev, data):
    risk_score = 0
    factors = {}
    reasons = []
    actions = []

    # === معادلة "الشيخوخة الحرارية" (Thermal Aging Logic) ===
    # الفكرة: تيوب قديم + شغل كتير = خطر مضاعف
    
    aging_risk = 0
    if dev != "الرنين المغناطيسي (MRI)":
        tube_val = data.get('tube_age', 0)
        work_val = data.get('cont_hours', 0)
        
        # حدود العمر لكل جهاز
        limit = 200000 if dev == "الأشعة المقطعية (CT Scan)" else 20000
        
        # 1. خطر العمر المباشر
        if tube_val > limit:
            aging_risk += 15
            reasons.append("التيوب تجاوز العمر الافتراضي")
            factors['Tube Age'] = 15
            
        # 2. خطر "الإجهاد المركب" (الربط بين العمر والتشغيل)
        # إذا التيوب قديم (أكثر من 70% من عمره) وشغال أكثر من 4 ساعات
        if (tube_val > limit * 0.7) and (work_val > 4):
            extra_stress = 20
            aging_risk += extra_stress
            reasons.append("إجهاد عالٍ: تشغيل طويل لتيوب قديم")
            actions.append("تقليل مدة الجلسات / تبريد إجباري")
            factors['Thermal Stress'] = extra_stress

    risk_score += aging_risk

    # === باقي العوامل ===
    # 1. الرنين (نفس السابق)
    if dev == "الرنين المغناطيسي (MRI)":
        if data['helium'] < 40: risk_score+=50; reasons.append("خطر Quench"); actions.append("تعبئة طارئة"); factors['Helium']=50
        elif data['helium'] < 60: risk_score+=20; reasons.append("انخفاض هيليوم"); factors['Helium']=20
        if data['chiller_temp'] > 20: risk_score+=30; reasons.append("فشل شيلر"); factors['Cooling']=30
        if (data['room_temp']*0.5 + data['cont_hours']*1.5) > 25: risk_score+=15; reasons.append("إجهاد حراري"); factors['Stress']=15

    # 2. المقطعية (CT)
    elif dev == "الأشعة المقطعية (CT Scan)":
        if data['gantry_temp'] > 85: risk_score+=50; reasons.append("حرارة جانتري خطرة"); actions.append("إيقاف فوري"); factors['Temperature']=50
        elif data['gantry_temp'] > 60: risk_score+=25; reasons.append("ارتفاع حرارة"); factors['Temperature']=25
        if abs(data['voltage']-220) > 20: risk_score+=30; reasons.append("تذبذب كهرباء"); factors['Electrical']=30

    # 3. الفلورو (Fluoro)
    elif dev == "الفلورسكوبي (Fluoro)":
        if data.get('humidity',0) > 70: risk_score+=40; reasons.append("رطوبة عالية"); actions.append("مزيلات رطوبة"); factors['Humidity']=40
        if data['voltage'] < 190: risk_score+=30; reasons.append("انخفاض جهد"); factors['Electrical']=30
        if data['tube_temp'] > 70: risk_score+=20; reasons.append("حرارة أنبوب"); factors['Temp']=20

    # 4. الإكس راي (X-Ray)
    elif dev == "الأشعة السينية (X-Ray)":
        if data['tube_temp'] > 60: risk_score+=45; reasons.append("حرارة أنبوب"); actions.append("تبريد زيت"); factors['Tube Heat']=45
        if abs(data['voltage']-70) > 15: risk_score+=20; reasons.append("تذبذب kV"); factors['Electrical']=20

    # النتيجة
    risk_score = min(risk_score, 100)
    if risk_score >= 50: status="خطر مرتفع 🔴"; css="crit-box"; clr="#ef4444"
    elif risk_score >= 20: status="تحذير 🟡"; css="warn-box"; clr="#f59e0b"
    else: status="آمن 🟢"; css="safe-box"; clr="#22c55e"; reasons.append("الأداء طبيعي"); actions.append("مراقبة دورية")
    
    return risk_score, status, css, reasons, actions, factors, clr

# تشغيل التحليل
score, status, css, reasons, actions, factors, clr = analyze_simulation(device_type, inputs)

# --- 8. العرض ---
st.markdown("### 3️⃣ نتائج التشخيص")
col_gauge, col_diag = st.columns([1, 2])

with col_gauge:
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        title = {'text': "مؤشر الخطر", 'font': {'size': 18}},
        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': clr},
                 'steps': [{'range': [0, 20], 'color': '#dcfce7'}, {'range': [20, 50], 'color': '#fef3c7'}, {'range': [50, 100], 'color': '#fee2e2'}]}))
    fig_gauge.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_diag:
    st.markdown(f"""
    <div class="result-container {css}">
        <h2 style="margin-top:0; color:{clr}">{status}</h2>
        <hr style="border-color:rgba(0,0,0,0.1)">
        <div style="display:flex; gap: 20px;">
            <div style="flex:1;">
                <h4 style="margin-bottom:10px;">🧐 تحليل الأسباب:</h4>
                <ul style="font-size:1.1em;">{''.join([f'<li>{r}</li>' for r in reasons])}</ul>
            </div>
            <div style="flex:1; border-right:1px solid rgba(0,0,0,0.1); padding-right:20px;">
                <h4 style="margin-bottom:10px;">🛠️ التوصيات:</h4>
                <ul style="font-size:1.1em;">{''.join([f'<li>{a}</li>' for a in actions])}</ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
if sum(factors.values()) > 0:
    st.markdown("---")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("📊 ما هو العامل الأكبر تأثيراً؟")
        fig_pie = px.pie(names=list(factors.keys()), values=list(factors.values()), hole=0.5)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_c2:
        st.subheader("⚠️ تحليل الإجهاد (التيوب vs التشغيل)")
        # رسم علاقة بسيط
        if device_type != "الرنين المغناطيسي (MRI)":
            fig_scat = px.scatter(x=[inputs.get('tube_age',0)], y=[inputs.get('cont_hours',0)], 
                                  size=[20], color=[score], color_continuous_scale='RdYlGn_r',
                                  labels={'x':'عمر التيوب', 'y':'ساعات التشغيل المتواصل'},
                                  title="موقعك الحالي في منحنى الإجهاد")
            # إضافة مناطق الخطر
            fig_scat.add_shape(type="rect", x0=100000, y0=4, x1=500000, y1=24, fillcolor="red", opacity=0.2)
            st.plotly_chart(fig_scat, use_container_width=True)
