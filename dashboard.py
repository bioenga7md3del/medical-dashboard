import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="Medical AI Command Center", layout="wide", page_icon="☢️")

# --- 2. إدارة القيم ---
default_values = {
    "الرنين المغناطيسي (MRI)": { "helium": 85.0, "comp_pressure": 20.0, "chiller_temp": 10.0, "room_temp": 22.0, "cont_hours": 4.0, "coil_snr": 95.0, "humidity": 45.0 },
    "الأشعة المقطعية (CT Scan)": { "gantry_temp": 35.0, "voltage": 220.0, "tube_arcing": 0, "tube_age": 50000.0, "cont_hours": 4.0, "fan_rpm": 3000, "room_temp": 22.0, "humidity": 40.0 },
    "الفلورسكوبي (Fluoro)": { "voltage": 220.0, "tube_temp": 30.0, "error_logs": 0, "cont_hours": 2.0, "tube_age": 10000.0, "humidity": 45.0 },
    "الأشعة السينية (X-Ray)": { "tube_temp": 35.0, "voltage": 70.0, "exposure_errors": 0, "cont_hours": 6.0, "tube_age": 15000.0, "room_temp": 22.0 }
}

if 'device_type' not in st.session_state: st.session_state['device_type'] = "الرنين المغناطيسي (MRI)"
def update_state(device):
    for key, val in default_values[device].items(): st.session_state[key] = val
def on_device_change(): update_state(st.session_state.device_selector)

# --- 3. CSS التصميم الطبي الاحترافي (Dark Theme) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; }

