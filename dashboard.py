import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="المحاكي الذكي للأعطال (Advanced)", layout="wide", page_icon="🧠")

# --- القيم الافتراضية المحدثة ---
default_values = {
    "الرنين المغناطيسي (MRI)": {
        "helium": 85.0, "chiller_temp": 10.0, "room_temp": 22.0, "humidity": 45.0,
        "cont_hours": 4.0, "comp_pressure": 20.0, "coil_snr": 95.0 # ضغط الكمبروسر + جودة الصورة
    },
    "الأشعة المقطعية (CT Scan)": {
        "gantry_temp": 35.0, "voltage": 220.0, "tube_arcing": 0, # عدد الشرارات
        "cont_hours": 4.0, "humidity": 40.0, "tube_age": 50000.0, "fan_rpm": 2500 # سرعة المراوح
    },
    "الفلورسكوبي (Fluoro)": {
        "voltage": 220.0, "humidity": 45.0, "tube_temp": 30.0,
        "cont_hours": 2.0, "tube_age": 10000.0, "error_logs": 0 # سجل الأخطاء
    },
    "الأشعة السينية (X-Ray)": {
        "tube_temp": 35.0, "voltage": 70.0, "cont_hours": 6.0,
        "tube_age": 15000.0, "exposure_errors": 0 # أخطاء التصوير
    }
}

# --- إدارة الحالة ---
if 'device_type' not in st.session_state: st.session_state['device_type'] = "الرنين المغناطيسي (MRI)"
def update_state(device):
    for key, val in default_values[device].items(): st.session_state[key] = val
def on_device_change(): update_state(st.session_state.device_selector)

