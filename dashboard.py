import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="Medical Command Center", layout="wide", page_icon="🏥")

# --- 2. القيم الافتراضية ---
default_values = {
    "الرنين المغناطيسي (MRI)": { "helium": 85.0, "comp_pressure": 20.0, "chiller_temp": 10.0, "room_temp": 22.0, "cont_hours": 4.0, "coil_snr": 95.0, "humidity": 45.0 },
    "الأشعة المقطعية (CT Scan)": { "gantry_temp": 35.0, "voltage": 220.0, "tube_arcing": 0, "tube_age": 10000.0, "cont_hours": 4.0, "fan_rpm": 3000, "room_temp": 22.0, "humidity": 40.0 },
    "الفلورسكوبي (Fluoro)": { "voltage": 220.0, "tube_temp": 30.0, "error_logs": 0, "cont_hours": 2.0, "tube_age": 5000.0, "humidity": 45.0 },
    "الأشعة السينية (X-Ray)": { "tube_temp": 35.0, "voltage": 70.0, "exposure_errors": 0, "cont_hours": 6.0, "tube_age": 2000.0, "room_temp": 22.0 }
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

# --- 4. CSS ---
if is_dark:
    bg_color = "#0e1117"; card_bg = "#1e2329"; text_color = "#fafafa"; border_color = "#2d333b"; chart_theme = "plotly_dark"
    limit_bg = "#0f3443"; limit_text = "#00bcd4"; limit_border = "#005662"
    input_bg = "#0e1117"
else:
    bg_color = "#f8fafc"; card_bg = "#ffffff"; text_color = "#0f172a"; border_color = "#e2e8f0"; chart_theme = "plotly_white"
    limit_bg = "#e0f2fe"; limit_text = "#0284c7"; limit_border = "#bae6fd"
    input_bg = "#ffffff"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');
html, body, [class*="css"] {{ font-family: 'Tajawal', sans-serif; direction: rtl; }}
.stApp {{ background-color: {bg_color}; color: {text_color}; }}

div[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px;
}}

.limit-badge {{
    background: {limit_bg}; color: {limit_text};
    font-size: 0.75rem; padding: 2px 8px; border-radius: 4px;
    border: 1px solid {limit_border}; float: left; margin-top: 2px;
}}
.input-label {{ font-size:0.9em; font-weight:bold; opacity: 0.9; }}

