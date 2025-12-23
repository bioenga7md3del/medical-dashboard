import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="Medical AI Command Center", layout="wide", page_icon="🏥")

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
    for key, val in default_values[selected].items():
        if key not in st.session_state:
            st.session_state[key] = val

if "device_selector" not in st.session_state:
    st.session_state["device_selector"] = "الرنين المغناطيسي (MRI)"
    update_state()

# --- 3. القائمة الجانبية ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2752/2752174.png", width=70)
    st.title("الإعدادات")
    is_dark = st.toggle("🌙 الوضع الليلي", value=True)
    st.markdown("---")
    
    device_type = st.selectbox("اختر الجهاز:", list(default_values.keys()), key="device_selector", on_change=update_state)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔄 إعادة ضبط القيم", use_container_width=True):
        for k, v in default_values[device_type].items():
            st.session_state[k] = v
        st.rerun()

# --- 4. الألوان والثيم (CSS للكروت الزجاجية) ---
if is_dark:
    bg_color = "#0e1117"; card_bg = "#1e2329"; text_color = "#fafafa"; sub_text = "#cfd8dc"
    border_color = "#2d333b"; input_bg = "#0e1117"; chart_template = "plotly_dark"
    shadow = "rgba(0,0,0,0.5)"; highlight = "#00bcd4"
else:
    bg_color = "#f8fafc"; card_bg = "#ffffff"; text_color = "#0f172a"; sub_text = "#475569"
    border_color = "#e2e8f0"; input_bg = "#ffffff"; chart_template = "plotly_white"
    shadow = "rgba(0,0,0,0.05)"; highlight = "#0284c7"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');
html, body, [class*="css"] {{ font-family: 'Tajawal', sans-serif; direction: rtl; }}
.stApp {{ background-color: {bg_color}; color: {text_color}; }}

/* تصميم الكارت الزجاجي */
.glass-card {{
    background-color: {card_bg}; padding: 20px; border-radius: 12px;
    border: 1px solid {border_color}; box-shadow: 0 4px 20px {shadow}; margin-bottom: 20px;
}}

h1, h2, h3, h4 {{ color: {text_color}; font-weight: 700; }}
.highlight {{ color: {highlight}; }}
.input-label {{ font-size:0.9em; font-weight:bold; color:{sub_text}; }}

.limit-tag {{
    background: {'#0f3443' if is_dark else '#e0f2fe'}; color: {'#00bcd4' if is_dark else '#0284c7'};
    font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; border: 1px solid {'#005662' if is_dark else '#bae6fd'}; float: left;
}}