/* الخلفية الداكنة */
.stApp { background-color: #0e1117; color: #fafafa; }

/* كروت المحتوى */
.glass-card {
    background-color: #1e2329;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #2d333b;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    margin-bottom: 20px;
}

/* العناوين */
h1, h2, h3, h4 { color: #e6e6e6; font-weight: 700; }
.highlight { color: #00bcd4; }

/* شارات الحدود */
.limit-tag {
    background: #0f3443; color: #00bcd4;
    font-size: 0.75rem; padding: 2px 8px; border-radius: 4px;
    border: 1px solid #005662; float: left;
}

/* صناديق الحالة */
.status-box { padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 15px; }
.safe { background: rgba(34, 197, 94, 0.2); border: 1px solid #22c55e; color: #4ade80; }
.warn { background: rgba(234, 179, 8, 0.2); border: 1px solid #eab308; color: #facc15; }
.crit { background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; color: #f87171; }

/* أزرار */
div.stButton > button {
    width: 100%; background: #262730; color: white; border: 1px solid #41444e;
}
div.stButton > button:hover { border-color: #00bcd4; color: #00bcd4; }

/* تحسين المدخلات */
.stNumberInput input { background-color: #0e1117; color: white; }
div[data-baseweb="select"] > div { background-color: #0e1117; color: white; }
</style>
""", unsafe_allow_html=True)

# دالة المدخلات
def smart_input(col, label, key, min_v, max_v, step, limit_text, icon="🔹"):
    col.markdown(f"""
    <div style="margin-bottom:5px;">
        <span style="font-size:0.9em; font-weight:bold; color:#cfd8dc;">{icon} {label}</span>
        <span class="limit-tag">{limit_text}</span>
    </div>""", unsafe_allow_html=True)
    return col.number_input("hidden", min_value=min_v, max_value=max_v, step=step, key=key, label_visibility="collapsed")

# --- 4. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2752/2752174.png", width=70)
    st.title("لوحة التحكم")
    st.markdown("---")
    device_type = st.selectbox("اختر الجهاز:", list(default_values.keys()), key="device_selector", on_change=on_device_change)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 إعادة ضبط القيم"):
        update_state(st.session_state.device_selector)
        st.rerun()
    st.markdown("---")
    st.caption("نظام مراقبة الأجهزة الطبية الذكي v2.0")

if "helium" not in st.session_state and st.session_state.device_type == "الرنين المغناطيسي (MRI)": update_state(st.session_state.device_type)

# --- 5. الواجهة الرئيسية ---

# العنوان الرئيسي
st.markdown(f"""<h2>🏥 مركز القيادة: <span class='highlight'>{device_type}</span></h2>""", unsafe_allow_html=True)

# تقسيم الشاشة: مدخلات (يمين) - نتائج (يسار)
col_inputs, col_dashboard = st.columns([1, 2])

# ====================
# 🎛️ قسم المدخلات (يمين)
# ====================
with col_inputs:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### ⚙️ لوحة التشغيل")
    
    # تبويبات داخلية
    tab1, tab2 = st.tabs(["المؤشرات الحيوية", "البيئة والتشغيل"])
    
    inputs = {}
    
    with tab1:
        st.write("")
        if device_type == "الرنين المغناطيسي (MRI)":
            inputs['helium'] = smart_input(st, "مستوى الهيليوم", "helium", 0.0, 100.0, 0.5, "> 60%", "🎈")
            inputs['comp_pressure'] = smart_input(st, "ضغط الكمبروسر", "comp_pressure", 0.0, 30.0, 0.5, "18-22 PSI", "⚙️")
            inputs['chiller_temp'] = smart_input(st, "حرارة الشيلر", "chiller_temp", 0.0, 50.0, 0.5, "< 20°C", "❄️")
            inputs['coil_snr'] = smart_input(st, "جودة الإشارة SNR", "coil_snr", 0.0, 100.0, 1.0, "> 80%", "📡")

        elif device_type == "الأشعة المقطعية (CT Scan)":
            inputs['gantry_temp'] = smart_input(st, "حرارة الجانتري", "gantry_temp", 10.0, 120.0, 0.5, "< 60°C", "☢️")
            inputs['voltage'] = smart_input(st, "الجهد (V)", "voltage", 0.0, 300.0, 1.0, "220±20", "⚡")
            inputs['tube_arcing'] = smart_input(st, "عدد الشرارات", "tube_arcing", 0, 50, 1, "0 فقط", "💥")
            inputs['fan_rpm'] = smart_input(st, "سرعة المراوح", "fan_rpm", 0, 5000, 100, "> 2000", "🌀")

        elif device_type == "الفلورسكوبي (Fluoro)":
            inputs['voltage'] = smart_input(st, "الجهد (V)", "voltage", 0.0, 300.0, 1.0, "220±20", "⚡")
            inputs['tube_temp'] = smart_input(st, "حرارة التيوب", "tube_temp", 10.0, 100.0, 0.5, "< 70°C", "🔥")
            inputs['error_logs'] = smart_input(st, "سجل الأخطاء", "error_logs", 0, 50, 1, "0 Log", "⚠️")

        elif device_type == "الأشعة السينية (X-Ray)":
            inputs['tube_temp'] = smart_input(st, "حرارة التيوب", "tube_temp", 10.0, 120.0, 0.5, "< 60°C", "🔥")
            inputs['voltage'] = smart_input(st, "جهد عالي (kV)", "voltage", 0.0, 200.0, 1.0, "70±10", "⚡")
            inputs['exposure_errors'] = smart_input(st, "فشل التصوير", "exposure_errors", 0, 20, 1, "0 Err", "🚫")

    with tab2:
        st.write("")
        inputs['room_temp'] = smart_input(st, "حرارة الغرفة", "room_temp", 10.0, 45.0, 0.5, "< 24°C", "🌡️")
        inputs['humidity'] = smart_input(st, "الرطوبة %", "humidity", 0.0, 100.0, 1.0, "30-70%", "💧")
        inputs['cont_hours'] = smart_input(st, "ساعات التشغيل", "cont_hours", 0.0, 24.0, 0.5, "< 10h", "⏱️")
        
        limit_txt = "200k" if "CT" in device_type else "20k"
        inputs['tube_age'] = smart_input(st, "عمر التيوب", "tube_age", 0.0, 500000.0, 1000.0, f"Max {limit_txt}", "⏳")

    st.markdown('</div>', unsafe_allow_html=True)

# ====================
# 🖥️ قسم النتائج (يسار)
# ====================

# المحرك التحليلي
def analyze(dev, data):
    score = 0; factors = {}; reasons = []; actions = []
    
    # Global
    if data.get('room_temp',22) > 24: score+=15; reasons.append(f"حرارة الغرفة {data['room_temp']}°"); factors['Room']=15
    if data.get('humidity',45) > 70: score+=20; reasons.append(f"رطوبة عالية {data['humidity']}%"); factors['Hum']=20
    if data.get('cont_hours',0) > 10: score+=15; reasons.append("إجهاد تشغيل"); factors['Work']=15

    # Specific
    if dev == "الرنين المغناطيسي (MRI)":
        if data['helium']<40: score+=50; reasons.append("خطر Quench"); factors['He']=50
        elif data['helium']<60: score+=20; reasons.append("نقص هيليوم"); factors['He']=20
        p = data.get('comp_pressure',20)
        if p<15 or p>25: score+=40; reasons.append("ضغط كمبروسر"); factors['Comp']=40
        if data.get('coil_snr',100)<80: score+=25; reasons.append("تشويش صورة"); factors['Img']=25
        if data['chiller_temp']>20: score+=30; reasons.append("فشل شيلر"); factors['Cool']=30

    elif dev == "الأشعة المقطعية (CT Scan)":
        a = data.get('tube_arcing',0)
        if a>0: score+=30+(a*10); reasons.append("شرارة (Arcing)"); factors['Arc']=40
        if data['gantry_temp']>85: score+=50; reasons.append("حرارة جانتري"); factors['Temp']=50
        if abs(data['voltage']-220)>20: score+=30; reasons.append("كهرباء"); factors['Elec']=30
        if data.get('fan_rpm',3000)<2000: score+=20; reasons.append("مراوح"); factors['Fan']=20
        if data['tube_age']>200000: score+=15; reasons.append("عمر التيوب"); factors['Age']=15

    elif dev == "الفلورسكوبي (Fluoro)":
        if data.get('error_logs',0)>10: score+=35; reasons.append("أخطاء نظام"); factors['Soft']=35
        if data['voltage']<190: score+=30; reasons.append("كهرباء"); factors['Elec']=30
        if data['tube_temp']>70: score+=30; reasons.append("حرارة"); factors['Temp']=30

    elif dev == "الأشعة السينية (X-Ray)":
        if data.get('exposure_errors',0)>3: score+=45; reasons.append("فشل تصوير"); factors['Gen']=45
        if data['tube_temp']>60: score+=45; reasons.append("حرارة"); factors['Temp']=45

    score = min(score, 100)
    if score >= 50: status="DANGER / خطر"; css="crit"; clr="#ef4444"
    elif score >= 20: status="WARNING / تحذير"; css="warn"; clr="#eab308"
    else: status="SAFE / آمن"; css="safe"; clr="#22c55e"
    
    return score, status, css, reasons, factors, clr

score, status, css, reasons, factors, clr = analyze(device_type, inputs)

with col_dashboard:
    # 1. شريط الحالة العلوي (HUD)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    hud1, hud2, hud3, hud4 = st.columns(4)
    
    # دالة لطباعة الأرقام بشكل جميل
    def metric_card(col, label, value, suffix, color="white"):
        col.markdown(f"""
        <div style="text-align:center;">
            <span style="font-size:0.8em; color:#9ca3af;">{label}</span><br>
            <span style="font-size:1.5em; font-weight:bold; color:{color};">{value}</span>
            <span style="font-size:0.8em; color:#9ca3af;">{suffix}</span>
        </div>
        """, unsafe_allow_html=True)

    # عرض بيانات الـ HUD حسب الجهاز
    if device_type == "الرنين المغناطيسي (MRI)":
        metric_card(hud1, "الهيليوم", inputs['helium'], "%", "#00bcd4")
        metric_card(hud2, "الشيلر", inputs['chiller_temp'], "°C", "#ef4444" if inputs['chiller_temp']>20 else "white")
        metric_card(hud3, "الضغط", inputs['comp_pressure'], "PSI")
        metric_card(hud4, "الغرفة", inputs['room_temp'], "°C")
    elif "CT" in device_type:
        metric_card(hud1, "الجانتري", inputs['gantry_temp'], "°C")
        metric_card(hud2, "الشرارات", inputs['tube_arcing'], "Event", "#ef4444" if inputs['tube_arcing']>0 else "white")
        metric_card(hud3, "الفولت", inputs['voltage'], "V")
        metric_card(hud4, "المراوح", inputs['fan_rpm'], "RPM")
    else:
        metric_card(hud1, "التيوب", inputs['tube_temp'], "°C")
        metric_card(hud2, "الفولت", inputs['voltage'], "V")
        metric_card(hud3, "الغرفة", inputs['room_temp'], "°C")
        metric_card(hud4, "الرطوبة", inputs['humidity'], "%")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. التشخيص والعداد
    c_res1, c_res2 = st.columns([1.5, 1])
    
    with c_res1:
        st.markdown(f"""
        <div class="glass-card" style="height:250px; display:flex; flex-direction:column; justify-content:center;">
            <div class="status-box {css}" style="font-size:1.5em;">{status}</div>
            <div style="color:#e0e0e0;">
                <b>📋 التشخيص التحليلي:</b>
                <ul style="margin-top:5px; color:#b0bec5;">
                    {''.join([f'<li>{r}</li>' for r in (reasons if reasons else ["جميع المؤشرات ضمن النطاق الطبيعي"])])}
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_res2:
        st.markdown('<div class="glass-card" style="height:250px;">', unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = score,
            title = {'text': "مؤشر الخطر", 'font': {'color': 'white'}},
            number = {'font': {'color': 'white'}},
            gauge = {'axis': {'range': [None, 100], 'tickcolor': "white"}, 'bar': {'color': clr},
                     'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 0,
                     'steps': [{'range': [0, 20], 'color': 'rgba(34, 197, 94, 0.3)'}, 
                               {'range': [20, 50], 'color': 'rgba(234, 179, 8, 0.3)'}, 
                               {'range': [50, 100], 'color': 'rgba(239, 68, 68, 0.3)'}]}))
        fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=200, margin=dict(l=10,r=10,t=40,b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. الرسوم البيانية
    if sum(factors.values()) > 0:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 📊 تحليل الأسباب الجذرية")
        cp1, cp2 = st.columns(2)
        with cp1:
            fig_pie = px.pie(names=list(factors.keys()), values=list(factors.values()), hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, showlegend=False, margin=dict(t=0,b=0,l=0,r=0), height=150)
            st.plotly_chart(fig_pie, use_container_width=True)
        with cp2:
            fig_bar = px.bar(x=list(factors.keys()), y=list(factors.values()), color=list(factors.values()), color_continuous_scale='Reds')
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, xaxis_title="", yaxis_title="درجة الخطر", coloraxis_showscale=False, margin=dict(t=0,b=0,l=0,r=0), height=150)
            st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
