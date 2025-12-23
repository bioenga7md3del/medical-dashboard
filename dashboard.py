import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="Monitor AI - Full", layout="wide", page_icon="📡")

# --- 2. القيم الافتراضية ---
default_values = {
    "الرنين المغناطيسي (MRI)": { "helium": 85.0, "comp_pressure": 20.0, "chiller_temp": 10.0, "room_temp": 22.0, "cont_hours": 4.0, "coil_snr": 95.0, "humidity": 45.0 },
    "الأشعة المقطعية (CT Scan)": { "gantry_temp": 35.0, "voltage": 220.0, "tube_arcing": 0, "tube_age": 50000.0, "cont_hours": 4.0, "fan_rpm": 3000, "room_temp": 22.0, "humidity": 40.0 },
    "الفلورسكوبي (Fluoro)": { "voltage": 220.0, "tube_temp": 30.0, "error_logs": 0, "cont_hours": 2.0, "tube_age": 10000.0, "humidity": 45.0 },
    "الأشعة السينية (X-Ray)": { "tube_temp": 35.0, "voltage": 70.0, "exposure_errors": 0, "cont_hours": 6.0, "tube_age": 15000.0, "room_temp": 22.0 }
}

# تهيئة الذاكرة
if 'device_type' not in st.session_state: st.session_state['device_type'] = "الرنين المغناطيسي (MRI)"

def update_state():
    selected = st.session_state.get("device_selector", "الرنين المغناطيسي (MRI)")
    st.session_state['device_type'] = selected
    # تحميل القيم الافتراضية إذا لم تكن موجودة
    for key, val in default_values[selected].items():
        if key not in st.session_state:
            st.session_state[key] = val

if "device_selector" not in st.session_state:
    st.session_state["device_selector"] = "الرنين المغناطيسي (MRI)"
    update_state()

# --- 3. القائمة الجانبية (Inputs) ---
with st.sidebar:
    st.title("🎛️ لوحة التحكم")
    
    # اختيار الثيم
    is_dark = st.toggle("الوضع الداكن", value=True)
    if is_dark:
        bg_color = "#0e1117"; text_color = "#ffffff"; chart_theme = "plotly_dark"
    else:
        bg_color = "#ffffff"; text_color = "#000000"; chart_theme = "plotly_white"

    st.markdown("---")
    
    # اختيار الجهاز
    device_type = st.selectbox("اختر الجهاز:", list(default_values.keys()), key="device_selector", on_change=update_state)
    st.markdown("---")
    
    # دالة مساعدة لرسم المدخلات
    def simple_input(label, key, min_v, max_v, step):
        # التأكد من تحميل القيمة الحالية
        if key not in st.session_state: 
            st.session_state[key] = default_values[device_type].get(key, min_v)
        return st.number_input(label, min_value=min_v, max_value=max_v, step=step, key=key)

    st.subheader("📝 إدخال القراءات")

    # === 1. مدخلات الرنين (MRI) ===
    if device_type == "الرنين المغناطيسي (MRI)":
        with st.expander("التبريد والمغناطيس", expanded=True):
            inputs = {}
            inputs['helium'] = simple_input("مستوى الهيليوم (%)", "helium", 0.0, 100.0, 0.5)
            inputs['comp_pressure'] = simple_input("ضغط الكمبروسر (PSI)", "comp_pressure", 0.0, 30.0, 0.5)
            inputs['chiller_temp'] = simple_input("حرارة الشيلر (°C)", "chiller_temp", 0.0, 50.0, 0.5)
        with st.expander("البيئة والتشغيل", expanded=True):
            inputs['coil_snr'] = simple_input("جودة الإشارة (SNR)", "coil_snr", 0.0, 100.0, 1.0)
            inputs['room_temp'] = simple_input("حرارة الغرفة (°C)", "room_temp", 10.0, 45.0, 0.5)
            inputs['humidity'] = simple_input("الرطوبة (%)", "humidity", 0.0, 100.0, 1.0)
            inputs['cont_hours'] = simple_input("ساعات التشغيل", "cont_hours", 0.0, 24.0, 0.5)

    # === 2. مدخلات المقطعية (CT Scan) ===
    elif device_type == "الأشعة المقطعية (CT Scan)":
        with st.expander("الأنبوب والجانتري", expanded=True):
            inputs = {}
            inputs['gantry_temp'] = simple_input("حرارة الجانتري", "gantry_temp", 10.0, 120.0, 0.5)
            inputs['tube_arcing'] = simple_input("عدد الشرارات (Arcing)", "tube_arcing", 0, 50, 1)
            inputs['fan_rpm'] = simple_input("سرعة المراوح (RPM)", "fan_rpm", 0, 5000, 100)
            inputs['tube_age'] = simple_input("عمر التيوب (Scan Sec)", "tube_age", 0.0, 500000.0, 1000.0)
        with st.expander("الكهرباء والبيئة", expanded=True):
            inputs['voltage'] = simple_input("الجهد (Volt)", "voltage", 0.0, 300.0, 1.0)
            inputs['room_temp'] = simple_input("حرارة الغرفة", "room_temp", 10.0, 45.0, 0.5)
            inputs['humidity'] = simple_input("الرطوبة (%)", "humidity", 0.0, 100.0, 1.0)
            inputs['cont_hours'] = simple_input("ساعات التشغيل", "cont_hours", 0.0, 24.0, 0.5)

    # === 3. مدخلات الفلورسكوبي (Fluoro) ===
    elif device_type == "الفلورسكوبي (Fluoro)":
        with st.expander("حالة الجهاز", expanded=True):
            inputs = {}
            inputs['tube_temp'] = simple_input("حرارة التيوب", "tube_temp", 10.0, 100.0, 0.5)
            inputs['voltage'] = simple_input("الجهد (Volt)", "voltage", 0.0, 300.0, 1.0)
            inputs['error_logs'] = simple_input("سجل الأخطاء (Logs)", "error_logs", 0, 50, 1)
        with st.expander("البيئة", expanded=True):
            inputs['humidity'] = simple_input("الرطوبة (%)", "humidity", 0.0, 100.0, 1.0)
            inputs['cont_hours'] = simple_input("ساعات التشغيل", "cont_hours", 0.0, 24.0, 0.5)
            # قيم افتراضية مخفية للفلورو
            inputs['room_temp'] = st.session_state.get('room_temp', 22.0)

    # === 4. مدخلات الأشعة (X-Ray) ===
    elif device_type == "الأشعة السينية (X-Ray)":
        with st.expander("المولد والتيوب", expanded=True):
            inputs = {}
            inputs['tube_temp'] = simple_input("حرارة التيوب", "tube_temp", 10.0, 120.0, 0.5)
            inputs['voltage'] = simple_input("الجهد العالي (kV)", "voltage", 0.0, 200.0, 1.0)
            inputs['exposure_errors'] = simple_input("أخطاء التصوير", "exposure_errors", 0, 20, 1)
        with st.expander("بيئة الغرفة", expanded=True):
            inputs['room_temp'] = simple_input("حرارة الغرفة", "room_temp", 10.0, 45.0, 0.5)
            inputs['cont_hours'] = simple_input("ساعات العمل", "cont_hours", 0.0, 24.0, 0.5)
            # قيم افتراضية مخفية
            inputs['humidity'] = st.session_state.get('humidity', 45.0)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("استعادة القيم الافتراضية", use_container_width=True):
        # إعادة تعيين القيم للجهاز الحالي فقط
        for k, v in default_values[device_type].items():
            st.session_state[k] = v
        st.rerun()

