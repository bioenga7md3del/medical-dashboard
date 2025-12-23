import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="Smart Medical Monitor", layout="wide", page_icon="🩺")

# --- 2. تعريف القيم والدوال (يجب أن تكون في البداية) ---
default_values = {
    "الرنين المغناطيسي (MRI)": { "helium": 85.0, "comp_pressure": 20.0, "chiller_temp": 10.0, "room_temp": 22.0, "cont_hours": 4.0, "coil_snr": 95.0, "humidity": 45.0 },
    "الأشعة المقطعية (CT Scan)": { "gantry_temp": 35.0, "voltage": 220.0, "tube_arcing": 0, "tube_age": 50000.0, "cont_hours": 4.0, "fan_rpm": 3000, "room_temp": 22.0, "humidity": 40.0 },
    "الفلورسكوبي (Fluoro)": { "voltage": 220.0, "tube_temp": 30.0, "error_logs": 0, "cont_hours": 2.0, "tube_age": 10000.0, "humidity": 45.0 },
    "الأشعة السينية (X-Ray)": { "tube_temp": 35.0, "voltage": 70.0, "exposure_errors": 0, "cont_hours": 6.0, "tube_age": 15000.0, "room_temp": 22.0 }
}

# دالة تحديث الحالة (تستخدم في الـ Callbacks)
def update_state():
    # نأخذ الجهاز المختار حالياً من الـ Session State
    selected_device = st.session_state.get("device_selector", "الرنين المغناطيسي (MRI)")
    # نقوم بتحديث القيم بناءً عليه
    for key, val in default_values[selected_device].items():
        st.session_state[key] = val

# تهيئة القيم لأول مرة فقط
if 'device_selector' not in st.session_state:
    st.session_state['device_selector'] = "الرنين المغناطيسي (MRI)"
    update_state() # استدعاء أولي

# --- 3. CSS (التصميم الانسيابي) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; }
.block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
.hero-banner {
    padding: 20px 30px; border-radius: 15px; margin-bottom: 30px;
    display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}
