import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="Medical Command Center", layout="wide", page_icon="🏥")

# --- 2. القيم الافتراضية ---
default_values = {
    "الرنين المغناطيسي (MRI)": { "helium": 85.0, "comp_pressure": 20.0, "chiller_temp": 10.0, "room_temp": 22.0, "cont_hours": 4.0, "coil_snr": 95.0, "humidity": 45.0 },
    "الأشعة المقطعية (CT Scan)": { "gantry_temp": 35.0, "voltage": 220.0, "tube_arcing": 0, "tube_age": 50000.0, "cont_hours": 4.0, "fan_rpm": 3000, "room_temp": 22.0, "humidity": 40.0 },
    "الفلورسكوبي (Fluoro)": { "voltage": 220.0, "tube_temp": 30.0, "error_logs": 0, "cont_hours": 2.0, "tube_age": 10000.0, "humidity": 45.0 },
    "الأشعة السينية (X-Ray)": { "tube_temp": 35.0, "voltage": 70.0, "exposure_errors": 0, "cont_hours": 6.0, "tube_age": 15000.0, "room_temp": 22.0 }
}

if 'device_type' not in st.session_state: st.session_state['device_type'] = "الرنين المغناطيسي (MRI)"

def update_state():
    selected = st.session_state.get("device_selector", "الرنين المغناطيسي (MRI)")
    st.session_state['device_type'] = selected
    for key, val in default_values[selected].items():
        if key not in st.session_state: st.session_state[key] = val

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

# --- 4. CSS (السحر هنا) ---
# سنقوم بتغيير ستايل الحاويات الأصلية لتبدو مثل الكروت
if is_dark:
    bg_color = "#0e1117"
    card_bg = "#1e2329" # لون الكارت الغامق
    text_color = "#fafafa"
    border_color = "#2d333b"
    chart_theme = "plotly_dark"
else:
    bg_color = "#f8fafc"
    card_bg = "#ffffff"
    text_color = "#0f172a"
    border_color = "#e2e8f0"
    chart_theme = "plotly_white"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');
html, body, [class*="css"] {{ font-family: 'Tajawal', sans-serif; direction: rtl; }}
.stApp {{ background-color: {bg_color}; color: {text_color}; }}

/* تحويل الحاويات (Containers) إلى كروت زجاجية */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: {card_bg};
    border: 1px solid {border_color};
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    padding: 20px;
    margin-bottom: 20px;
}}