.status-box {{ padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 15px; }}
.crit {{ background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #ef4444; }}
.warn {{ background: rgba(234, 179, 8, 0.1); border: 1px solid #eab308; color: #eab308; }}
.safe {{ background: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; color: #22c55e; }}

.stNumberInput input {{ background-color: {input_bg}; color: {text_color}; }}
div[data-baseweb="select"] > div {{ background-color: {input_bg}; color: {text_color}; }}
div[data-baseweb="tab-list"] {{ background-color: transparent; }}
</style>
""", unsafe_allow_html=True)

def smart_input(col, label, key, min_v, max_v, step, limit_text, icon="🔹"):
    if key not in st.session_state: st.session_state[key] = default_values[device_type].get(key, min_v)
    col.markdown(f"""<div style="margin-bottom:5px;"><span class="input-label">{icon} {label}</span><span class="limit-tag">{limit_text}</span></div>""", unsafe_allow_html=True)
    return col.number_input("hidden", min_value=min_v, max_value=max_v, step=step, key=key, label_visibility="collapsed")

# --- 5. الهيكل الرئيسي ---
st.markdown(f"""<h2>🏥 مركز القيادة: <span class='highlight'>{device_type}</span></h2>""", unsafe_allow_html=True)

col_inputs, col_dashboard = st.columns([1, 2.2], gap="medium")

# === قسم المدخلات (يمين) ===
with col_inputs:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### ⚙️ لوحة التشغيل")
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
            # قيم مخفية
            inputs['cont_hours'] = st.session_state.get('cont_hours', 2.0)
            inputs['room_temp'] = st.session_state.get('room_temp', 22.0)
        elif device_type == "الأشعة السينية (X-Ray)":
            inputs['tube_temp'] = smart_input(st, "حرارة التيوب", "tube_temp", 10.0, 120.0, 0.5, "< 60°C", "🔥")
            inputs['voltage'] = smart_input(st, "جهد عالي (kV)", "voltage", 0.0, 200.0, 1.0, "70±10", "⚡")
            inputs['exposure_errors'] = smart_input(st, "فشل التصوير", "exposure_errors", 0, 20, 1, "0 Err", "🚫")
            # قيم مخفية
            inputs['cont_hours'] = st.session_state.get('cont_hours', 6.0)
            inputs['room_temp'] = st.session_state.get('room_temp', 22.0)

    with tab2:
        st.write("")
        inputs['room_temp'] = smart_input(st, "حرارة الغرفة", "room_temp", 10.0, 45.0, 0.5, "< 24°C", "🌡️")
        inputs['humidity'] = smart_input(st, "الرطوبة %", "humidity", 0.0, 100.0, 1.0, "30-70%", "💧")
        inputs['cont_hours'] = smart_input(st, "ساعات التشغيل", "cont_hours", 0.0, 24.0, 0.5, "< 10h", "⏱️")
        limit_txt = "200k" if "CT" in device_type else "20k"
        inputs['tube_age'] = smart_input(st, "عمر التيوب", "tube_age", 0.0, 500000.0, 1000.0, f"Max {limit_txt}", "⏳")
    st.markdown('</div>', unsafe_allow_html=True)

# === منطق التحليل ===
def analyze(dev, data):
    score = 0; factors = {}; reasons = []
    
    # Global Checks
    if data.get('room_temp',22) > 24: score+=15; reasons.append(f"حرارة الغرفة"); factors['Room']=15
    if data.get('humidity',45) > 70: score+=20; reasons.append(f"رطوبة عالية"); factors['Hum']=20
    if data.get('cont_hours',0) > 10: score+=15; reasons.append("إجهاد تشغيل"); factors['Work']=15

    # Specific Checks
    if dev == "الرنين المغناطيسي (MRI)":
        if data.get('helium', 85)<40: score+=50; reasons.append("خطر Quench"); factors['He']=50
        elif data.get('helium', 85)<60: score+=20; reasons.append("نقص هيليوم"); factors['He']=20
        p = data.get('comp_pressure',20)
        if p<15 or p>25: score+=40; reasons.append("ضغط كمبروسر"); factors['Comp']=40
        if data.get('chiller_temp',10)>20: score+=30; reasons.append("فشل شيلر"); factors['Cool']=30

    elif dev == "الأشعة المقطعية (CT Scan)":
        if data.get('tube_arcing',0)>0: score+=40; reasons.append("شرارة (Arcing)"); factors['Arc']=40
        if data.get('gantry_temp',35)>85: score+=50; reasons.append("حرارة جانتري"); factors['Temp']=50
        if abs(data.get('voltage',220)-220)>20: score+=30; reasons.append("تذبذب كهرباء"); factors['Elec']=30
        
    elif dev == "الفلورسكوبي (Fluoro)":
        if data.get('voltage',220)<190: score+=30; reasons.append("انخفاض جهد"); factors['Elec']=30
        if data.get('error_logs',0)>10: score+=35; reasons.append("أخطاء نظام"); factors['Soft']=35
        
    elif dev == "الأشعة السينية (X-Ray)":
        if data.get('exposure_errors',0)>3: score+=45; reasons.append("فشل تصوير"); factors['Gen']=45

    score = min(score, 100)
    if score >= 50: return score, "DANGER / خطر", "crit", reasons, factors, "#ef4444"
    elif score >= 20: return score, "WARNING / تحذير", "warn", reasons, factors, "#eab308"
    return score, "SAFE / آمن", "safe", reasons, factors, "#22c55e"

score, status, css, reasons, factors, clr = analyze(device_type, inputs)

# === قسم النتائج (الداشبورد) ===
with col_dashboard:
    # 1. شريط الحالة العلوي (HUD)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    hud1, hud2, hud3, hud4 = st.columns(4)
    def metric_card(col, label, value, suffix, alert_cond=False):
        val_color = "#ef4444" if alert_cond else text_color
        col.markdown(f"""<div style="text-align:center;"><span style="font-size:0.8em; color:{sub_text};">{label}</span><br><span style="font-size:1.5em; font-weight:bold; color:{val_color};">{value}</span><span style="font-size:0.8em; color:{sub_text};">{suffix}</span></div>""", unsafe_allow_html=True)

    if device_type == "الرنين المغناطيسي (MRI)":
        metric_card(hud1, "الهيليوم", inputs.get('helium',0), "%", inputs.get('helium',0)<60)
        metric_card(hud2, "الشيلر", inputs.get('chiller_temp',0), "°C", inputs.get('chiller_temp',0)>20)
        metric_card(hud3, "الضغط", inputs.get('comp_pressure',0), "PSI")
        metric_card(hud4, "الغرفة", inputs.get('room_temp',0), "°C", inputs.get('room_temp',0)>24)
    elif "CT" in device_type:
        metric_card(hud1, "الجانتري", inputs.get('gantry_temp',0), "°C", inputs.get('gantry_temp',0)>60)
        metric_card(hud2, "الشرارات", inputs.get('tube_arcing',0), "#", inputs.get('tube_arcing',0)>0)
        metric_card(hud3, "الفولت", inputs.get('voltage',0), "V")
        metric_card(hud4, "المراوح", inputs.get('fan_rpm',0), "RPM")
    else:
        metric_card(hud1, "التيوب", inputs.get('tube_temp',0), "°C", inputs.get('tube_temp',0)>60)
        metric_card(hud2, "الفولت", inputs.get('voltage',0), "V")
        metric_card(hud3, "الغرفة", inputs.get('room_temp',0), "°C")
        metric_card(hud4, "الرطوبة", inputs.get('humidity',0), "%")
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. منطقة التحليل - التخطيط الشبكي
    c_status, c_charts = st.columns([1, 2], gap="medium") # الحالة يمين (1)، الرسوم يسار (2)

    # --- العمود الأيمن (الحالة + العداد) ---
    with c_status:
        # كارت الحالة
        st.markdown(f"""
        <div class="glass-card" style="height: 220px; display:flex; flex-direction:column; justify-content:center;">
            <div class="status-box {css}" style="font-size:1.4em;">{status}</div>
            <div style="color:{text_color}; text-align:center;">
                <b>📋 التشخيص:</b>
                <ul style="margin-top:5px; color:{sub_text}; text-align:right; font-size:0.9em; list-style-position: inside;">
                    {''.join([f'<li>{r}</li>' for r in (reasons if reasons else ["لا توجد أعطال"])])}
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # كارت العداد
        st.markdown('<div class="glass-card" style="height: 220px;">', unsafe_allow_html=True)
        gauge_text_color = "white" if is_dark else "#0f172a"
        fig_gauge = go.Figure(go.Indicator(mode = "gauge+number", value = score, title = {'text': "مؤشر الخطر", 'font': {'color': gauge_text_color, 'size': 14}}, number = {'font': {'color': gauge_text_color, 'size': 30}}, gauge = {'axis': {'range': [None, 100], 'tickcolor': gauge_text_color}, 'bar': {'color': clr}, 'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 0, 'steps': [{'range': [0, 20], 'color': 'rgba(34, 197, 94, 0.3)'}, {'range': [20, 50], 'color': 'rgba(234, 179, 8, 0.3)'}, {'range': [50, 100], 'color': 'rgba(239, 68, 68, 0.3)'}]}))
        fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': gauge_text_color}, height=180, margin=dict(l=10,r=10,t=30,b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- العمود الأيسر (الرسوم البيانية) ---
    with c_charts:
        st.markdown('<div class="glass-card" style="height:460px; display:flex; flex-direction:column; justify-content:center;">', unsafe_allow_html=True)
        
        if sum(factors.values()) > 0:
            st.markdown(f"#### 📊 تحليل الأسباب الجذرية")
            
            fig_bar = px.bar(x=list(factors.keys()), y=list(factors.values()), color=list(factors.values()), color_continuous_scale='Reds', template=chart_template)
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="الخطر", coloraxis_showscale=False, margin=dict(t=10,b=10,l=10,r=10), height=180)
            st.plotly_chart(fig_bar, use_container_width=True)
            
            fig_pie = px.pie(names=list(factors.keys()), values=list(factors.values()), hole=0.6, template=chart_template)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5), margin=dict(t=0,b=20,l=10,r=10), height=160)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            # رسالة الأمان
            st.markdown(f"""
            <div style="text-align:center; opacity:0.7;">
                <h1 style="font-size:6em; margin:0;">🛡️</h1>
                <h2 style="color:{text_color}; margin:0;">النظام آمن</h2>
                <p style="color:{sub_text}; margin-top:10px;">جميع المؤشرات في النطاق الطبيعي</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
