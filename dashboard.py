import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# --- 1. إعداد الصفحة (Wide Mode) ---
st.set_page_config(page_title="Medical Twin Simulator", layout="wide", page_icon="🏥")

# --- 2. إدارة القيم الافتراضية ---
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

# --- 3. CSS الاحترافي (Advanced Styling) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; }

/* الخلفية العامة */
.stApp { background-color: #f8fafc; }

/* كارت التحكم الجانبي */
.control-card {
    background: white; padding: 20px; border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
}

/* كارت النتائج الكبير */
.monitor-card {
    background: white; padding: 25px; border-radius: 15px; height: 100%;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
}

/* العناوين */
h1, h2, h3 { color: #0f172a; font-weight: 700; }
.sub-header { color: #64748b; font-size: 0.9em; margin-bottom: 15px; }

/* شارات الحدود (Limit Badges) */
.badge {
    font-size: 0.75em; padding: 2px 8px; border-radius: 6px;
    background: #e0f2fe; color: #0284c7; font-weight: 600;
    float: left; margin-top: 2px;
}
.label-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
.label-text { font-weight: 600; color: #334155; font-size: 0.95em; }

/* ألوان الحالة */
.status-safe { background: #dcfce7; color: #166534; border-right: 6px solid #22c55e; padding: 15px; border-radius: 8px; }
.status-warn { background: #fef9c3; color: #854d0e; border-right: 6px solid #eab308; padding: 15px; border-radius: 8px; }
.status-crit { background: #fee2e2; color: #991b1b; border-right: 6px solid #ef4444; padding: 15px; border-radius: 8px; }

/* زر الريسيت */
div.stButton > button {
    width: 100%; background-color: #f1f5f9; color: #475569; border: none; font-weight: bold;
}
div.stButton > button:hover { background-color: #e2e8f0; color: #1e293b; }

</style>
""", unsafe_allow_html=True)

# --- 4. دالة الإدخال الذكية ---
def smart_input(col, label, key, min_v, max_v, step, limit_text, help_txt=""):
    col.markdown(f"""
    <div class="label-row">
        <span class="label-text">{label}</span>
        <span class="badge">{limit_text}</span>
    </div>
    """, unsafe_allow_html=True)
    return col.number_input("hidden", min_value=min_v, max_value=max_v, step=step, key=key, label_visibility="collapsed", help=help_txt)

# --- 5. الهيدر العلوي ---
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown("## 🏥 نظام التوأم الرقمي (Digital Twin Simulator)")
    st.markdown("<div class='sub-header'>منصة محاكاة الأعطال والتحليل التنبؤي للأجهزة الطبية</div>", unsafe_allow_html=True)
with c2:
    if st.button("🔄 استعادة القيم الافتراضية"):
        update_state(st.session_state.device_selector)
        st.rerun()

st.markdown("---")

# --- 6. التخطيط الرئيسي (Split Layout) ---
# تقسيم الشاشة: عمود ضيق للتحكم (يمين) وعمود عريض للمراقبة (يسار)
col_control, col_monitor = st.columns([1, 2.2])

if "helium" not in st.session_state and st.session_state.device_type == "الرنين المغناطيسي (MRI)": update_state(st.session_state.device_type)

# ==========================================
# 🎛️ العمود الأيمن: لوحة التحكم (Controls)
# ==========================================
with col_control:
    st.markdown('<div class="control-card">', unsafe_allow_html=True)
    
    # اختيار الجهاز
    st.markdown("#### ⚙️ إعدادات المحاكاة")
    device_type = st.selectbox("اختر الجهاز:", list(default_values.keys()), key="device_selector", on_change=on_device_change)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # تبويبات للمدخلات لتقليل الزحام
    tab_vital, tab_ops = st.tabs(["📊 القراءات الحيوية", "⚙️ التشغيل والبيئة"])
    
    inputs = {}
    
    with tab_vital:
        st.markdown("<br>", unsafe_allow_html=True)
        if device_type == "الرنين المغناطيسي (MRI)":
            inputs['helium'] = smart_input(st, "🎈 مستوى الهيليوم", "helium", 0.0, 100.0, 0.5, "خطر < 60%")
            inputs['comp_pressure'] = smart_input(st, "⚙️ ضغط الكمبروسر", "comp_pressure", 0.0, 30.0, 0.5, "18-22 PSI")
            inputs['chiller_temp'] = smart_input(st, "❄️ حرارة الشيلر", "chiller_temp", 0.0, 50.0, 0.5, "> 20°C خطر")
            inputs['coil_snr'] = smart_input(st, "📡 جودة الإشارة (SNR)", "coil_snr", 0.0, 100.0, 1.0, "< 80% سيء")
            
        elif device_type == "الأشعة المقطعية (CT Scan)":
            inputs['gantry_temp'] = smart_input(st, "☢️ حرارة الجانتري", "gantry_temp", 10.0, 120.0, 0.5, "> 60°C خطر")
            inputs['voltage'] = smart_input(st, "⚡ الجهد (Volt)", "voltage", 0.0, 300.0, 1.0, "220V ±10%")
            inputs['tube_arcing'] = smart_input(st, "💥 عدد الشرارات (Arc)", "tube_arcing", 0, 50, 1, "يجب أن يكون 0")
            inputs['fan_rpm'] = smart_input(st, "🌀 سرعة المراوح", "fan_rpm", 0, 5000, 100, "< 2000 خطر")

        elif device_type == "الفلورسكوبي (Fluoro)":
            inputs['voltage'] = smart_input(st, "⚡ الجهد (Volt)", "voltage", 0.0, 300.0, 1.0, "220V ±10%")
            inputs['tube_temp'] = smart_input(st, "🔥 حرارة التيوب", "tube_temp", 10.0, 100.0, 0.5, "> 70°C خطر")
            inputs['error_logs'] = smart_input(st, "⚠️ سجل الأخطاء", "error_logs", 0, 50, 1, "يجب أن يكون 0")

        elif device_type == "الأشعة السينية (X-Ray)":
            inputs['tube_temp'] = smart_input(st, "🔥 حرارة التيوب", "tube_temp", 10.0, 120.0, 0.5, "> 60°C خطر")
            inputs['voltage'] = smart_input(st, "⚡ جهد عالي (kV)", "voltage", 0.0, 200.0, 1.0, "70kV ±10%")
            inputs['exposure_errors'] = smart_input(st, "🚫 فشل التصوير", "exposure_errors", 0, 20, 1, "يجب أن يكون 0")

    with tab_ops:
        st.markdown("<br>", unsafe_allow_html=True)
        # مدخلات مشتركة ومحددة
        inputs['room_temp'] = smart_input(st, "🌡️ حرارة الغرفة", "room_temp", 10.0, 45.0, 0.5, "> 24°C خطر")
        inputs['humidity'] = smart_input(st, "💧 الرطوبة (%)", "humidity", 0.0, 100.0, 1.0, "> 70% خطر")
        inputs['cont_hours'] = smart_input(st, "⏱️ ساعات تشغيل متواصل", "cont_hours", 0.0, 24.0, 0.5, "> 10h إجهاد")
        
        # العمر الافتراضي
        limit_age = "200k" if "CT" in device_type else "20k"
        inputs['tube_age'] = smart_input(st, "⏳ عمر التيوب/الجهاز", "tube_age", 0.0, 500000.0, 1000.0, f"Max: {limit_age}")

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🖥️ العمود الأيسر: شاشة المراقبة (Monitor)
# ==========================================

# --- المنطق التحليلي (نفس المنطق القوي السابق) ---
def analyze_simulation(dev, data):
    risk_score = 0; factors = {}; reasons = []; actions = []

    # 1. العوامل المشتركة
    if data.get('room_temp', 22) > 24: risk_score += 15; reasons.append(f"حرارة غرفة عالية ({data.get('room_temp')}°C)"); actions.append("فحص التكييف"); factors['Room']=15
    if data.get('humidity', 45) > 70: risk_score += 20; reasons.append("رطوبة عالية (خطر كهربائي)"); factors['Hum']=20
    if data.get('cont_hours', 0) > 10: risk_score += 15; reasons.append("تشغيل متواصل مفرط"); factors['Overwork']=15

    # 2. العوامل الخاصة
    if dev == "الرنين المغناطيسي (MRI)":
        p = data.get('comp_pressure', 20)
        if p < 15 or p > 25: risk_score+=40; reasons.append(f"ضغط كمبروسر ({p})"); actions.append("صيانة Cold Head"); factors['Comp']=40
        if data.get('coil_snr', 100) < 80: risk_score+=25; reasons.append("Low SNR"); factors['Img']=25
        if data['helium'] < 40: risk_score+=50; reasons.append("خطر Quench"); factors['He']=50
        elif data['helium'] < 60: risk_score+=20; reasons.append("نقص هيليوم"); factors['He']=20
        if data['chiller_temp'] > 20: risk_score+=30; reasons.append("فشل شيلر"); factors['Cool']=30

    elif dev == "الأشعة المقطعية (CT Scan)":
        a = data.get('tube_arcing', 0)
        if a > 0: risk_score+=30 + (a*10); reasons.append(f"شرارة ({a})"); actions.append("فحص التيوب"); factors['Arc']=40
        if data.get('fan_rpm', 3000) < 2000: risk_score+=20; reasons.append("ضعف مراوح"); factors['Fan']=20
        if data['gantry_temp'] > 85: risk_score+=50; reasons.append("حرارة جانتري"); factors['Temp']=50
        if abs(data['voltage']-220)>20: risk_score+=30; reasons.append("تذبذب كهرباء"); factors['Elec']=30
        if data['tube_age'] > 200000: risk_score+=15; reasons.append("تيوب قديم"); factors['Age']=15

    elif dev == "الفلورسكوبي (Fluoro)":
        l = data.get('error_logs', 0)
        if l > 10: risk_score+=35; reasons.append("أخطاء نظام"); factors['Soft']=35
        if data['voltage'] < 190: risk_score+=30; reasons.append("ضعف جهد"); factors['Elec']=30
        if data['tube_temp'] > 70: risk_score+=30; reasons.append("حرارة عالية"); factors['Temp']=30

    elif dev == "الأشعة السينية (X-Ray)":
        e = data.get('exposure_errors', 0)
        if e > 3: risk_score+=45; reasons.append("فشل تصوير"); factors['Gen']=45
        if data['tube_temp'] > 60: risk_score+=45; reasons.append("حرارة أنبوب"); factors['Temp']=45

    risk_score = min(risk_score, 100)
    if risk_score >= 50: status="CRITICAL - خطر مرتفع"; css="status-crit"; clr="#ef4444"
    elif risk_score >= 20: status="WARNING - تحذير"; css="status-warn"; clr="#eab308"
    else: status="NORMAL - آمن"; css="status-safe"; clr="#22c55e"; reasons.append("جميع المؤشرات طبيعية"); actions.append("متابعة روتينية")
    
    return risk_score, status, css, reasons, actions, factors, clr

score, status, css, reasons, actions, factors, clr = analyze_simulation(device_type, inputs)

with col_monitor:
    st.markdown('<div class="monitor-card">', unsafe_allow_html=True)
    
    # الجزء العلوي: الحالة والعداد
    m1, m2 = st.columns([1.5, 1])
    with m1:
        st.markdown(f"""
        <div class="{css}">
            <h2 style="margin:0; color:inherit;">{status}</h2>
            <div style="margin-top:10px; font-size:0.95em;">
                <b>الأسباب الجذرية المكتشفة:</b><br>
                {' • '.join(reasons)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if actions[0] != "متابعة روتينية":
            st.markdown(f"""
            <div style="margin-top:15px; padding:10px; background:#f1f5f9; border-radius:8px; border-right:4px solid #475569;">
                <b>🛠️ الإجراء التصحيحي الموصى به:</b><br>
                {' • '.join(actions)}
            </div>
            """, unsafe_allow_html=True)

    with m2:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = score,
            title = {'text': "مؤشر صحة الجهاز"},
            gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': clr},
                     'steps': [{'range': [0, 20], 'color': '#dcfce7'}, {'range': [20, 50], 'color': '#fef9c3'}, {'range': [50, 100], 'color': '#fee2e2'}]}))
        fig_gauge.update_layout(height=220, margin=dict(l=10,r=10,t=30,b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")
    
    # الجزء السفلي: الرسوم البيانية للتحليل
    if sum(factors.values()) > 0:
        st.markdown("#### 📊 تحليل العوامل المؤثرة (Root Cause Analysis)")
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            fig_pie = px.pie(names=list(factors.keys()), values=list(factors.values()), hole=0.6, title="توزيع مصادر الخطر")
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        with c_chart2:
             fig_bar = px.bar(x=list(factors.keys()), y=list(factors.values()), title="شدة التأثير (بالنقاط)", 
                              labels={'x':'العامل','y':'النقاط'}, color=list(factors.values()), color_continuous_scale='Reds')
             st.plotly_chart(fig_bar, use_container_width=True)
    else:
        # رسم توضيحي عندما يكون الوضع آمناً
        st.info("✅ الجهاز يعمل بكفاءة تامة (Optimal Performance).")
        # يمكن إضافة رسم خطي وهمي للأداء هنا كنوع من الديكور
        
    st.markdown('</div>', unsafe_allow_html=True)
