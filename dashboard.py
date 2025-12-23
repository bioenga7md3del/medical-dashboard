import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="المحاكي الذكي للأعطال", layout="wide", page_icon="🎛️")

# CSS لتنسيق احترافي
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;800&display=swap');
* { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }

/* تنسيق لوحة الإدخال */
.control-panel {
    background-color: #ffffff;
    padding: 25px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
}
/* تنسيق عناوين المجموعات */
.group-header {
    color: #0b3b52;
    font-weight: 700;
    margin-bottom: 15px;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 5px;
}

/* تنسيق صناديق النتائج */
.result-container {
    padding: 20px; border-radius: 12px; height: 100%;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.safe-box { background-color: #f0fdf4; border-top: 5px solid #22c55e; }
.warn-box { background-color: #fffbeb; border-top: 5px solid #f59e0b; }
.crit-box { background-color: #fef2f2; border-top: 5px solid #ef4444; }

h1, h2, h3 { color: #0f172a; }
</style>
""", unsafe_allow_html=True)

# --- 2. العنوان واختيار الجهاز ---
col_header, col_select = st.columns([2, 1])
with col_header:
    st.title("🎛️ نظام محاكاة الأعطال (Simulator)")
    st.markdown("**أدخل القراءات يدوياً لاختبار استجابة الذكاء الاصطناعي**")

with col_select:
    device_type = st.selectbox("🔻 نوع الجهاز:", 
                               ["الرنين المغناطيسي (MRI)", "الأشعة المقطعية (CT Scan)", 
                                "الفلورسكوبي (Fluoro)", "الأشعة السينية (X-Ray)"])

# --- 3. لوحة المدخلات (Number Inputs) ---
inputs = {}

# حاوية بيضاء للمدخلات
with st.container():
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    
    # الصف الأول: المؤشرات الحيوية والبيئية
    st.markdown('<div class="group-header">1️⃣ القراءات الحيوية والبيئية</div>', unsafe_allow_html=True)
    
    if device_type == "الرنين المغناطيسي (MRI)":
        c1, c2, c3, c4 = st.columns(4)
        with c1: inputs['helium'] = st.number_input("🎈 مستوى الهيليوم (%)", min_value=0.0, max_value=100.0, value=85.0, step=0.5)
        with c2: inputs['chiller_temp'] = st.number_input("❄️ حرارة الشيلر (°C)", min_value=0.0, max_value=50.0, value=10.0, step=0.1)
        with c3: inputs['room_temp'] = st.number_input("🌡️ حرارة الغرفة (°C)", min_value=10.0, max_value=40.0, value=22.0, step=0.1)
        with c4: inputs['humidity'] = st.number_input("💧 الرطوبة (%)", min_value=0, max_value=100, value=45, step=1)
        
        st.markdown('<br><div class="group-header">2️⃣ بيانات التشغيل</div>', unsafe_allow_html=True)
        c5, c6, c7 = st.columns(3)
        with c5: inputs['cont_hours'] = st.number_input("⏱️ تشغيل متواصل (ساعة)", 0.0, 24.0, 4.0, step=0.5)
        with c6: inputs['total_usage'] = st.number_input("⏳ العمر الكلي (ساعة)", 0, 200000, 20000, step=500)
        with c7: inputs['total_cases'] = st.number_input("busts عدد الحالات اليومي", 0, 100, 15)

    elif device_type == "الأشعة المقطعية (CT Scan)":
        c1, c2, c3, c4 = st.columns(4)
        with c1: inputs['gantry_temp'] = st.number_input("☢️ حرارة الجانتري (°C)", 10.0, 120.0, 35.0, step=0.5)
        with c2: inputs['voltage'] = st.number_input("⚡ جهد الجانتري (V)", 0.0, 300.0, 220.0, step=1.0)
        with c3: inputs['current'] = st.number_input("التيار (mA)", 0.0, 50.0, 10.0, step=0.1)
        with c4: inputs['room_temp'] = st.number_input("🌡️ حرارة الغرفة (°C)", 10.0, 45.0, 22.0, step=0.1)

        st.markdown('<br><div class="group-header">2️⃣ بيانات التشغيل</div>', unsafe_allow_html=True)
        c5, c6, c7 = st.columns(3)
        with c5: inputs['cont_hours'] = st.number_input("⏱️ تشغيل متواصل (ساعة)", 0.0, 24.0, 6.0, step=0.5)
        with c6: inputs['humidity'] = st.number_input("💧 الرطوبة (%)", 0, 100, 40)
        with c7: inputs['total_usage'] = st.number_input("⏳ العمر الكلي (ساعة)", 0, 200000, 30000, step=500)

    elif device_type == "الفلورسكوبي (Fluoro)":
        c1, c2, c3 = st.columns(3)
        with c1: inputs['voltage'] = st.number_input("⚡ الجهد الكهربائي (V)", 0.0, 300.0, 220.0, step=1.0)
        with c2: inputs['humidity'] = st.number_input("💧 الرطوبة (%)", 0, 100, 45)
        with c3: inputs['tube_temp'] = st.number_input("🔥 حرارة الأنبوب (°C)", 10.0, 100.0, 30.0, step=0.5)
        
        st.markdown('<br><div class="group-header">2️⃣ بيانات التشغيل</div>', unsafe_allow_html=True)
        c4, c5 = st.columns(2)
        with c4: inputs['cont_hours'] = st.number_input("⏱️ تشغيل متواصل", 0.0, 12.0, 2.0, step=0.5)
        with c5: inputs['total_usage'] = st.number_input("⏳ العمر الكلي", 0, 200000, 15000, step=500)

    elif device_type == "الأشعة السينية (X-Ray)":
        c1, c2, c3 = st.columns(3)
        with c1: inputs['tube_temp'] = st.number_input("🔥 حرارة الأنبوب (°C)", 10.0, 120.0, 35.0, step=0.5)
        with c2: inputs['voltage'] = st.number_input("⚡ الجهد العالي (kV)", 0.0, 200.0, 70.0, step=1.0)
        with c3: inputs['cont_hours'] = st.number_input("⏱️ ساعات العمل اليومي", 0.0, 24.0, 8.0, step=0.5)
        
        st.markdown('<br><div class="group-header">2️⃣ بيانات التشغيل</div>', unsafe_allow_html=True)
        c4 = st.columns(1)[0]
        with c4: inputs['total_usage'] = st.number_input("⏳ العمر الكلي (ساعة)", 0, 200000, 25000, step=500)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. محرك التحليل (Logic) ---
def analyze_simulation(dev, data):
    risk_score = 0
    factors = {}
    reasons = []
    actions = []

    # 1. منطق الرنين (MRI)
    if dev == "الرنين المغناطيسي (MRI)":
        if data['helium'] < 40:
            risk_score += 50; reasons.append("خطر Quench (توقف المغناطيس)"); actions.append("تعبئة هيليوم طارئة"); factors['Helium'] = 50
        elif data['helium'] < 60:
            risk_score += 20; reasons.append("انخفاض الهيليوم"); actions.append("طلب تعبئة"); factors['Helium'] = 20
        
        if data['chiller_temp'] > 20:
            risk_score += 30; reasons.append("فشل تبريد الشيلر"); actions.append("فحص الضاغط"); factors['Cooling'] = 30
        
        # معادلة الإجهاد الحراري
        if (data['room_temp'] * 0.5) + (data['cont_hours'] * 1.5) > 25:
            risk_score += 15; reasons.append("إجهاد حراري (بيئة + تشغيل)"); factors['Stress'] = 15

    # 2. منطق المقطعية (CT)
    elif dev == "الأشعة المقطعية (CT Scan)":
        if data['gantry_temp'] > 85:
            risk_score += 50; reasons.append("حرارة الجانتري حرجة"); actions.append("إيقاف فوري"); factors['Temperature'] = 50
        elif data['gantry_temp'] > 60:
            risk_score += 25; reasons.append("ارتفاع حرارة"); factors['Temperature'] = 25
        
        if abs(data['voltage'] - 220) > 20:
            risk_score += 30; reasons.append("تذبذب جهد"); actions.append("فحص Stabilizer"); factors['Electrical'] = 30

    # 3. الفلورو
    elif dev == "الفلورسكوبي (Fluoro)":
        if data['humidity'] > 75:
            risk_score += 40; reasons.append("رطوبة عالية (خطر شورت)"); actions.append("تشغيل مزيلات الرطوبة"); factors['Humidity'] = 40
        if data['voltage'] < 190:
            risk_score += 30; reasons.append("انخفاض جهد"); factors['Electrical'] = 30

    # 4. الإكس راي
    elif dev == "الأشعة السينية (X-Ray)":
        if data['tube_temp'] > 60:
            risk_score += 45; reasons.append("حرارة الأنبوب مرتفعة"); actions.append("تبريد الزيت"); factors['Tube Heat'] = 45

    # النتيجة النهائية
    risk_score = min(risk_score, 100)
    if risk_score >= 50: status = "خطر مرتفع 🔴"; css = "crit-box"; status_color = "#ef4444"
    elif risk_score >= 20: status = "تحذير 🟡"; css = "warn-box"; status_color = "#f59e0b"
    else: status = "آمن 🟢"; css = "safe-box"; status_color = "#22c55e"; reasons.append("الأداء طبيعي"); actions.append("مراقبة روتينية")
    
    return risk_score, status, css, reasons, actions, factors, status_color

# تشغيل التحليل
score, status, css, reasons, actions, factors, status_color = analyze_simulation(device_type, inputs)

# --- 5. عرض النتائج ---
st.markdown("### 3️⃣ نتائج التشخيص")

col_gauge, col_diag = st.columns([1, 2])

with col_gauge:
    # عداد السرعة
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        title = {'text': "مؤشر الخطر (Risk Index)", 'font': {'size': 18}},
        gauge = {'axis': {'range': [None, 100]},
                 'bar': {'color': status_color},
                 'steps': [{'range': [0, 20], 'color': '#dcfce7'}, {'range': [20, 50], 'color': '#fef3c7'}, {'range': [50, 100], 'color': '#fee2e2'}]}))
    fig_gauge.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_diag:
    # كارت التشخيص
    st.markdown(f"""
    <div class="result-container {css}">
        <h2 style="margin-top:0; color:{status_color}">{status}</h2>
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
    </div>
    """, unsafe_allow_html=True)
    
# --- 6. رسوم بيانية توضيحية ---
if sum(factors.values()) > 0:
    st.markdown("---")
    st.subheader("📊 تحليل العوامل المؤثرة")
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Pie Chart
        fig_pie = px.pie(names=list(factors.keys()), values=list(factors.values()), 
                         title="نسبة مساهمة كل عامل في الخطر", hole=0.5,
                         color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_chart2:
        # Bar Chart
        fig_bar = px.bar(x=list(factors.keys()), y=list(factors.values()),
                         title="شدة تأثير كل عامل (من 100)", labels={'x':'العامل', 'y':'النقاط'},
                         text_auto=True, color=list(factors.values()), color_continuous_scale='Reds')
        st.plotly_chart(fig_bar, use_container_width=True)