.hero-safe { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; }
.hero-warn { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; }
.hero-crit { background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); color: white; }
h1, h2, h3 { font-weight: 800; }
[data-testid="stSidebar"] { background-color: #f8fafc; border-left: 1px solid #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# --- 4. القائمة الجانبية (Inputs) ---
with st.sidebar:
    st.title("🎛️ وحدة التحكم")
    
    # القائمة المنسدلة للجهاز (مع Callback لتحديث القيم فور التغيير)
    device_type = st.selectbox(
        "الجهاز المتصل:", 
        list(default_values.keys()), 
        key="device_selector", 
        on_change=update_state
    )
    
    st.markdown("### ⚙️ المدخلات الحية")
    
    inputs = {}
    
    # دالة إدخال آمنة
    def simple_input(label, key, min_v, max_v, step):
        # التأكد من وجود القيمة في الذاكرة لتجنب الأخطاء
        if key not in st.session_state:
            st.session_state[key] = default_values[device_type].get(key, min_v)
        return st.number_input(label, min_value=min_v, max_value=max_v, step=step, key=key)

    # عرض المدخلات حسب نوع الجهاز
    if device_type == "الرنين المغناطيسي (MRI)":
        with st.expander("تبريد ومغناطيس", expanded=True):
            inputs['helium'] = simple_input("He Level (%)", "helium", 0.0, 100.0, 0.5)
            inputs['chiller_temp'] = simple_input("Chiller (°C)", "chiller_temp", 0.0, 50.0, 0.5)
            inputs['comp_pressure'] = simple_input("Pressure (PSI)", "comp_pressure", 0.0, 30.0, 0.5)
        with st.expander("بيئة وتشغيل", expanded=True):
            inputs['room_temp'] = simple_input("Room (°C)", "room_temp", 10.0, 45.0, 0.5)
            inputs['humidity'] = simple_input("Humidity (%)", "humidity", 0.0, 100.0, 1.0)
            inputs['cont_hours'] = simple_input("Work Hours", "cont_hours", 0.0, 24.0, 0.5)
            inputs['coil_snr'] = simple_input("SNR", "coil_snr", 0.0, 100.0, 1.0)

    elif device_type == "الأشعة المقطعية (CT Scan)":
        with st.expander("تيوب وجانتري", expanded=True):
            inputs['gantry_temp'] = simple_input("Gantry (°C)", "gantry_temp", 10.0, 120.0, 0.5)
            inputs['tube_arcing'] = simple_input("Arcing Count", "tube_arcing", 0, 50, 1)
            inputs['fan_rpm'] = simple_input("Fan RPM", "fan_rpm", 0, 5000, 100)
        with st.expander("كهرباء وتشغيل", expanded=True):
            inputs['voltage'] = simple_input("Voltage (V)", "voltage", 0.0, 300.0, 1.0)
            inputs['room_temp'] = simple_input("Room (°C)", "room_temp", 10.0, 45.0, 0.5)
            inputs['humidity'] = simple_input("Humidity (%)", "humidity", 0.0, 100.0, 1.0)
            inputs['cont_hours'] = simple_input("Hours", "cont_hours", 0.0, 24.0, 0.5)
            inputs['tube_age'] = simple_input("Tube Age", "tube_age", 0.0, 500000.0, 1000.0)

    elif device_type == "الفلورسكوبي (Fluoro)":
        inputs['voltage'] = simple_input("Voltage", "voltage", 0.0, 300.0, 1.0)
        inputs['tube_temp'] = simple_input("Tube Temp", "tube_temp", 0.0, 100.0, 0.5)
        inputs['error_logs'] = simple_input("Error Logs", "error_logs", 0, 50, 1)
        inputs['humidity'] = simple_input("Humidity", "humidity", 0.0, 100.0, 1.0)
        # قيم افتراضية مخفية للفلورو لتجنب اخطاء التحليل
        inputs['cont_hours'] = st.session_state.get('cont_hours', 2.0)
        inputs['room_temp'] = st.session_state.get('room_temp', 22.0)

    elif device_type == "الأشعة السينية (X-Ray)":
        inputs['tube_temp'] = simple_input("Tube Temp", "tube_temp", 0.0, 100.0, 0.5)
        inputs['voltage'] = simple_input("kV", "voltage", 0.0, 200.0, 1.0)
        inputs['exposure_errors'] = simple_input("Exposure Errs", "exposure_errors", 0, 20, 1)
        inputs['room_temp'] = simple_input("Room Temp", "room_temp", 10.0, 45.0, 0.5)
        # قيم افتراضية مخفية
        inputs['humidity'] = st.session_state.get('humidity', 45.0)
        inputs['cont_hours'] = st.session_state.get('cont_hours', 6.0)

    st.markdown("---")
    if st.button("استعادة القيم الافتراضية", use_container_width=True):
        update_state()
        st.rerun()

# --- 5. منطق التحليل (Logic) ---
def analyze(dev, data):
    score = 0; factors = {}; reasons = []
    
    # Global Rules
    if data.get('room_temp',22) > 24: score+=15; reasons.append("حرارة غرفة مرتفعة"); factors['Room']=15
    if data.get('humidity',45) > 70: score+=20; reasons.append("رطوبة عالية"); factors['Hum']=20
    if data.get('cont_hours',0) > 10: score+=15; reasons.append("إجهاد تشغيل"); factors['Work']=15

    # Specific Rules
    if dev == "الرنين المغناطيسي (MRI)":
        if data.get('helium', 85)<40: score+=50; reasons.append("Quench Risk"); factors['He']=50
        elif data.get('helium', 85)<60: score+=20; reasons.append("Low Helium"); factors['He']=20
        if data.get('comp_pressure',20)<15 or data.get('comp_pressure',20)>25: score+=40; reasons.append("Compressor"); factors['Comp']=40
        if data.get('chiller_temp',10)>20: score+=30; reasons.append("Chiller Fail"); factors['Cool']=30

    elif dev == "الأشعة المقطعية (CT Scan)":
        if data.get('tube_arcing',0)>0: score+=40; reasons.append("Arcing Detected"); factors['Arc']=40
        if data.get('gantry_temp',35)>85: score+=50; reasons.append("Gantry Overheat"); factors['Temp']=50
        if abs(data.get('voltage',220)-220)>20: score+=30; reasons.append("Power Unstable"); factors['Elec']=30
        
    elif dev == "الفلورسكوبي (Fluoro)" and data.get('voltage',220)<190: 
        score+=30; reasons.append("Low Voltage"); factors['Elec']=30
    elif dev == "الأشعة السينية (X-Ray)" and data.get('exposure_errors',0)>3: 
        score+=45; reasons.append("Gen Failure"); factors['Gen']=45

    score = min(score, 100)
    if score >= 50: return score, "CRITICAL", "hero-crit", reasons, factors
    elif score >= 20: return score, "WARNING", "hero-warn", reasons, factors
    return score, "OPTIMAL", "hero-safe", reasons, factors

score, status, css_class, reasons, factors = analyze(device_type, inputs)

# --- 6. واجهة العرض (Dashboard) ---

# A. شريط الحالة العملاق
st.markdown(f"""
<div class="hero-banner {css_class}">
    <div>
        <div style="font-size:1.2em; opacity:0.9;">حالة النظام الحالية</div>
        <div style="font-size:3.5em; font-weight:800; line-height:1.1;">{status}</div>
        <div style="font-size:1em; opacity:0.9; margin-top:5px;">{' | '.join(reasons) if reasons else "جميع الأنظمة تعمل بكفاءة تامة"}</div>
    </div>
    <div style="text-align:left;">
        <div style="font-size:4em; font-weight:900;">{score}%</div>
        <div style="font-size:1em;">مؤشر الخطر</div>
    </div>
</div>
""", unsafe_allow_html=True)

# B. الأرقام العائمة (Metrics)
m1, m2, m3, m4 = st.columns(4)
def clean_metric(col, label, value, delta=None):
    col.metric(label=label, value=value, delta=delta)

if device_type == "الرنين المغناطيسي (MRI)":
    clean_metric(m1, "مستوى الهيليوم", f"{inputs.get('helium',0)}%", "-2%" if inputs.get('helium',0)<60 else "Normal")
    clean_metric(m2, "حرارة الشيلر", f"{inputs.get('chiller_temp',0)}°C", "High" if inputs.get('chiller_temp',0)>20 else "Ok")
    clean_metric(m3, "ضغط الضاغط", f"{inputs.get('comp_pressure',0)} PSI", None)
    clean_metric(m4, "حرارة الغرفة", f"{inputs.get('room_temp',0)}°C", "Hot" if inputs.get('room_temp',0)>24 else "Stable")
elif "CT" in device_type:
    clean_metric(m1, "حرارة الجانتري", f"{inputs.get('gantry_temp',0)}°C", "Hot" if inputs.get('gantry_temp',0)>60 else "Ok")
    clean_metric(m2, "الشرارات", f"{inputs.get('tube_arcing',0)}", "Detected" if inputs.get('tube_arcing',0)>0 else "None")
    clean_metric(m3, "سرعة المراوح", f"{inputs.get('fan_rpm',0)} RPM", "-Low" if inputs.get('fan_rpm',0)<2000 else "Optimal")
    clean_metric(m4, "عمر التيوب", f"{int(inputs.get('tube_age',0)):,}", None)
else:
    clean_metric(m1, "الفولت", f"{inputs.get('voltage', 0)} V", None)
    clean_metric(m2, "حرارة التيوب", f"{inputs.get('tube_temp', 0)}°C", None)
    clean_metric(m3, "الرطوبة", f"{inputs.get('humidity', 0)}%", None)
    clean_metric(m4, "ساعات العمل", f"{inputs.get('cont_hours', 0)}h", None)

st.markdown("---")

# C. الرسوم البيانية
c_main, c_side = st.columns([2, 1])

with c_main:
    st.subheader("📊 التحليل البياني للأسباب")
    if sum(factors.values()) > 0:
        fig = px.bar(
            x=list(factors.keys()), 
            y=list(factors.values()),
            orientation='h',
            color=list(factors.values()),
            color_continuous_scale=['#22c55e', '#eab308', '#ef4444'],
            title="مصادر الخطر الحالية"
        )
        fig.update_layout(height=350, xaxis_title="نسبة المساهمة في الخطر", yaxis_title="العامل", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown("""
        <div style="background:#f0fdf4; border-radius:10px; padding:40px; text-align:center; color:#166534;">
            <h3>🛡️ التحليل السليم</h3>
            <p>خوارزميات الذكاء الاصطناعي لم ترصد أي شذوذ في البيانات الحالية.</p>
        </div>
        """, unsafe_allow_html=True)

with c_side:
    st.subheader("📈 مؤشر الأداء")
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Risk Index"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "rgba(0,0,0,0)"},
            'steps': [
                {'range': [0, score], 'color': "#ef4444" if score>50 else "#eab308" if score>20 else "#22c55e"},
                {'range': [score, 100], 'color': "#e2e8f0"}
            ],
            'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': score}
        }
    ))
    fig_gauge.update_layout(height=300, margin=dict(l=20,r=20,t=50,b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)