.stNumberInput input {{ background-color: {input_bg}; color: {text_color}; }}
h1, h2, h3, h4 {{ color: {text_color}; font-weight: 700; }}
.highlight {{ color: #00bcd4; }}

.status-box {{ padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 10px; }}
.crit {{ background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #ef4444; }}
.warn {{ background: rgba(234, 179, 8, 0.1); border: 1px solid #eab308; color: #eab308; }}
.safe {{ background: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; color: #22c55e; }}
</style>
""", unsafe_allow_html=True)

# --- دالة الإدخال الذكية ---
def smart_input(col, label, key, min_v, max_v, step, limit_text, icon="🔹"):
    if key not in st.session_state: st.session_state[key] = default_values[device_type].get(key, min_v)
    col.markdown(f"""
    <div style="margin-bottom:5px; display:flex; justify-content:space-between;">
        <span class="input-label">{icon} {label}</span>
        <span class="limit-badge">{limit_text}</span>
    </div>""", unsafe_allow_html=True)
    return col.number_input("hidden", min_value=min_v, max_value=max_v, step=step, key=key, label_visibility="collapsed")

# --- 5. الهيكل الرئيسي ---
st.markdown(f"""<h2>🏥 مركز القيادة: <span class='highlight'>{device_type}</span></h2>""", unsafe_allow_html=True)

col_inputs, col_dashboard = st.columns([1, 2.5], gap="large")

# === القسم الأيمن: المدخلات ===
with col_inputs:
    with st.container(border=True):
        st.markdown("#### ⚙️ لوحة التشغيل")
        tab1, tab2 = st.tabs(["المؤشرات الحيوية", "البيئة والتشغيل"])
        
        inputs = {}
        with tab1:
            st.write("")
            if device_type == "الرنين المغناطيسي (MRI)":
                inputs['helium'] = smart_input(st, "مستوى الهيليوم", "helium", 0.0, 100.0, 0.5, "خطر < 60%", "🎈")
                inputs['comp_pressure'] = smart_input(st, "ضغط الكمبروسر", "comp_pressure", 0.0, 30.0, 0.5, "18-22 PSI", "⚙️")
                inputs['chiller_temp'] = smart_input(st, "حرارة الشيلر", "chiller_temp", 0.0, 50.0, 0.5, "خطر > 20°C", "❄️")
                inputs['coil_snr'] = smart_input(st, "جودة الإشارة", "coil_snr", 0.0, 100.0, 1.0, "خطر < 80%", "📡")
            elif device_type == "الأشعة المقطعية (CT Scan)":
                inputs['gantry_temp'] = smart_input(st, "حرارة الجانتري", "gantry_temp", 10.0, 120.0, 0.5, "خطر > 60°C", "☢️")
                inputs['voltage'] = smart_input(st, "الجهد (V)", "voltage", 0.0, 300.0, 1.0, "220 ± 10%", "⚡")
                inputs['tube_arcing'] = smart_input(st, "الشرارات", "tube_arcing", 0, 50, 1, "يجب أن يكون 0", "💥")
                inputs['fan_rpm'] = smart_input(st, "المراوح", "fan_rpm", 0, 5000, 100, "خطر < 2000", "🌀")
            elif device_type == "الفلورسكوبي (Fluoro)":
                inputs['voltage'] = smart_input(st, "الجهد (V)", "voltage", 0.0, 300.0, 1.0, "220 ± 10%", "⚡")
                inputs['tube_temp'] = smart_input(st, "حرارة التيوب", "tube_temp", 10.0, 100.0, 0.5, "خطر > 70°C", "🔥")
                inputs['error_logs'] = smart_input(st, "سجل الأخطاء", "error_logs", 0, 50, 1, "يجب أن يكون 0", "⚠️")
                inputs['cont_hours'] = st.session_state.get('cont_hours', 2.0)
                inputs['room_temp'] = st.session_state.get('room_temp', 22.0)
            elif device_type == "الأشعة السينية (X-Ray)":
                inputs['tube_temp'] = smart_input(st, "حرارة التيوب", "tube_temp", 10.0, 120.0, 0.5, "خطر > 60°C", "🔥")
                inputs['voltage'] = smart_input(st, "الجهد (kV)", "voltage", 0.0, 200.0, 1.0, "70 ± 10%", "⚡")
                inputs['exposure_errors'] = smart_input(st, "فشل التصوير", "exposure_errors", 0, 20, 1, "0 خطأ", "🚫")
                inputs['cont_hours'] = st.session_state.get('cont_hours', 6.0)
                inputs['room_temp'] = st.session_state.get('room_temp', 22.0)
        with tab2:
            st.write("")
            inputs['room_temp'] = smart_input(st, "حرارة الغرفة", "room_temp", 10.0, 45.0, 0.5, "المثالي < 24°C", "🌡️")
            inputs['humidity'] = smart_input(st, "الرطوبة %", "humidity", 0.0, 100.0, 1.0, "30-70%", "💧")
            inputs['cont_hours'] = smart_input(st, "ساعات التشغيل", "cont_hours", 0.0, 24.0, 0.5, "يعتمد على العمر", "⏱️")
            limit_txt = "Max 200k" if "CT" in device_type else "Max 50k"
            inputs['tube_age'] = smart_input(st, "عمر التيوب", "tube_age", 0.0, 500000.0, 1000.0, limit_txt, "⏳")

# === منطق التحليل الذكي (تم التعديل: ربط العمر بساعات التشغيل) ===
def analyze(dev, data):
    score = 0
    factors = {}
    reasons = []
    actions = []

    # 1. معادلة الشيخوخة الديناميكية (Dynamic Aging Formula)
    # كلما زاد عمر التيوب، قلت ساعات التشغيل المسموحة
    
    current_hours = data.get('cont_hours', 0)
    current_age = data.get('tube_age', 0)
    
    # حدد الحد الأقصى للعمر بناء على الجهاز
    max_life = 200000 if "CT" in dev else 50000 
    
    # حساب "ساعات العمل الآمنة" (Safe Hours Limit)
    # المعادلة: التيوب الجديد (0) يتحمل 14 ساعة. التيوب المتهالك (Max) يتحمل 4 ساعات فقط.
    age_factor = min(current_age / max_life, 1.0) # نسبة الاستهلاك من 0 إلى 1
    safe_hours_limit = 14 - (10 * age_factor) # يبدأ من 14 وينخفض تدريجياً إلى 4
    
    # تطبيق التحقق
    if current_hours > safe_hours_limit:
        score += 20
        reasons.append(f"إجهاد تشغيل ({current_hours}h) لتيوب حالته {(1-age_factor)*100:.0f}%")
        factors['Work Stress'] = 20
        actions.append(f"يجب إيقاف الجهاز. الحد الآمن لهذا التيوب حالياً هو {safe_hours_limit:.1f} ساعة")

    # 2. الفحوصات العامة
    if data.get('room_temp',22) > 24: 
        score+=15; reasons.append("حرارة الغرفة مرتفعة"); factors['Room']=15
        actions.append("فحص التكييف")
    if data.get('humidity',45) > 70: 
        score+=20; reasons.append("رطوبة عالية"); factors['Hum']=20
        actions.append("مزيلات رطوبة")

    # 3. الفحوصات الخاصة
    if dev == "الرنين المغناطيسي (MRI)":
        # الرنين ليس له تيوب بنفس المعنى، لذا نعتمد على الهيليوم والضغط
        if data.get('helium', 85)<40: score+=50; reasons.append("خطر Quench"); factors['He']=50; actions.append("تعبئة طارئة")
        elif data.get('helium', 85)<60: score+=20; reasons.append("نقص هيليوم"); factors['He']=20
        if data.get('comp_pressure',20)<15 or data.get('comp_pressure',20)>25: score+=40; reasons.append("ضغط كمبروسر"); factors['Comp']=40; actions.append("فحص Cold Head")
        if data.get('chiller_temp',10)>20: score+=30; reasons.append("فشل شيلر"); factors['Cool']=30

    elif dev == "الأشعة المقطعية (CT Scan)":
        if data.get('tube_arcing',0)>0: score+=40; reasons.append("Arcing"); factors['Arc']=40; actions.append("Tube Conditioning")
        if data.get('gantry_temp',35)>85: score+=50; reasons.append("حرارة جانتري"); factors['Temp']=50; actions.append("إيقاف فوري")
        if abs(data.get('voltage',220)-220)>20: score+=30; reasons.append("كهرباء"); factors['Elec']=30

    elif dev == "الفلورسكوبي (Fluoro)": 
        if data.get('voltage',220)<190: score+=30; reasons.append("جهد منخفض"); factors['Elec']=30
        if data.get('error_logs',0)>10: score+=35; reasons.append("أخطاء نظام"); factors['Soft']=35

    elif dev == "الأشعة السينية (X-Ray)":
        if data.get('exposure_errors',0)>3: score+=45; reasons.append("فشل تصوير"); factors['Gen']=45

    score = min(score, 100)
    if score >= 50: return score, "DANGER / خطر", "crit", reasons, actions, factors, "#ef4444"
    elif score >= 20: return score, "WARNING / تحذير", "warn", reasons, actions, factors, "#eab308"
    return score, "SAFE / آمن", "safe", reasons, actions, factors, "#22c55e"

score, status, css, reasons, actions, factors, clr = analyze(device_type, inputs)

# === القسم الأيسر: الداشبورد ===
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
    grid_c1, grid_c2 = st.columns([2, 1])

    with grid_c1:
        with st.container(border=True): 
            if sum(factors.values()) > 0:
                st.markdown("#### 📊 تحليل الأسباب الجذرية")
                fig_bar = px.bar(x=list(factors.keys()), y=list(factors.values()), color=list(factors.values()), color_continuous_scale='Reds', template=chart_theme)
                fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="", yaxis_title="الخطر", coloraxis_showscale=False, margin=dict(t=10,b=10,l=10,r=10), height=200)
                st.plotly_chart(fig_bar, use_container_width=True)
                
                fig_pie = px.pie(names=list(factors.keys()), values=list(factors.values()), hole=0.6, template=chart_theme)
                fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5), margin=dict(t=0,b=20,l=10,r=10), height=180)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style="text-align:center; opacity:0.7;">
                    <img src="https://cdn-icons-png.flaticon.com/512/1161/1161388.png" width="100" style="filter: grayscale(100%); margin-bottom:15px;">
                    <h3 style="margin:0; color:{text_color}">النظام مستقر</h3>
                    <p style="color:#888">جميع المؤشرات في النطاق الآمن</p>
                </div>
                <br><br>
                """, unsafe_allow_html=True)

    with grid_c2:
        with st.container(border=True):
            st.markdown(f"""<div class="status-box {css}" style="font-size:1.4em;">{status}</div>""", unsafe_allow_html=True)
            
            st.markdown(f"**📋 التشخيص:**")
            if reasons:
                for r in reasons: st.markdown(f"- 🔴 {r}")
            else: st.markdown("- لا توجد أعطال")
            
            st.markdown("---")
            st.markdown(f"**🛠️ التوصيات:**")
            if actions:
                for a in actions: st.markdown(f"- ✅ {a}")
            else:
                st.markdown("- المتابعة الروتينية")
            
        with st.container(border=True):
            gauge_text_color = "white" if is_dark else "#0f172a"
            fig_gauge = go.Figure(go.Indicator(mode = "gauge+number", value = score, title = {'text': "مؤشر الخطر", 'font': {'color': gauge_text_color, 'size': 14}}, number = {'font': {'color': gauge_text_color, 'size': 30}}, gauge = {'axis': {'range': [None, 100], 'tickcolor': gauge_text_color}, 'bar': {'color': clr}, 'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 0, 'steps': [{'range': [0, 20], 'color': 'rgba(34, 197, 94, 0.3)'}, {'range': [20, 50], 'color': 'rgba(234, 179, 8, 0.3)'}, {'range': [50, 100], 'color': 'rgba(239, 68, 68, 0.3)'}]}))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': gauge_text_color}, height=160, margin=dict(l=10,r=10,t=30,b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)
