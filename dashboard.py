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

/* تنسيق لوحة التحكم العلوية */
.control-panel {
    background-color: #f1f5f9;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #cbd5e1;
    margin-bottom: 20px;
}
.stSlider > div > div > div > div { background-color: #0ea5e9; }

/* تنسيق صناديق النتائج */
.result-container {
    padding: 20px; border-radius: 12px; margin-top: 10px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.safe-box { background-color: #dcfce7; border: 2px solid #22c55e; color: #14532d; }
.warn-box { background-color: #fef3c7; border: 2px solid #f59e0b; color: #78350f; }
.crit-box { background-color: #fee2e2; border: 2px solid #ef4444; color: #7f1d1d; }

h1, h2, h3 { color: #0f172a; }
</style>
""", unsafe_allow_html=True)

# --- 2. العنوان واختيار الجهاز (في الأعلى) ---
col_header, col_select = st.columns([2, 1])
with col_header:
    st.title("🎛️ محاكي الأعطال التفاعلي")
    st.caption("قم بتغيير المعطيات وشاهد تشخيص الذكاء الاصطناعي لحظياً")

with col_select:
    device_type = st.selectbox("🔻 اختر الجهاز للبدء:", 
                               ["الرنين المغناطيسي (MRI)", "الأشعة المقطعية (CT Scan)", 
                                "الفلورسكوبي (Fluoro)", "الأشعة السينية (X-Ray)"])

# --- 3. لوحة التحكم (Grid Layout) ---
st.markdown("### 1️⃣ لوحة المدخلات (Control Panel)")
inputs = {}

# حاوية رمادية للمدخلات
with st.container():
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    
    if device_type == "الرنين المغناطيسي (MRI)":
        c1, c2, c3, c4 = st.columns(4)
        with c1: inputs['helium'] = st.slider("🎈 مستوى الهيليوم (%)", 0, 100, 85)
        with c2: inputs['chiller_temp'] = st.slider("❄️ حرارة الشيلر (°C)", 5, 30, 10)
        with c3: inputs['room_temp'] = st.slider("🌡️ حرارة الغرفة (°C)", 15, 35, 22)
        with c4: inputs['humidity'] = st.slider("💧 الرطوبة (%)", 20, 90, 45)
        
        c5, c6, c7 = st.columns(3)
        with c5: inputs['cont_hours'] = st.slider("⏱️ تشغيل متواصل (ساعة)", 0, 24, 4)
        with c6: inputs['total_usage'] = st.number_input("⏳ العمر (ساعة)", 0, 100000, 20000, step=1000)
        with c7: inputs['total_cases'] = st.slider("busts ضغط الحالات", 0, 50, 15)

    elif device_type == "الأشعة المقطعية (CT Scan)":
        c1, c2, c3, c4 = st.columns(4)
        with c1: inputs['gantry_temp'] = st.slider("☢️ حرارة الجانتري (°C)", 20, 100, 35)
        with c2: inputs['voltage'] = st.slider("⚡ جهد الجانتري (V)", 180, 260, 220)
        with c3: inputs['room_temp'] = st.slider("🌡️ حرارة الغرفة (°C)", 15, 35, 22)
        with c4: inputs['current'] = st.slider("التيار (mA)", 5, 20, 10)

        c5, c6, c7 = st.columns(3)
        with c5: inputs['cont_hours'] = st.slider("⏱️ تشغيل متواصل", 0, 24, 6)
        with c6: inputs['humidity'] = st.slider("💧 الرطوبة (%)", 20, 90, 40)
        with c7: inputs['total_usage'] = st.number_input("⏳ العمر (ساعة)", 0, 100000, 30000, step=1000)

    elif device_type == "الفلورسكوبي (Fluoro)":
        c1, c2, c3 = st.columns(3)
        with c1: inputs['voltage'] = st.slider("⚡ الجهد الكهربائي (V)", 150, 280, 220)
        with c2: inputs['humidity'] = st.slider("💧 الرطوبة (%)", 10, 100, 45)
        with c3: inputs['tube_temp'] = st.slider("🔥 حرارة الأنبوب (°C)", 20, 80, 30)
        
        c4, c5 = st.columns(2)
        with c4: inputs['cont_hours'] = st.slider("⏱️ تشغيل متواصل", 0, 12, 2)
        with c5: inputs['total_usage'] = st.number_input("⏳ العمر التشغيلي", 0, 100000, 15000)

    elif device_type == "الأشعة السينية (X-Ray)":
        c1, c2, c3 = st.columns(3)
        with c1: inputs['tube_temp'] = st.slider("🔥 حرارة الأنبوب (°C)", 20, 90, 35)
        with c2: inputs['voltage'] = st.slider("⚡ الجهد العالي (kV)", 40, 150, 70)
        with c3: inputs['cont_hours'] = st.slider("⏱️ ساعات العمل اليومي", 0, 24, 8)
        
        c4 = st.columns(1)[0]
        with c4: inputs['total_usage'] = st.number_input("⏳ العمر التشغيلي (ساعة)", 0, 100000, 25000)
    
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
        
        if (data['room_temp'] * 0.5) + (data['cont_hours'] * 1.5) > 25:
            risk_score += 15; reasons.append("إجهاد حراري"); factors['Usage Stress'] = 15

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
    if risk_score >= 50: status = "خطر مرتفع 🔴"; css = "crit-box"
    elif risk_score >= 20: status = "تحذير 🟡"; css = "warn-box"
    else: status = "آمن 🟢"; css = "safe-box"; reasons.append("الأداء طبيعي"); actions.append("مراقبة روتينية")
    
    return risk_score, status, css, reasons, actions, factors

# تشغيل التحليل
score, status, css, reasons, actions, factors = analyze_simulation(device_type, inputs)

# --- 5. عرض النتائج ---
st.markdown("### 2️⃣ نتائج التحليل والتشخيص")

col_gauge, col_diag = st.columns([1, 2])

with col_gauge:
    # عداد السرعة
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        title = {'text': "مؤشر الخطر", 'font': {'size': 20}},
        gauge = {'axis': {'range': [None, 100]},
                 'bar': {'color': "#ef4444" if score>50 else "#f59e0b" if score>20 else "#22c55e"},
                 'steps': [{'range': [0, 20], 'color': '#dcfce7'}, {'range': [20, 50], 'color': '#fef3c7'}, {'range': [50, 100], 'color': '#fee2e2'}]}))
    fig_gauge.update_layout(height=300, margin=dict(l=20,r=20,t=50,b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_diag:
    # كارت التشخيص
    st.markdown(f"""
    <div class="result-container {css}">
        <h2 style="margin-top:0;">الحالة: {status}</h2>
        <hr style="border-color:rgba(0,0,0,0.1)">
        <div style="display:flex; justify-content:space-between;">
            <div style="flex:1;">
                <h4 style="margin-bottom:5px;">🧐 الأسباب الجذرية:</h4>
                <ul>{''.join([f'<li>{r}</li>' for r in reasons])}</ul>
            </div>
            <div style="flex:1;">
                <h4 style="margin-bottom:5px;">🛠️ الإجراء المطلوب:</h4>
                <ul>{''.join([f'<li>{a}</li>' for a in actions])}</ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # الرسم البياني للعوامل
    if sum(factors.values()) > 0:
        st.markdown("#### 📊 توزيع العوامل المؤثرة:")
        fig_bar = px.bar(x=list(factors.keys()), y=list(factors.values()), 
                         labels={'x':'العامل', 'y':'نسبة الخطر'}, text_auto=True)
        fig_bar.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)