# تطبيق الخلفية
st.markdown(f"""<style>.stApp {{ background-color: {bg_color}; color: {text_color}; }}</style>""", unsafe_allow_html=True)

# --- 4. منطق التحليل (Logic) ---
def analyze(dev, data):
    score = 0; factors = {}; reasons = []
    
    # Global Checks
    if data.get('room_temp',22) > 24: score+=15; reasons.append("حرارة الغرفة مرتفعة"); factors['Room']=15
    if data.get('humidity',45) > 70: score+=20; reasons.append("رطوبة عالية"); factors['Hum']=20
    if data.get('cont_hours',0) > 10: score+=15; reasons.append("إجهاد تشغيل"); factors['Work']=15

    # Specific Checks
    if dev == "الرنين المغناطيسي (MRI)":
        if data.get('helium', 85)<40: score+=50; reasons.append("خطر Quench"); factors['He']=50
        elif data.get('helium', 85)<60: score+=20; reasons.append("نقص هيليوم"); factors['He']=20
        if data.get('comp_pressure',20)<15 or data.get('comp_pressure',20)>25: score+=40; reasons.append("الكمبروسر"); factors['Comp']=40
        if data.get('chiller_temp',10)>20: score+=30; reasons.append("الشيلر"); factors['Cool']=30

    elif dev == "الأشعة المقطعية (CT Scan)":
        if data.get('tube_arcing',0)>0: score+=40; reasons.append("شرارة (Arcing)"); factors['Arc']=40
        if data.get('gantry_temp',35)>85: score+=50; reasons.append("حرارة جانتري"); factors['Temp']=50
        if abs(data.get('voltage',220)-220)>20: score+=30; reasons.append("تذبذب كهرباء"); factors['Elec']=30
        if data.get('fan_rpm', 3000) < 2000: score+=20; reasons.append("ضعف المراوح"); factors['Fan']=20
        
    elif dev == "الفلورسكوبي (Fluoro)": 
        if data.get('error_logs',0)>10: score+=35; reasons.append("أخطاء نظام"); factors['Soft']=35
        if data.get('voltage',220)<190: score+=30; reasons.append("انخفاض جهد"); factors['Elec']=30
        if data.get('tube_temp',30)>70: score+=30; reasons.append("حرارة التيوب"); factors['Temp']=30
        
    elif dev == "الأشعة السينية (X-Ray)":
        if data.get('exposure_errors',0)>3: score+=45; reasons.append("فشل تصوير"); factors['Gen']=45
        if data.get('tube_temp',35)>60: score+=45; reasons.append("حرارة التيوب"); factors['Temp']=45

    score = min(score, 100)
    if score >= 50: return score, "خطر / CRITICAL", "inverse", reasons, factors, "#ef4444"
    elif score >= 20: return score, "تحذير / WARNING", "off", reasons, factors, "#eab308"
    return score, "آمن / STABLE", "normal", reasons, factors, "#22c55e"

