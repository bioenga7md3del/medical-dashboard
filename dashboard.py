import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="المحاكي الذكي للأعطال", layout="wide", page_icon="🎛️")

# --- 2. القيم الافتراضية ---
default_values = {
    "الرنين المغناطيسي (MRI)": {
        "helium": 85.0, "comp_pressure": 20.0, "chiller_temp": 10.0, "room_temp": 22.0,
        "cont_hours": 4.0, "coil_snr": 95.0, "humidity": 45.0
    },
    "الأشعة المقطعية (CT Scan)": {
        "gantry_temp": 35.0, "voltage": 220.0, "tube_arcing": 0, "tube_age": 50000.0,
        "cont_hours": 4.0, "fan_rpm": 3000, "room_temp": 22.0, "humidity": 40.0
    },
    "الفلورسكوبي (Fluoro)": {
        "voltage": 220.0, "tube_temp": 30.0, "error_logs": 0,
        "cont_hours": 2.0, "tube_age": 10000.0, "humidity": 45.0
    },
    "الأشعة السينية (X-Ray)": {
        "tube_temp": 35.0, "voltage": 70.0, "exposure_errors": 0,
        "cont_hours": 6.0, "tube_age": 15000.0, "room_temp": 22.0
    }
}

if 'device_type' not in st.session_state: st.session_state['device_type'] = "الرنين المغناطيسي (MRI)"
def update_state(device):
    for key, val in default_values[device].items(): st.session_state[key] = val
def on_device_change(): update_state(st.session_state.device_selector)

