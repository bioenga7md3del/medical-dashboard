import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(
    page_title="نظام التنبؤ بالأعطال - لوحة التحكم",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص الألوان لتناسب الهوية الطبية (CSS)
st.markdown("""
    <style>
    .main { background-color: #f0f9ff; }
    .stAppHeader { background-color: #f0f9ff; }
    h1, h2, h3 { color: #0b3b52; font-family: 'Tajawal', sans-serif; }
    .stMetric { background-color: #fff; padding: 15px; border-radius: 10px; border: 1px solid #e0f2fe; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. دالة المحاكاة (في حال عدم رفع ملف) ---
def get_sample_data():
    data = {
        'Device_ID': [f'DEV-{i:03d}' for i in range(1, 21)],
        'Device_Type': np.random.choice(['MRI', 'CT Scan', 'X-Ray', 'Ultrasound'], 20),
        'Temperature_C': np.random.uniform(20, 85, 20),
        'Vibration_Hz': np.random.uniform(10, 100, 20),
        'Voltage_V': np.random.uniform(210, 240, 20),
        'Hours_Since_Maintenance': np.random.randint(50, 2000, 20),
        'Last_Maintenance_Date': pd.date_range(start='2023-01-01', periods=20, freq='W')
    }
    return pd.DataFrame(data)

# --- 3. خوارزمية التنبؤ (AI Logic Mockup) ---
def predict_risk(df):
    # هذه معادلة بسيطة لمحاكاة الذكاء الاصطناعي
    # Risk Score = (Temp * 0.4) + (Vibration * 0.3) + (Hours * 0.01)
    # كلما زاد الرقم، زاد الخطر
    
    df['Risk_Score'] = (
        (df['Temperature_C'] / 100 * 40) + 
        (df['Vibration_Hz'] / 100 * 30) + 
        (df['Hours_Since_Maintenance'] / 2000 * 30)
    ).round(2)
    
    # تحديد الحالة بناءً على السكور
    conditions = [
        (df['Risk_Score'] > 60),
        (df['Risk_Score'] > 40)
    ]
    choices = ['Critical 🔴', 'Warning 🟡']
    df['Status'] = np.select(conditions, choices, default='Normal 🟢')
    
    # حساب وقت العطل المتوقع (ETTF) بشكل تقريبي
    df['ETTF_Days'] = np.where(df['Risk_Score'] > 60, np.random.randint(1, 7, len(df)), 
                               np.where(df['Risk_Score'] > 40, np.random.randint(7, 30, len(df)), 
                                        np.random.randint(30, 180, len(df))))
    return df

# --- 4. الواجهة الجانبية (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063823.png", width=80)
    st.title("لوحة التحكم")
    st.write("---")
    
    uploaded_file = st.file_uploader("📂 ارفع ملف Excel", type=['xlsx', 'csv'])
    
    st.write("---")
    st.subheader("⚙️ إعدادات النموذج")
    threshold = st.slider("عتبة الخطر (Risk Threshold)", 0, 100, 60)
    
    st.info("💡 ملاحظة: النظام يقبل ملفات Excel تحتوي على الأعمدة: Temperature, Vibration, Voltage")

# --- 5. التطبيق الرئيسي ---
st.title("🚀 النظام الذكي للتنبؤ بالأعطال - Live Dashboard")
st.markdown("تحليل البيانات الفوري باستخدام خوارزميات التنبؤ (Predictive Maintenance)")

# تحميل البيانات
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file)
        else:
            df_raw = pd.read_excel(uploaded_file)
        st.success("تم تحميل الملف بنجاح!")
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
        df_raw = get_sample_data()
else:
    st.warning("⚠️ لم يتم رفع ملف. يتم استخدام **بيانات تجريبية** للعرض.")
    df_raw = get_sample_data()

# تطبيق التحليل
df_analyzed = predict_risk(df_raw)

# تصفية البيانات حسب العتبة المختارة في السايد بار
high_risk_df = df_analyzed[df_analyzed['Risk_Score'] >= threshold]

# --- 6. مؤشرات الأداء (KPIs) ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("إجمالي الأجهزة", len(df_analyzed))
with col2:
    st.metric("أجهزة في خطر (Critical)", len(df_analyzed[df_analyzed['Status'] == 'Critical 🔴']), delta="-2", delta_color="inverse")
with col3:
    st.metric("متوسط درجة الحرارة", f"{df_analyzed['Temperature_C'].mean():.1f}°C")
with col4:
    st.metric("نسبة الجاهزية", f"{((len(df_analyzed)-len(high_risk_df))/len(df_analyzed)*100):.1f}%")

st.markdown("---")

# --- 7. الرسوم البيانية ---
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📊 تحليل المخاطر حسب نوع الجهاز")
    fig_bar = px.bar(df_analyzed, x='Device_Type', y='Risk_Score', color='Status', 
                     color_discrete_map={'Critical 🔴': '#ef4444', 'Warning 🟡': '#f59e0b', 'Normal 🟢': '#10b981'},
                     title="توزيع مخاطر الأعطال")
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    st.subheader("🌡️ الحرارة مقابل الاهتزاز")
    fig_scatter = px.scatter(df_analyzed, x='Temperature_C', y='Vibration_Hz', color='Status', size='Risk_Score',
                             hover_data=['Device_ID'], title="علاقة المؤشرات الحيوية")
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- 8. جدول التنبيهات والأعطال المتوقعة ---
st.subheader("🚨 قائمة الأجهزة ذات الأولوية القصوى (Action Required)")

if not high_risk_df.empty:
    st.dataframe(
        high_risk_df[['Device_ID', 'Device_Type', 'Status', 'Risk_Score', 'ETTF_Days', 'Temperature_C']]
        .style.applymap(lambda x: 'background-color: #fee2e2; color: black' if x > 60 else '', subset=['Risk_Score'])
        .format({'Temperature_C': '{:.1f}°C', 'Risk_Score': '{:.2f}'}),
        use_container_width=True
    )
    st.error(f"يوجد {len(high_risk_df)} جهاز يتطلب صيانة فورية لتجنب العطل!")
else:
    st.success("🎉 جميع الأجهزة تعمل بشكل جيد ضمن الحدود المسموحة.")

# --- 9. تحميل التقرير ---
st.download_button(
    label="📥 تحميل تقرير الصيانة (CSV)",
    data=df_analyzed.to_csv(index=False).encode('utf-8'),
    file_name='maintenance_prediction_report.csv',
    mime='text/csv',
)
