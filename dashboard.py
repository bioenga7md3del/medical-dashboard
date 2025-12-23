import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="المحاكي الذكي للأعطال", layout="wide", page_icon="🎛️")

# --- 2. تعريف القيم الافتراضية (الطبيعية) لكل جهاز ---
# هذا القاموس يستخدم لزر الريسيت
default_values = {
    "الرنين المغناطيسي (MRI)": {
        "helium": 85.0, "chiller_temp": 10.0, "room_temp": 22.0, "humidity": 45.0,
        "cont_hours": 4.0, "total_usage": 20000.0, "total_cases": 15
    },
    "الأشعة المقطعية (CT Scan)": {
        "gantry_temp": 35.0, "voltage": 220.0, "current": 10.0, "room_temp": 22.0,
        "cont_hours": 6.0, "humidity": 40.0, "total_usage": 30000.0
    },
    "الفلورسكوبي (Fluoro)": {
        "voltage": 220.0, "humidity": 45.0, "tube_temp": 30.0,
        "cont_hours": 2.0, "total_usage": 15000.0
    },
    "الأشعة السينية (X-Ray)": {
        "tube_temp": 35.0, "voltage": 70.0, "cont_hours": 8.0,
        "total_usage": 25000.0
    }
}

# --- 3. إدارة الحالة (Session State) ---
# التأكد من وجود قيم مبدئية عند فتح البرنامج لأول مرة
if 'device_type' not in st.session_state:
    st.session_state['device_type'] = "الرنين المغناطيسي (MRI)"

# دالة تحديث القيم عند تغيير الجهاز أو الضغط على ريسيت
def update_state(device):
    defaults = default_values[device]
    for key, val in defaults.items():
        st.session_state[key] = val

# عند تغيير نوع الجهاز، نقوم بتحميل قيمه الافتراضية
def on_device_change():
    update_state(st.session_state.device_selector)

# --- 4. CSS للتنسيق الاحترافي ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;800&display=swap');
* { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }

.control-panel {
    background-color: #ffffff; padding: 25px; border-radius: 12px;
    border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 20px;
}
.group-header {
    color: #0b3b52; font-weight: 700; margin-bottom: 15px;
    border-bottom: 2px solid #e2e8f0; padding-bottom: 5px;
}
.result-container {
    padding: 20px; border-radius: 12px; height: 100%;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.safe-box { background-color: #f0fdf4; border-top: 5px solid #22c55e; }
.warn-box { background-color: #fffbeb; border-top: 5px solid #f59e0b; }
.crit-box { background-color: #fef2f2; border-top: 5px solid #ef4444; }
</style>
""", unsafe_allow_html=True)

# --- 5. الهيدر واختيار الجهاز ---
col_header, col_select, col_reset = st.columns([2, 1, 0.5])

with col_header:
    st.title("🎛️ نظام محاكاة الأعطال (Simulator)")
    st.caption("أدخل القراءات يدوياً واضغط Enter لتحديث التحليل")

with col_select:
    # اختيار الجهاز (يتم حفظه في Session State)
    device_type = st.selectbox(
        "🔻 نوع الجهاز:", 
        list(default_values.keys()),
        key="device_selector",
        on_change=on_device_change
    )

with col_reset:
    st.write("") # مسافة لضبط المحاذاة
    st.write("")
    if st.button("🔄 استعادة الطبيعي"):
        update_state(device_type)
        st.rerun() # إعادة تشغيل فورية لتطبيق القيم

# التأكد من تحميل القيم لأول مرة
if "helium" not in st.session_state and device_type == "الرنين المغناطيسي (MRI)":
    update_state(device_type)


# --- 6. لوحة المدخلات (Grid) ---
inputs = {}

with st.container():
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    st.markdown('<div class="group-header">1️⃣ القراءات الحيوية والبيئية</div>', unsafe_allow_html=True)
    
    # === مدخلات الرنين ===
    if device_type == "الرنين المغناطيسي (MRI)":
        c1, c2, c3, c4 = st.columns(4)
        inputs['helium'] = c1.number_input("🎈 هيليوم (%)", 0.0, 100.0, key="helium", step=0.5)
        inputs['chiller_temp'] = c2.number_input("❄️ حرارة الشيلر (°C)", 0.0, 50.0, key="chiller_temp", step=0.5)
        inputs['room_temp'] = c3.number_input("🌡️ حرارة الغرفة (°C)", 10.0, 45.0, key="room_temp", step=0.5)
        inputs['humidity'] = c4.number_input("💧 الرطوبة (%)", 0.0, 100.0, key="humidity", step=1.0)
        
        st.markdown('<br><div class="group-header">2️⃣ بيانات التشغيل</div>', unsafe_allow_html=True)
        c5, c6, c7 = st.columns(3)
        inputs['cont_hours'] = c5.number_input("⏱️ تشغيل متواصل", 0.0, 24.0, key="cont_hours", step=0.5)
        inputs['total_usage'] = c6.number_input("⏳ العمر الكلي", 0.0, 200000.0, key="total_usage", step=1000.0)
        inputs['total_cases'] = c7.number_input("busts الحالات اليومية", 0, 100, key="total_cases")

    # === مدخلات المقطعية ===
    elif device_type == "الأشعة المقطعية (CT Scan)":
        c1, c2, c3, c4 = st.columns(4)
        inputs['gantry_temp'] = c1.number_input("☢️ حرارة الجانتري", 10.0, 120.0, key="gantry_temp", step=0.5)
        inputs['voltage'] = c2.number_input("⚡ جهد (V)", 0.0, 300.0, key="voltage", step=1.0)
        inputs['current'] = c3.number_input("تيار (mA)", 0.0, 50.0, key="current", step=0.5)
        inputs['room_temp'] = c4.number_input("🌡️ حرارة الغرفة", 10.0, 45.0, key="room_temp", step=0.5)

        st.markdown('<br><div class="group-header">2️⃣ بيانات التشغيل</div>', unsafe_allow_html=True)
        c5, c6, c7 = st.columns(3)
        inputs['cont_hours'] = c5.number_input("⏱️ تشغيل متواصل", 0.0, 24.0, key="cont_hours", step=0.5)
        inputs['humidity'] = c6.number_input("💧 الرطوبة (%)", 0.0, 100.0, key="humidity", step=1.0)
        inputs['total_usage'] = c7.number_input("⏳ العمر الكلي", 0.0, 200000.0, key="total_usage", step=1000.0)

    # === مدخلات الفلورو ===
    elif device_type == "الفلورسكوبي (Fluoro)":
        c1, c2, c3 = st.columns(3)
        inputs['voltage'] = c1.number_input("⚡ جهد (V)", 0.0, 300.0, key="voltage", step=1.0)
        inputs['humidity'] = c2.number_input("💧 الرطوبة (%)", 0.0, 100.0, key="humidity", step=1.0)
        inputs['tube_temp'] = c3.number_input("🔥 حرارة الأنبوب", 10.0, 100.0, key="tube_temp", step=0.5)
        
        st.markdown('<br><div class="group-header">2️⃣ بيانات التشغيل</div>', unsafe_allow_html=True)
        c4, c5 = st.columns(2)
        inputs['cont_hours'] = c4.number_input("⏱️ تشغيل متواصل", 0.0, 12.0, key="cont_hours", step=0.5)
        inputs['total_usage'] = c5.number_input("⏳ العمر الكلي", 0.0, 200000.0, key="total_usage", step=1000.0)

    # === مدخلات الإكس راي ===
    elif device_type == "الأشعة السينية (X-Ray)":
        c1, c2, c3 = st.columns(3)
        inputs['tube_temp'] = c1.number_input("🔥 حرارة الأنبوب", 10.0, 120.0, key="tube_temp", step=0.5)
        inputs['voltage'] = c2.number_input("⚡ جهد عالي (kV)", 0.0, 200.0, key="voltage", step=1.0)
        inputs['cont_hours'] = c3.number_input("⏱️ ساعات العمل", 0.0, 24.0, key="cont_hours", step=0.5)
        
        st.markdown('<br><div class="group-header">2️⃣ بيانات التشغيل</div>', unsafe_allow_html=True)
        c4 = st.columns(1)[0]
        inputs['total_usage'] = c4.number_input("⏳ العمر الكلي", 0.0, 200000.0, key="total_usage", step=1000.0)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. محرك المنطق والتحليل الشامل ---
def analyze_simulation(dev, data):
    risk_score = 0
    factors = {}
    reasons = []
    actions = []

    # --- أ. عوامل مشتركة (الرطوبة والعمر) ---
    # 1. الرطوبة
    hum_val = data.get('humidity', 40) # استخدام قيمة افتراضية لو مش موجودة
    if hum_val > 70:
        pts = 40 if dev == "الفلورسكوبي (Fluoro)" else 15
        risk_score += pts
        reasons.append(f"رطوبة عالية ({hum_val}%)")
        actions.append("تشغيل مزيلات الرطوبة / فحص التكييف")
        factors['Humidity'] = pts

    # 2. العمر الافتراضي
    usage_val = data.get('total_usage', 0)
    age_limit = 50000 if dev == "الرنين المغناطيسي (MRI)" else 25000
    if usage_val > age_limit:
        risk_score += 15
        reasons.append("الجهاز قديم (تجاوز العمر الافتراضي)")
        actions.append("زيادة وتيرة الصيانة الوقائية")
        factors['Aging'] = 15

    # --- ب. عوامل خاصة ---
    
    # 1. الرنين
    if dev == "الرنين المغناطيسي (MRI)":
        if data['helium'] < 40:
            risk_score += 50; reasons.append("خطر Quench (توقف المغناطيس)"); actions.append("تعبئة هيليوم طارئة"); factors['Helium'] = 50
        elif data['helium'] < 60:
            risk_score += 20; reasons.append("انخفاض الهيليوم"); actions.append("طلب تعبئة"); factors['Helium'] = 20
        
        if data['chiller_temp'] > 20:
            risk_score += 30; reasons.append("فشل تبريد الشيلر"); actions.append("فحص الضاغط"); factors['Cooling'] = 30
        
        # الإجهاد الحراري
        if (data['room_temp'] * 0.5) + (data['cont_hours'] * 1.5) > 25:
            risk_score += 15; reasons.append("إجهاد حراري وتشغيلي"); factors['Stress'] = 15

    # 2. المقطعية
    elif dev == "الأشعة المقطعية (CT Scan)":
        if data['gantry_temp'] > 85:
            risk_score += 50; reasons.append("حرارة الجانتري خطرة"); actions.append("إيقاف فوري"); factors['Temperature'] = 50
        elif data['gantry_temp'] > 60:
            risk_score += 25; reasons.append("ارتفاع حرارة الجانتري"); factors['Temperature'] = 25
        
        if abs(data['voltage'] - 220) > 20:
            risk_score += 30; reasons.append("تذبذب كهرباء"); actions.append("فحص Stabilizer"); factors['Electrical'] = 30

    # 3. الفلورو
    elif dev == "الفلورسكوبي (Fluoro)":
        if data['voltage'] < 190:
            risk_score += 30; reasons.append("انخفاض جهد (Under Voltage)"); factors['Electrical'] = 30
        if data['tube_temp'] > 70:
             risk_score += 20; reasons.append("حرارة الأنبوب"); factors['Temp'] = 20

    # 4. الإكس راي
    elif dev == "الأشعة السينية (X-Ray)":
        if data['tube_temp'] > 60:
            risk_score += 45; reasons.append("حرارة الأنبوب مرتفعة"); actions.append("تبريد الزيت"); factors['Tube Heat'] = 45
        if abs(data['voltage'] - 70) > 15:
             risk_score += 20; reasons.append("عدم استقرار الـ kV"); factors['Electrical'] = 20

    # النتائج
    risk_score = min(risk_score, 100)
    if risk_score >= 50: status = "خطر مرتفع 🔴"; css = "crit-box"; clr = "#ef4444"
    elif risk_score >= 20: status = "تحذير 🟡"; css = "warn-box"; clr = "#f59e0b"
    else: status = "آمن 🟢"; css = "safe-box"; clr = "#22c55e"; reasons.append("الأداء طبيعي"); actions.append("مراقبة دورية")
    
    return risk_score, status, css, reasons, actions, factors, clr

# تشغيل التحليل
score, status, css, reasons, actions, factors, clr = analyze_simulation(device_type, inputs)

# --- 8. عرض النتائج ---
st.markdown("### 3️⃣ نتائج التشخيص")

col_gauge, col_diag = st.columns([1, 2])

with col_gauge:
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        title = {'text': "مؤشر الخطر (Risk Index)", 'font': {'size': 18}},
        gauge = {'axis': {'range': [None, 100]},
                 'bar': {'color': clr},
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
                <h4 style="margin-bottom:10px;">🧐 الأسباب:</h4>
                <ul style="font-size:1.1em;">{''.join([f'<li>{r}</li>' for r in reasons])}</ul>
            </div>
            <div style="flex:1; border-right:1px solid rgba(0,0,0,0.1); padding-right:20px;">
                <h4 style="margin-bottom:10px;">🛠️ التوصيات:</h4>
                <ul style="font-size:1.1em;">{''.join([f'<li>{a}</li>' for a in actions])}</ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
# --- 9. الرسوم البيانية ---
if sum(factors.values()) > 0:
    st.markdown("---")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        fig_pie = px.pie(names=list(factors.keys()), values=list(factors.values()), title="توزيع مسببات الخطر", hole=0.5)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_c2:
        fig_bar = px.bar(x=list(factors.keys()), y=list(factors.values()), title="تأثير كل عامل (بالنقاط)", 
                         labels={'x':'العامل', 'y':'النقاط'}, text_auto=True, color=list(factors.values()), color_continuous_scale='Reds')
        st.plotly_chart(fig_bar, use_container_width=True)