# --- 3. CSS ---
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
.limit-badge { font-size: 0.8em; padding: 2px 8px; border-radius: 4px; background-color: #e0f2fe; color: #0369a1; font-weight: bold; float: left; }
.input-label { font-weight: bold; color: #334155; font-size: 0.95em; display: flex; justify-content: space-between; margin-bottom: 2px; }
</style>
""", unsafe_allow_html=True)

def smart_input(col, label, key, min_v, max_v, step, limit_text, help_txt=""):
    col.markdown(f"""<div class="input-label"><span>{label}</span><span class="limit-badge">{limit_text}</span></div>""", unsafe_allow_html=True)
    return col.number_input("hidden", min_value=min_v, max_value=max_v, step=step, key=key, label_visibility="collapsed", help=help_txt)

# --- 5. الهيدر ---
c_h, c_s, c_r = st.columns([2, 1, 0.5])
with c_h: st.title("🎛️ المحاكي (تحديث الحساسية العالية)"); st.caption("الآن الرطوبة والحرارة تؤثر فوراً على كل الأجهزة")
with c_s: device_type = st.selectbox("🔻 الجهاز:", list(default_values.keys()), key="device_selector", on_change=on_device_change)
with c_r: 
    st.write(""); st.write("")
    if st.button("🔄 ريسيت"): update_state(device_type); st.rerun()

if "helium" not in st.session_state and device_type == "الرنين المغناطيسي (MRI)": update_state(device_type)

# --- 6. المدخلات ---
inputs = {}
with st.container():
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    
    # 1. MRI Inputs
    if device_type == "الرنين المغناطيسي (MRI)":
        st.markdown('<div class="group-header">1️⃣ التبريد والمغناطيس</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        inputs['helium'] = smart_input(c1, "🎈 هيليوم (%)", "helium", 0.0, 100.0, 0.5, "الخطر < 60%")
        inputs['comp_pressure'] = smart_input(c2, "⚙️ ضغط كمبروسر", "comp_pressure", 0.0, 30.0, 0.5, "المثالي: 18-22")
        inputs['chiller_temp'] = smart_input(c3, "❄️ حرارة شيلر", "chiller_temp", 0.0, 50.0, 0.5, "الخطر > 20°C")
        inputs['room_temp'] = smart_input(c4, "🌡️ حرارة غرفة", "room_temp", 10.0, 45.0, 0.5, "المثالي < 24°C")
        
        st.markdown('<br><div class="group-header">2️⃣ التشغيل والبيئة</div>', unsafe_allow_html=True)
        c5, c6, c7 = st.columns(3)
        inputs['cont_hours'] = smart_input(c5, "⏱️ تشغيل متواصل", "cont_hours", 0.0, 24.0, 0.5, "يفضل < 12h")
        inputs['coil_snr'] = smart_input(c6, "📡 جودة (SNR)", "coil_snr", 0.0, 100.0, 1.0, "الخطر < 80%")
        inputs['humidity'] = smart_input(c7, "💧 الرطوبة", "humidity", 0.0, 100.0, 1.0, "الخطر > 70%")

    # 2. CT Inputs
    elif device_type == "الأشعة المقطعية (CT Scan)":
        st.markdown('<div class="group-header">1️⃣ صحة الأنبوب والكهرباء</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        inputs['gantry_temp'] = smart_input(c1, "☢️ حرارة جانتري", "gantry_temp", 10.0, 120.0, 0.5, "الخطر > 60°C")
        inputs['voltage'] = smart_input(c2, "⚡ جهد (V)", "voltage", 0.0, 300.0, 1.0, "المدى: 200-240")
        inputs['tube_arcing'] = smart_input(c3, "💥 شرارة (Arcing)", "tube_arcing", 0, 50, 1, "يجب أن يكون 0")
        inputs['tube_age'] = smart_input(c4, "⏳ عمر تيوب (Scan)", "tube_age", 0.0, 500000.0, 1000.0, "Max: 200k")

        st.markdown('<br><div class="group-header">2️⃣ البيئة والمكونات</div>', unsafe_allow_html=True)
        c5, c6, c7, c8 = st.columns(4)
        inputs['cont_hours'] = smart_input(c5, "⏱️ تشغيل متواصل", "cont_hours", 0.0, 24.0, 0.5, "يفضل < 12h")
        inputs['fan_rpm'] = smart_input(c6, "🌀 سرعة مراوح", "fan_rpm", 0, 5000, 100, "الخطر < 2000")
        inputs['room_temp'] = smart_input(c7, "🌡️ حرارة الغرفة", "room_temp", 10.0, 45.0, 0.5, "المثالي < 24°C")
        inputs['humidity'] = smart_input(c8, "💧 الرطوبة", "humidity", 0.0, 100.0, 1.0, "الخطر > 70%")

    # 3. Fluoro Inputs
    elif device_type == "الفلورسكوبي (Fluoro)":
        c1, c2, c3 = st.columns(3)
        inputs['voltage'] = smart_input(c1, "⚡ جهد (V)", "voltage", 0.0, 300.0, 1.0, "المدى: 200-240")
        inputs['tube_temp'] = smart_input(c2, "🔥 حرارة تيوب", "tube_temp", 10.0, 100.0, 0.5, "الخطر > 70°C")
        inputs['error_logs'] = smart_input(c3, "⚠️ سجل أخطاء", "error_logs", 0, 50, 1, "يجب أن يكون 0")
        
        c4, c5, c6 = st.columns(3)
        inputs['cont_hours'] = smart_input(c4, "⏱️ تشغيل", "cont_hours", 0.0, 12.0, 0.5, "Low Stress")
        inputs['tube_age'] = smart_input(c5, "⏳ عمر التيوب", "tube_age", 0.0, 100000.0, 500.0, "Max: 20k")
        inputs['humidity'] = smart_input(c6, "💧 الرطوبة", "humidity", 0.0, 100.0, 1.0, "الخطر > 70%")

    # 4. X-Ray Inputs
    elif device_type == "الأشعة السينية (X-Ray)":
        c1, c2, c3 = st.columns(3)
        inputs['tube_temp'] = smart_input(c1, "🔥 حرارة تيوب", "tube_temp", 10.0, 120.0, 0.5, "الخطر > 60°C")
        inputs['voltage'] = smart_input(c2, "⚡ جهد (kV)", "voltage", 0.0, 200.0, 1.0, "±10% من 70")
        inputs['exposure_errors'] = smart_input(c3, "🚫 فشل تصوير", "exposure_errors", 0, 20, 1, "يجب أن يكون 0")
        
        c4, c5, c6 = st.columns(3)
        inputs['cont_hours'] = smart_input(c4, "⏱️ تشغيل", "cont_hours", 0.0, 24.0, 0.5, "Low Stress")
        inputs['tube_age'] = smart_input(c5, "⏳ عمر التيوب", "tube_age", 0.0, 100000.0, 500.0, "Max: 25k")
        inputs['room_temp'] = smart_input(c6, "🌡️ حرارة الغرفة", "room_temp", 10.0, 45.0, 0.5, "المثالي < 24°C")

    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. المحرك التحليلي (تعديل: إضافة العوامل المشتركة بقوة) ---
def analyze_simulation(dev, data):
    risk_score = 0
    factors = {}
    reasons = []
    actions = []

    # ==========================================
    # 🌍 العوامل المشتركة (تطبق على الكل أولاً)
    # ==========================================
    
    # 1. حرارة الغرفة (Room Temp Impact)
    # إذا الغرفة حارة > 24، نضيف 10 نقاط فوراً للجميع
    r_temp = data.get('room_temp', 22) # (الفلورو لا يملك حساس غرفة، نعتبره 22)
    if r_temp > 24:
        risk_score += 15 # رفعنا النسبة ليكون التأثير ملحوظاً
        reasons.append(f"حرارة الغرفة مرتفعة ({r_temp}°C)")
        actions.append("فحص التكييف المركزي")
        factors['Room Env'] = 15

    # 2. الرطوبة (Humidity Impact)
    hum = data.get('humidity', 45)
    if hum > 70:
        risk_score += 20
        reasons.append(f"رطوبة عالية ({hum}%) - خطر كهربائي")
        actions.append("تشغيل مزيلات الرطوبة")
        factors['Humidity'] = 20
    elif hum < 30:
        risk_score += 10
        reasons.append(f"رطوبة منخفضة ({hum}%) - خطر Static")
        factors['Humidity'] = 10

    # 3. التشغيل المتواصل (Continuous Operation)
    hrs = data.get('cont_hours', 0)
    if hrs > 10:
        risk_score += 15
        reasons.append(f"تشغيل متواصل مفرط ({hrs} ساعة)")
        actions.append("إعطاء فترة راحة للجهاز")
        factors['Overwork'] = 15


    # ==========================================
    # 🔧 العوامل الخاصة (Specific Factors)
    # ==========================================

    # 1. الرنين
    if dev == "الرنين المغناطيسي (MRI)":
        pres = data.get('comp_pressure', 20)
        if pres < 15 or pres > 25: risk_score += 40; reasons.append(f"ضغط كمبروسر ({pres})"); actions.append("فحص Cold Head"); factors['Comp']=40
        if data.get('coil_snr', 100) < 80: risk_score += 25; reasons.append("Low SNR"); factors['Image']=25
        if data['helium'] < 40: risk_score+=50; reasons.append("خطر Quench"); factors['He']=50
        elif data['helium'] < 60: risk_score+=20; reasons.append("نقص هيليوم"); factors['He']=20
        if data['chiller_temp'] > 20: risk_score+=30; reasons.append("فشل شيلر"); factors['Cool']=30

    # 2. المقطعية
    elif dev == "الأشعة المقطعية (CT Scan)":
        arcs = data.get('tube_arcing', 0)
        if arcs > 2: risk_score += 60; reasons.append(f"شرارة متكررة ({arcs})"); actions.append("استبدال تيوب"); factors['Arcing']=60
        elif arcs > 0: risk_score += 30; reasons.append("شرارة (Arcing)"); factors['Arcing']=30
        if data.get('fan_rpm', 3000) < 2000: risk_score += 20; reasons.append("ضعف مراوح"); factors['Fan']=20
        if data['gantry_temp'] > 85: risk_score+=50; reasons.append("حرارة جانتري"); factors['Temp']=50
        if abs(data['voltage']-220)>20: risk_score+=30; reasons.append("كهرباء"); factors['Elec']=30
        # إجهاد التيوب
        if data['tube_age'] > 200000: risk_score += 15; reasons.append("التيوب قديم"); factors['Age']=15

    # 3. الفلورو
    elif dev == "الفلورسكوبي (Fluoro)":
        logs = data.get('error_logs', 0)
        if logs > 10: risk_score += 35; reasons.append("أخطاء نظام"); factors['Soft']=35
        if data['voltage'] < 190: risk_score+=30; reasons.append("ضعف جهد"); factors['Elec']=30
        if data['tube_temp'] > 70: risk_score+=30; reasons.append("حرارة أنبوب عالية"); factors['Temp']=30

    # 4. X-Ray
    elif dev == "الأشعة السينية (X-Ray)":
        errs = data.get('exposure_errors', 0)
        if errs > 3: risk_score += 45; reasons.append("فشل تصوير"); factors['Gen']=45
        if data['tube_temp'] > 60: risk_score+=45; reasons.append("حرارة أنبوب"); factors['Temp']=45

    risk_score = min(risk_score, 100)
    if risk_score >= 50: status="خطر مرتفع 🔴"; css="crit-box"; clr="#ef4444"
    elif risk_score >= 20: status="تحذير 🟡"; css="warn-box"; clr="#f59e0b"
    else: status="آمن 🟢"; css="safe-box"; clr="#22c55e"; reasons.append("يعمل بكفاءة"); actions.append("لا يوجد إجراء")
    
    return risk_score, status, css, reasons, actions, factors, clr

score, status, css, reasons, actions, factors, clr = analyze_simulation(device_type, inputs)

# --- 8. العرض ---
st.markdown("### 3️⃣ نتائج التشخيص")
c_g, c_d = st.columns([1, 2])
with c_g:
    st.plotly_chart(go.Figure(go.Indicator(
        mode = "gauge+number", value = score, title = {'text': "مؤشر الخطر"},
        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': clr},
                 'steps': [{'range': [0, 20], 'color': '#dcfce7'}, {'range': [20, 50], 'color': '#fef3c7'}, {'range': [50, 100], 'color': '#fee2e2'}]})).update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20)), use_container_width=True)

with c_d:
    st.markdown(f"""
    <div class="result-container {css}">
        <h2 style="margin-top:0; color:{clr}">{status}</h2>
        <hr style="border-color:rgba(0,0,0,0.1)">
        <div style="display:flex; gap: 20px;">
            <div style="flex:1;">
                <h4 style="margin-bottom:10px;">🧐 الأسباب:</h4>
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
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(px.pie(names=list(factors.keys()), values=list(factors.values()), title="توزيع مسببات الخطر", hole=0.5), use_container_width=True)
    with c2: st.plotly_chart(px.bar(x=list(factors.keys()), y=list(factors.values()), title="تأثير العوامل", labels={'x':'العامل','y':'الخطر'}, color=list(factors.values()), color_continuous_scale='Reds'), use_container_width=True)