/* تنسيق النصوص */
h1, h2, h3, h4 {{ color: {text_color}; font-weight: 700; }}
.highlight {{ color: #00bcd4; }}

/* صناديق الحالة الملونة */
.status-box {{ padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 10px; }}
.crit {{ background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #ef4444; }}
.warn {{ background: rgba(234, 179, 8, 0.1); border: 1px solid #eab308; color: #eab308; }}
.safe {{ background: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; color: #22c55e; }}

</style>
""", unsafe_allow_html=True)

# دالة للإدخال
def smart_input(col, label, key, min_v, max_v, step):
    if key not in st.session_state: st.session_state[key] = default_values[device_type].get(key, min_v)
    return col.number_input(label, min_value=min_v, max_value=max_v, step=step, key=key)

# --- 5. الهيكل الرئيسي ---
st.markdown(f"""<h2>🏥 مركز القيادة: <span class='highlight'>{device_type}</span></h2>""", unsafe_allow_html=True)

col_inputs, col_dashboard = st.columns([1, 2.5], gap="large")

# === القسم الأيمن: المدخلات (داخل كارت) ===
with col_inputs:
    with st.container(border=True): # هذا سيتحول لكارت تلقائياً بفضل الـ CSS
        st.markdown("#### ⚙️ لوحة التشغيل")
        tab1, tab2 = st.tabs(["المؤشرات الحيوية", "البيئة والتشغيل"])
        inputs = {}
        with tab1:
            st.write("")
            if device_type == "الرنين المغناطيسي (MRI)":
                inputs['helium'] = smart_input(st, "🎈 مستوى الهيليوم %", "helium", 0.0, 100.0, 0.5)
                inputs['comp_pressure'] = smart_input(st, "⚙️ ضغط الكمبروسر", "comp_pressure", 0.0, 30.0, 0.5)
                inputs['chiller_temp'] = smart_input(st, "❄️ حرارة الشيلر", "chiller_temp", 0.0, 50.0, 0.5)
                inputs['coil_snr'] = smart_input(st, "📡 جودة الإشارة SNR", "coil_snr", 0.0, 100.0, 1.0)
            elif device_type == "الأشعة المقطعية (CT Scan)":
                inputs['gantry_temp'] = smart_input(st, "☢️ حرارة الجانتري", "gantry_temp", 10.0, 120.0, 0.5)
                inputs['voltage'] = smart_input(st, "⚡ الجهد (V)", "voltage", 0.0, 300.0, 1.0)
                inputs['tube_arcing'] = smart_input(st, "💥 عدد الشرارات", "tube_arcing", 0, 50, 1)
                inputs['fan_rpm'] = smart_input(st, "🌀 سرعة المراوح", "fan_rpm", 0, 5000, 100)
            elif device_type == "الفلورسكوبي (Fluoro)":
                inputs['voltage'] = smart_input(st, "⚡ الجهد (V)", "voltage", 0.0, 300.0, 1.0)
                inputs['tube_temp'] = smart_input(st, "🔥 حرارة التيوب", "tube_temp", 10.0, 100.0, 0.5)
                inputs['error_logs'] = smart_input(st, "⚠️ سجل الأخطاء", "error_logs", 0, 50, 1)
                inputs['cont_hours'] = st.session_state.get('cont_hours', 2.0)
                inputs['room_temp'] = st.session_state.get('room_temp', 22.0)
            elif device_type == "الأشعة السينية (X-Ray)":
                inputs['tube_temp'] = smart_input(st, "🔥 حرارة التيوب", "tube_temp", 10.0, 120.0, 0.5)
                inputs['voltage'] = smart_input(st, "⚡ جهد عالي (kV)", "voltage", 0.0, 200.0, 1.0)
                inputs['exposure_errors'] = smart_input(st, "🚫 فشل التصوير", "exposure_errors", 0, 20, 1)
                inputs['cont_hours'] = st.session_state.get('cont_hours', 6.0)
                inputs['room_temp'] = st.session_state.get('room_temp', 22.0)
        with tab2:
            st.write("")
            inputs['room_temp'] = smart_input(st, "🌡️ حرارة الغرفة", "room_temp", 10.0, 45.0, 0.5)
            inputs['humidity'] = smart_input(st, "💧 الرطوبة %", "humidity", 0.0, 100.0, 1.0)
            inputs['cont_hours'] = smart_input(st, "⏱️ ساعات التشغيل", "cont_hours", 0.0, 24.0, 0.5)
            limit_txt = "200k" if "CT" in device_type else "20k"
            inputs['tube_age'] = smart_input(st, "⏳ عمر التيوب", "tube_age", 0.0, 500000.0, 1000.0)

# === منطق التحليل ===
def analyze(dev, data):
    score = 0; factors = {}; reasons = []
    
    # Global Checks
    if data.get('room_temp',22) > 24: score+=15; reasons.append("حرارة الغرفة"); factors['Room']=15
    if data.get('humidity',45) > 70: score+=20; reasons.append("رطوبة عالية"); factors['Hum']=20
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

# === القسم الأيسر: الداشبورد (داخل كروت) ===
with col_dashboard:
    
    # 1. شريط الحالة العلوية (HUD)
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        def hud_metric(col, label, val, suffix, is_alert=False):
            color = "#ef4444" if is_alert else text_color
            col.markdown(f"<div style='text-align:center'><span style='color:#888; font-size:0.8em'>{label}</span><br><span style='color:{color}; font-size:1.4em; font-weight:bold'>{val}</span> <span style='font-size:0.8em'>{suffix}</span></div>", unsafe_allow_html=True)
            
        if device_type == "الرنين المغناطيسي (MRI)":
            hud_metric(c1, "الهيليوم", inputs.get('helium',0), "%", inputs.get('helium',0)<60)
            hud_metric(c2, "الشيلر", inputs.get('chiller_temp',0), "°C", inputs.get('chiller_temp',0)>20)
            hud_metric(c3, "الضغط", inputs.get('comp_pressure',0), "PSI")
            hud_metric(c4, "الغرفة", inputs.get('room_temp',0), "°C", inputs.get('room_temp',0)>24)
        elif "CT" in device_type:
            hud_metric(c1, "الجانتري", inputs.get('gantry_temp',0), "°C", inputs.get('gantry_temp',0)>60)
            hud_metric(c2, "الشرارات", inputs.get('tube_arcing',0), "#", inputs.get('tube_arcing',0)>0)
            hud_metric(c3, "الفولت", inputs.get('voltage',0), "V")
            hud_metric(c4, "المراوح", inputs.get('fan_rpm',0), "RPM")
        else:
            hud_metric(c1, "التيوب", inputs.get('tube_temp',0), "°C", inputs.get('tube_temp',0)>60)
            hud_metric(c2, "الفولت", inputs.get('voltage',0), "V")
            hud_metric(c3, "الغرفة", inputs.get('room_temp',0), "°C")
            hud_metric(c4, "الرطوبة", inputs.get('humidity',0), "%")

    # 2. منطقة الرسم البياني والتشخيص
    # هذا هو الجزء الأهم: استخدام الحاويات الأصلية لضمان أن الرسم داخل المربع
    
    grid_c1, grid_c2 = st.columns([2, 1])

    # === المربع الكبير (يسار): الرسوم البيانية ===
    with grid_c1:
        with st.container(border=True): # المربع الكبير
            if sum(factors.values()) > 0:
                st.markdown("#### 📊 تحليل الأسباب الجذرية")
                
                # Bar Chart
                fig_bar = px.bar(x=list(factors.keys()), y=list(factors.values()), color=list(factors.values()), color_continuous_scale='Reds', template=chart_theme)
                fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="الخطر", coloraxis_showscale=False, margin=dict(t=10,b=10,l=10,r=10), height=200)
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Pie Chart
                fig_pie = px.pie(names=list(factors.keys()), values=list(factors.values()), hole=0.6, template=chart_theme)
                fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5), margin=dict(t=0,b=20,l=10,r=10), height=180)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                # محتوى بديل عند الأمان لملء الفراغ
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style="text-align:center; opacity:0.7;">
                    <img src="https://cdn-icons-png.flaticon.com/512/1161/1161388.png" width="100" style="filter: grayscale(100%); margin-bottom:15px;">
                    <h3 style="margin:0; color:{text_color}">النظام مستقر</h3>
                    <p style="color:#888">جميع المؤشرات في النطاق الآمن</p>
                </div>
                <br><br>
                """, unsafe_allow_html=True)

    # === المربع الجانبي (يمين): الحالة والعداد ===
    with grid_c2:
        # المربع العلوي: الحالة
        with st.container(border=True):
            st.markdown(f"""<div class="status-box {css}" style="font-size:1.4em;">{status}</div>""", unsafe_allow_html=True)
            st.markdown(f"**📋 التشخيص:**")
            if reasons:
                for r in reasons:
                    st.markdown(f"- {r}")
            else:
                st.markdown("- لا توجد أعطال")
            st.markdown("<br>", unsafe_allow_html=True)
            
        # المربع السفلي: العداد
        with st.container(border=True):
            gauge_text_color = "white" if is_dark else "#0f172a"
            fig_gauge = go.Figure(go.Indicator(mode = "gauge+number", value = score, title = {'text': "مؤشر الخطر", 'font': {'color': gauge_text_color, 'size': 14}}, number = {'font': {'color': gauge_text_color, 'size': 30}}, gauge = {'axis': {'range': [None, 100], 'tickcolor': gauge_text_color}, 'bar': {'color': clr}, 'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 0, 'steps': [{'range': [0, 20], 'color': 'rgba(34, 197, 94, 0.3)'}, {'range': [20, 50], 'color': 'rgba(234, 179, 8, 0.3)'}, {'range': [50, 100], 'color': 'rgba(239, 68, 68, 0.3)'}]}))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': gauge_text_color}, height=160, margin=dict(l=10,r=10,t=30,b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)
