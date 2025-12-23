import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="محاكي تحليل الأعطال", layout="wide", page_icon="🎛️")

# CSS لتنسيق العربية
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;800&display=swap');
* { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
.stSlider > div > div > div > div { background-color: #0ea5e9; }
.metric-box {
    padding: 15px; border-radius: 10px; border: 1px solid #e0f2fe;
    text-align: center; background-color: #f8fafc;
}
.diagnosis-box {
    padding: 20px; border-radius: 10px; margin-top: 20px;
}
.safe-box { background-color: #dcfce7; border: 1px solid #22c55e; color: #14532d; }
.warn-box { background-color: #fef3c7; border: 1px solid #f59e0b; color: #78350f; }
.crit-box { background-color: #fee2e2; border: 1px solid #ef4444; color: #7f1d1d; }
</style>
""", unsafe_allow_html=True)

# --- 2. القائمة الجانبية (لوحة التحكم بالمحاكاة) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/10606/10606037.png", width=80)
    st.title("🎛️ لوحة المحاكاة")
    
    # اختيار الجهاز
    device_type = st.selectbox("اختر الجهاز للمحاكاة:", 
                               ["الرنين المغناطيسي (MRI)", "الأشعة المقطعية (CT Scan)", 
                                "الفلورسكوبي (Fluoro)", "الأشعة السينية (X-Ray)"])
    
    st.markdown("---")
    st.subheader("أدخل المعطيات الحالية:")

    # متغيرات سيتم ملؤها حسب نوع الجهاز
    inputs = {}

    if device_type == "الرنين المغناطيسي (MRI)":
        inputs['room_temp'] = st.slider("🌡️ درجة حرارة الغرفة (°C)", 15, 35, 22)
        inputs['chiller_temp'] = st.slider("❄️ درجة حرارة الشيلر (°C)", 5, 30, 10)
        inputs['humidity'] = st.slider("💧 الرطوبة (%)", 20, 90, 45)
        inputs['helium'] = st.slider("🎈 مستوى الهيليوم (%)", 0, 100, 85)
        inputs['cont_hours'] = st.slider("⏱️ ساعات تشغيل متواصلة", 0, 24, 4)
        inputs['total_cases'] = st.slider("busts عدد الحالات اليومي", 0, 50, 15)
        inputs['total_usage'] = st.number_input("⏳ العمر التشغيلي (ساعة)", 0, 100000, 20000)

    elif device_type == "الأشعة المقطعية (CT Scan)":
        inputs['room_temp'] = st.slider("🌡️ حرارة الغرفة (°C)", 15, 35, 22)
        inputs['gantry_temp'] = st.slider("☢️ حرارة الجانتري (°C)", 20, 100, 35)
        inputs['voltage'] = st.slider("⚡ جهد الجانتري (V)", 180, 260, 220)
        inputs['current'] = st.slider("امبير التيار (mA)", 5, 20, 10)
        inputs['humidity'] = st.slider("💧 الرطوبة (%)", 20, 90, 40)
        inputs['cont_hours'] = st.slider("⏱️ ساعات تشغيل متواصلة", 0, 24, 6)
        inputs['total_usage'] = st.number_input("⏳ العمر التشغيلي (ساعة)", 0, 100000, 30000)

    elif device_type == "الفلورسكوبي (Fluoro)":
        inputs['voltage'] = st.slider("⚡ الجهد الكهربائي (V)", 150, 280, 220)
        inputs['humidity'] = st.slider("💧 الرطوبة (%)", 10, 100, 45)
        inputs['tube_temp'] = st.slider("🔥 حرارة الأنبوب (°C)", 20, 80, 30)
        inputs['cont_hours'] = st.slider("⏱️ ساعات تشغيل متواصلة", 0, 12, 2)
        inputs['total_usage'] = st.number_input("⏳ العمر التشغيلي (ساعة)", 0, 100000, 15000)

    elif device_type == "الأشعة السينية (X-Ray)":
        inputs['tube_temp'] = st.slider("🔥 حرارة الأنبوب (°C)", 20, 90, 35)
        inputs['voltage'] = st.slider("⚡ الجهد العالي (kV)", 40, 150, 70) # هنا kV
        inputs['cont_hours'] = st.slider("⏱️ ساعات العمل اليومي", 0, 24, 8)
        inputs['total_usage'] = st.number_input("⏳ العمر التشغيلي (ساعة)", 0, 100000, 25000)

# --- 3. محرك المنطق والتحليل (Physics Engine) ---
def analyze_simulation(dev, data):
    risk_score = 0
    factors = {} # لتخزين نسبة مساهمة كل عامل في الخطر
    reasons = []
    actions = []

    # 1. منطق الرنين (MRI Logic)
    if dev == "الرنين المغناطيسي (MRI)":
        # الهيليوم (وزن عالي)
        if data['helium'] < 40:
            risk_score += 50
            reasons.append("خطر Quench (توقف المغناطيس)")
            actions.append("تعبئة هيليوم طارئة")
            factors['Helium'] = 50
        elif data['helium'] < 60:
            risk_score += 20
            reasons.append("انخفاض مستوى الهيليوم")
            actions.append("طلب تعبئة")
            factors['Helium'] = 20
        else: factors['Helium'] = 0

        # الشيلر والحرارة
        if data['chiller_temp'] > 20:
            risk_score += 30
            reasons.append("فشل نظام تبريد الشيلر")
            actions.append("فحص ضاغط الشيلر ومضخة الماء")
            factors['Cooling'] = 30
        else: factors['Cooling'] = 0

        # تأثير التشغيل المتواصل على الحرارة
        # معادلة افتراضية: لو الغرفة حارة + تشغيل طويل = خطر
        heat_stress = (data['room_temp'] * 0.5) + (data['cont_hours'] * 1.5)
        if heat_stress > 25: # عتبة افتراضية
            risk_score += 15
            reasons.append("إجهاد حراري بسبب التشغيل المستمر")
            factors['Usage Stress'] = 15
        else: factors['Usage Stress'] = 0

    # 2. منطق المقطعية (CT Logic)
    elif dev == "الأشعة المقطعية (CT Scan)":
        # حرارة الجانتري
        if data['gantry_temp'] > 85:
            risk_score += 50
            reasons.append("حرارة الجانتري حرجة جداً")
            actions.append("إيقاف الجهاز للتبريد فوراً")
            factors['Temperature'] = 50
        elif data['gantry_temp'] > 60:
            risk_score += 25
            reasons.append("ارتفاع حرارة المكونات الداخلية")
            factors['Temperature'] = 25
        else: factors['Temperature'] = 0

        # الكهرباء
        volt_diff = abs(data['voltage'] - 220)
        if volt_diff > 20:
            risk_score += 30
            reasons.append("تذبذب شديد في الجهد الكهربائي")
            actions.append("فحص منظم الجهد (Stabilizer)")
            factors['Electrical'] = 30
        else: factors['Electrical'] = 0

        # العمر
        if data['total_usage'] > 40000:
            risk_score += 15
            reasons.append("الجهاز تجاوز العمر الافتراضي للكفاءة")
            factors['Aging'] = 15
        else: factors['Aging'] = 0

    # 3. منطق الفلورو (Fluoro Logic)
    elif dev == "الفلورسكوبي (Fluoro)":
        # الرطوبة (خطر كهربائي)
        if data['humidity'] > 75:
            risk_score += 40
            reasons.append("رطوبة عالية (خطر قصر دائرة)")
            actions.append("تشغيل مزيلات الرطوبة فوراً")
            factors['Humidity'] = 40
        else: factors['Humidity'] = 0

        # الجهد
        if data['voltage'] < 190:
            risk_score += 30
            reasons.append("انخفاض الجهد (Under Voltage)")
            factors['Electrical'] = 30
        else: factors['Electrical'] = 0

    # 4. منطق الإكس راي (X-Ray Logic)
    elif dev == "الأشعة السينية (X-Ray)":
        if data['tube_temp'] > 60:
            risk_score += 45
            reasons.append("حرارة الأنبوب مرتفعة")
            actions.append("توقف عن التصوير لتبريد الزيت")
            factors['Tube Heat'] = 45
        else: factors['Tube Heat'] = 0

    # تقييم نهائي
    risk_score = min(risk_score, 100) # لا يزيد عن 100
    if risk_score >= 50:
        status = "خطر مرتفع 🔴"
        box_class = "crit-box"
    elif risk_score >= 20:
        status = "تحذير 🟡"
        box_class = "warn-box"
    else:
        status = "آمن 🟢"
        box_class = "safe-box"
        reasons.append("المؤشرات ضمن المعدل الطبيعي")
        actions.append("استمرار المراقبة الروتينية")

    return risk_score, status, box_class, reasons, actions, factors

# --- 4. واجهة العرض الرئيسية ---
st.title(f"معمل تحليل: {device_type}")
st.markdown("قم بتغيير المعطيات من القائمة الجانبية ولاحظ كيف يحلل النظام المخاطر.")

# تشغيل التحليل
score, status, css, reasons, actions, factors = analyze_simulation(device_type, inputs)

# عرض النتيجة الرئيسية (KPIs)
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    # عداد السرعة للخطر
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        title = {'text': "مؤشر الخطر الحالي"},
        gauge = {'axis': {'range': [None, 100]},
                 'bar': {'color': "#ef4444" if score>50 else "#f59e0b" if score>20 else "#22c55e"},
                 'steps': [{'range': [0, 20], 'color': '#dcfce7'}, 
                           {'range': [20, 50], 'color': '#fef3c7'},
                           {'range': [50, 100], 'color': '#fee2e2'}]}))
    fig_gauge.update_layout(height=250, margin=dict(l=10,r=10,t=30,b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    # صندوق التشخيص
    st.markdown(f"""
    <div class="diagnosis-box {css}">
        <h2 style="margin:0; text-align:center;">{status}</h2>
        <hr style="border-color:rgba(0,0,0,0.1)">
        <h4 style="margin-bottom:5px;">🧐 التشخيص التحليلي (الأسباب):</h4>
        <ul>{''.join([f'<li>{r}</li>' for r in reasons])}</ul>
        <h4 style="margin-bottom:5px;">🛠️ الإجراء الموصى به:</h4>
        <ul>{''.join([f'<li>{a}</li>' for a in actions])}</ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # تفاصيل سريعة
    st.markdown("### 📊 القراءات الحالية")
    for key, val in inputs.items():
        # تنسيق الاسم للعرض
        name = key.replace('_', ' ').title()
        st.metric(name, val)

st.markdown("---")

# --- 5. الرسوم البيانية التحليلية (Visual Correlation) ---
col_charts1, col_charts2 = st.columns(2)

with col_charts1:
    st.subheader("تحليل مسببات الخطر (Risk Factors)")
    if sum(factors.values()) > 0:
        # رسم دائري يوضح ما هو السبب الأكبر في الخطر
        fig_pie = px.pie(names=list(factors.keys()), values=list(factors.values()), 
                         title="ما هو العامل المؤثر الأكبر الآن؟", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("الجهاز سليم، لا توجد عوامل خطر لعرضها.")

with col_charts2:
    st.subheader("محاكاة العلاقة (Correlation Simulation)")
    # رسم يوضح أين تقع نقطتك الحالية مقارنة بمنطقة الخطر
    # سنصنع بيانات وهمية للخلفية لكي تظهر "منطقة الخطر"
    
    if device_type == "الرنين المغناطيسي (MRI)":
        # رسم العلاقة بين الهيليوم وحرارة الشيلر
        fig_sim = go.Figure()
        # منطقة الخطر
        fig_sim.add_shape(type="rect", x0=20, y0=0, x1=35, y1=50, fillcolor="red", opacity=0.2, line_width=0)
        # النقطة الحالية
        fig_sim.add_trace(go.Scatter(x=[inputs['chiller_temp']], y=[inputs['helium']], 
                                     mode='markers', marker=dict(size=20, color='black'), name='حالتك الحالية'))
        fig_sim.update_layout(title="موقعك الحالي: الهيليوم vs الشيلر", 
                              xaxis_title="حرارة الشيلر", yaxis_title="مستوى الهيليوم")
        st.plotly_chart(fig_sim, use_container_width=True)
        st.caption("المربع الأحمر يمثل منطقة الخطر (حرارة عالية + هيليوم منخفض).")

    elif device_type == "الأشعة المقطعية (CT Scan)":
        # رسم العلاقة بين حرارة الجانتري والفولت
        fig_sim = go.Figure()
        fig_sim.add_shape(type="rect", x0=180, y0=80, x1=260, y1=100, fillcolor="red", opacity=0.2, line_width=0)
        fig_sim.add_trace(go.Scatter(x=[inputs['voltage']], y=[inputs['gantry_temp']], 
                                     mode='markers', marker=dict(size=20, color='blue'), name='حالتك الحالية'))
        fig_sim.update_layout(title="موقعك الحالي: الفولت vs حرارة الجانتري",
                              xaxis_title="الجهد الكهربائي", yaxis_title="حرارة الجانتري")
        st.plotly_chart(fig_sim, use_container_width=True)