score, status_text, delta_color, reasons, factors, gauge_color = analyze(device_type, inputs)

# --- 5. واجهة العرض (Dashboard Layout) ---

st.title(f"مركز المراقبة: {device_type}")
st.markdown("---")

# 1. شريط الحالة
if score >= 50:
    st.error(f"### الحالة: {status_text} | المؤشر: {score}%", icon="🚨")
elif score >= 20:
    st.warning(f"### الحالة: {status_text} | المؤشر: {score}%", icon="⚠️")
else:
    st.success(f"### الحالة: {status_text} | المؤشر: {score}%", icon="✅")

# 2. الأرقام الرئيسية (Metrics)
st.subheader("📊 القراءات الحيوية")
col1, col2, col3, col4 = st.columns(4)

if device_type == "الرنين المغناطيسي (MRI)":
    col1.metric("الهيليوم", f"{inputs.get('helium')}%", "-Low" if inputs.get('helium')<60 else "Ok", delta_color="normal" if inputs.get('helium')>=60 else "inverse")
    col2.metric("الشيلر", f"{inputs.get('chiller_temp')}°C", "High" if inputs.get('chiller_temp')>20 else "Ok", delta_color="inverse")
    col3.metric("الضغط", f"{inputs.get('comp_pressure')} PSI")
    col4.metric("الغرفة", f"{inputs.get('room_temp')}°C", "Hot" if inputs.get('room_temp')>24 else "Ok", delta_color="inverse")
elif "CT" in device_type:
    col1.metric("الجانتري", f"{inputs.get('gantry_temp')}°C", "High" if inputs.get('gantry_temp')>60 else "Ok", delta_color="inverse")
    col2.metric("الشرارات", f"{inputs.get('tube_arcing')}", "Detected" if inputs.get('tube_arcing')>0 else "None", delta_color="inverse")
    col3.metric("المراوح", f"{inputs.get('fan_rpm')} RPM", "-Low" if inputs.get('fan_rpm')<2000 else "Ok")
    col4.metric("عمر التيوب", f"{int(inputs.get('tube_age',0)):,}")
elif device_type == "الفلورسكوبي (Fluoro)":
    col1.metric("التيوب", f"{inputs.get('tube_temp')}°C")
    col2.metric("سجل الأخطاء", f"{inputs.get('error_logs')}", "Errors" if inputs.get('error_logs')>0 else "Clean", delta_color="inverse")
    col3.metric("الفولت", f"{inputs.get('voltage')} V")
    col4.metric("الرطوبة", f"{inputs.get('humidity')}%")
else: # X-Ray
    col1.metric("التيوب", f"{inputs.get('tube_temp')}°C")
    col2.metric("أخطاء التصوير", f"{inputs.get('exposure_errors')}", "Fail" if inputs.get('exposure_errors')>0 else "Ok", delta_color="inverse")
    col3.metric("kV", f"{inputs.get('voltage')}")
    col4.metric("الغرفة", f"{inputs.get('room_temp')}°C")

st.markdown("---")

# 3. الرسوم والتحليل
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("تحليل الأسباب (Root Cause)")
    if factors:
        fig_bar = px.bar(
            x=list(factors.values()), 
            y=list(factors.keys()), 
            orientation='h',
            labels={'x': 'نسبة المساهمة', 'y': 'العامل'},
            color=list(factors.values()),
            color_continuous_scale='Reds',
            template=chart_theme
        )
        fig_bar.update_layout(coloraxis_showscale=False, height=350)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("النظام يعمل بشكل ممتاز. لا توجد عوامل خطر.")

with col_right:
    st.subheader("مؤشر الخطر")
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        title = {'text': "Risk Score"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': gauge_color},
            'steps': [
                {'range': [0, 20], 'color': "rgba(34, 197, 94, 0.2)"},
                {'range': [20, 50], 'color': "rgba(234, 179, 8, 0.2)"},
                {'range': [50, 100], 'color': "rgba(239, 68, 68, 0.2)"}
            ]
        }
    ))
    
    font_col = "white" if is_dark else "black"
    fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': font_col}, height=300, margin=dict(t=30, b=30, l=30, r=30))
    st.plotly_chart(fig_gauge, use_container_width=True)

    if reasons:
        st.write("📋 **التفاصيل:**")
        for r in reasons:
            st.markdown(f"- ⚠️ {r}")