# --- CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;800&display=swap');
* { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
.control-panel { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; }
.group-header { color: #1e293b; font-weight: 700; margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; font-size: 1.1em; }
.result-container { padding: 20px; border-radius: 12px; height: 100%; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
.safe-box { background-color: #f0fdf4; border-top: 5px solid #22c55e; }
.warn-box { background-color: #fffbeb; border-top: 5px solid #f59e0b; }
.crit-box { background-color: #fef2f2; border-top: 5px solid #ef4444; }
</style>
""", unsafe_allow_html=True)

# --- الهيدر ---
col_h, col_s, col_r = st.columns([2, 1, 0.5])
with col_h: st.title("🧠 المحاكي الذكي (Advanced)"); st.caption("تمت إضافة: Arcing, Pressure, Fans, Error Logs")
with col_s: device_type = st.selectbox("🔻 الجهاز:", list(default_values.keys()), key="device_selector", on_change=on_device_change)
with col_r: 
    st.write(""); st.write("")
    if st.button("🔄 ريسيت"): update_state(device_type); st.rerun()

if "helium" not in st.session_state and device_type == "الرنين المغناطيسي (MRI)": update_state(device_type)

# --- المدخلات ---
inputs = {}
with st.container():
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    
    # 1. MRI Inputs
    if device_type == "الرنين المغناطيسي (MRI)":
        st.markdown('<div class="group-header">1️⃣ التبريد والمغناطيس</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        inputs['helium'] = c1.number_input("🎈 هيليوم (%)", 0.0, 100.0, key="helium", step=0.5)
        # المعطى الجديد: ضغط الكمبروسر
        inputs['comp_pressure'] = c2.number_input("⚙️ ضغط الكمبروسر (PSI)", 0.0, 30.0, key="comp_pressure", step=0.5, help="المثالي بين 18-22 PSI")
        inputs['chiller_temp'] = c3.number_input("❄️ حرارة الشيلر", 0.0, 50.0, key="chiller_temp", step=0.5)
        inputs['room_temp'] = c4.number_input("🌡️ حرارة الغرفة", 10.0, 45.0, key="room_temp", step=0.5)
        
        st.markdown('<br><div class="group-header">2️⃣ التشغيل وجودة الصورة</div>', unsafe_allow_html=True)
        c5, c6, c7 = st.columns(3)
        inputs['cont_hours'] = c5.number_input("⏱️ تشغيل متواصل", 0.0, 24.0, key="cont_hours")
        # المعطى الجديد: SNR
        inputs['coil_snr'] = c6.number_input("📡 جودة الإشارة (SNR %)", 0.0, 100.0, key="coil_snr", step=1.0, help="أقل من 80% يعني صور مشوشة")
        inputs['humidity'] = c7.number_input("💧 الرطوبة", 0.0, 100.0, key="humidity")

    # 2. CT Inputs
    elif device_type == "الأشعة المقطعية (CT Scan)":
        st.markdown('<div class="group-header">1️⃣ صحة الأنبوب والكهرباء</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        inputs['gantry_temp'] = c1.number_input("☢️ حرارة الجانتري", 10.0, 120.0, key="gantry_temp")
        inputs['voltage'] = c2.number_input("⚡ جهد (V)", 0.0, 300.0, key="voltage")
        # المعطى الجديد: Arcing
        inputs['tube_arcing'] = c3.number_input("💥 عدد الشرارات (Arcing/Day)", 0, 50, key="tube_arcing", help="أي رقم فوق الصفر مقلق")
        inputs['tube_age'] = c4.number_input("⏳ عمر التيوب (Scan Sec)", 0.0, 500000.0, key="tube_age", step=1000.0)

        st.markdown('<br><div class="group-header">2️⃣ البيئة والمكونات</div>', unsafe_allow_html=True)
        c5, c6, c7 = st.columns(3)
        inputs['cont_hours'] = c5.number_input("⏱️ تشغيل متواصل", 0.0, 24.0, key="cont_hours")
        # المعطى الجديد: RPM
        inputs['fan_rpm'] = c6.number_input("🌀 سرعة المراوح (RPM)", 0, 5000, key="fan_rpm", help="أقل من 2000 خطر")
        inputs['humidity'] = c7.number_input("💧 الرطوبة", 0.0, 100.0, key="humidity")

    # 3. Fluoro Inputs
    elif device_type == "الفلورسكوبي (Fluoro)":
        c1, c2, c3 = st.columns(3)
        inputs['voltage'] = c1.number_input("⚡ جهد (V)", 0.0, 300.0, key="voltage")
        inputs['tube_temp'] = c2.number_input("🔥 حرارة التيوب", 10.0, 100.0, key="tube_temp")
        # المعطى الجديد: Logs
        inputs['error_logs'] = c3.number_input("⚠️ سجل الأخطاء (Log/hr)", 0, 50, key="error_logs")
        
        c4, c5, c6 = st.columns(3)
        inputs['cont_hours'] = c4.number_input("⏱️ تشغيل متواصل", 0.0, 12.0, key="cont_hours")
        inputs['tube_age'] = c5.number_input("⏳ عمر التيوب", 0.0, 100000.0, key="tube_age")
        inputs['humidity'] = c6.number_input("💧 الرطوبة", 0.0, 100.0, key="humidity")

    # 4. X-Ray Inputs
    elif device_type == "الأشعة السينية (X-Ray)":
        c1, c2, c3 = st.columns(3)
        inputs['tube_temp'] = c1.number_input("🔥 حرارة التيوب", 10.0, 120.0, key="tube_temp")
        inputs['voltage'] = c2.number_input("⚡ جهد (kV)", 0.0, 200.0, key="voltage")
        # المعطى الجديد: Exposure Errors
        inputs['exposure_errors'] = c3.number_input("🚫 فشل التصوير (Errors)", 0, 20, key="exposure_errors")
        
        c4, c5 = st.columns(2)
        inputs['cont_hours'] = c4.number_input("⏱️ تشغيل", 0.0, 24.0, key="cont_hours")
        inputs['tube_age'] = c5.number_input("⏳ عمر التيوب", 0.0, 100000.0, key="tube_age")

    st.markdown('</div>', unsafe_allow_html=True)

# --- المحرك التحليلي المتقدم ---
def analyze_simulation(dev, data):
    risk_score = 0
    factors = {}
    reasons = []
    actions = []

    # 1. تحليل الرنين (MRI)
    if dev == "الرنين المغناطيسي (MRI)":
        # ضغط الكمبروسر (الجديد)
        pres = data.get('comp_pressure', 20)
        if pres < 15 or pres > 25:
            risk_score += 40
            reasons.append(f"ضغط كمبروسر غير مستقر ({pres} PSI)")
            actions.append("فحص الـ Cold Head والوصلات")
            factors['Compressor'] = 40
        
        # جودة الصورة (الجديد)
        if data.get('coil_snr', 100) < 80:
            risk_score += 25
            reasons.append("تشويش في الصورة (Low SNR)")
            actions.append("فحص الـ RF Coils")
            factors['Image Quality'] = 25

        if data['helium'] < 40: risk_score+=50; reasons.append("خطر Quench"); factors['Helium']=50
        elif data['helium'] < 60: risk_score+=20; reasons.append("نقص هيليوم"); factors['Helium']=20
        if data['chiller_temp'] > 20: risk_score+=30; reasons.append("فشل شيلر"); factors['Cooling']=30

    # 2. تحليل المقطعية (CT)
    elif dev == "الأشعة المقطعية (CT Scan)":
        # Arcing (الجديد والأخطر)
        arcs = data.get('tube_arcing', 0)
        if arcs > 2:
            risk_score += 60 # وزن عالي جداً
            reasons.append(f"شرارة داخلية متكررة ({arcs}/day)")
            actions.append("استبدال التيوب فوراً (Spitting)")
            factors['Tube Arcing'] = 60
        elif arcs > 0:
            risk_score += 30
            reasons.append("بداية شرارة (Arcing)")
            actions.append("عمل Tube Conditioning")
            factors['Tube Arcing'] = 30
            
        # المراوح (الجديد)
        if data.get('fan_rpm', 3000) < 2000:
            risk_score += 20
            reasons.append("ضعف تبريد اللوحات (Low RPM)")
            factors['Fans'] = 20

        if data['gantry_temp'] > 85: risk_score+=50; reasons.append("حرارة عالية"); factors['Temp']=50
        if abs(data['voltage']-220)>20: risk_score+=30; reasons.append("تذبذب كهرباء"); factors['Elec']=30
        
        # معادلة التيوب والتشغيل
        if data['tube_age'] > 200000 and data['cont_hours'] > 4:
            risk_score += 20; reasons.append("إجهاد تيوب قديم"); factors['Stress']=20

    # 3. تحليل الفلورو (Fluoro)
    elif dev == "الفلورسكوبي (Fluoro)":
        # سجل الأخطاء (الجديد)
        logs = data.get('error_logs', 0)
        if logs > 10:
            risk_score += 35
            reasons.append(f"أخطاء نظام متكررة ({logs}/hr)")
            actions.append("فحص السوفتوير والهارد ديسك")
            factors['Software'] = 35

        if data['humidity'] > 70: risk_score+=40; reasons.append("رطوبة عالية"); factors['Humidity']=40
        if data['voltage'] < 190: risk_score+=30; reasons.append("ضعف جهد"); factors['Elec']=30

    # 4. تحليل X-Ray
    elif dev == "الأشعة السينية (X-Ray)":
        # فشل التصوير (الجديد)
        errs = data.get('exposure_errors', 0)
        if errs > 3:
            risk_score += 45
            reasons.append("فشل متكرر في الـ Exposure")
            actions.append("فحص زر الـ Handswitch وكابلات المولد")
            factors['Generator'] = 45

        if data['tube_temp'] > 60: risk_score+=45; reasons.append("حرارة أنبوب"); factors['Temp']=45

    # النتيجة النهائية
    risk_score = min(risk_score, 100)
    if risk_score >= 50: status="خطر مرتفع 🔴"; css="crit-box"; clr="#ef4444"
    elif risk_score >= 20: status="تحذير 🟡"; css="warn-box"; clr="#f59e0b"
    else: status="آمن 🟢"; css="safe-box"; clr="#22c55e"; reasons.append("الجهاز يعمل بكفاءة"); actions.append("لا يوجد إجراء مطلوب")
    
    return risk_score, status, css, reasons, actions, factors, clr

score, status, css, reasons, actions, factors, clr = analyze_simulation(device_type, inputs)

# --- العرض ---
st.markdown("### 3️⃣ نتائج التشخيص")
c_g, c_d = st.columns([1, 2])
with c_g:
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = score, title = {'text': "مؤشر الخطر"},
        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': clr},
                 'steps': [{'range': [0, 20], 'color': '#dcfce7'}, {'range': [20, 50], 'color': '#fef3c7'}, {'range': [50, 100], 'color': '#fee2e2'}]}))
    fig_gauge.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

with c_d:
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
    </div>""", unsafe_allow_html=True)

if sum(factors.values()) > 0:
    st.markdown("---")
    st.subheader("📊 العوامل المؤثرة")
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(px.pie(names=list(factors.keys()), values=list(factors.values()), hole=0.5), use_container_width=True)
    with c2: st.plotly_chart(px.bar(x=list(factors.keys()), y=list(factors.values()), labels={'x':'العامل','y':'الخطر'}, color=list(factors.values()), color_continuous_scale='Reds'), use_container_width=True)
