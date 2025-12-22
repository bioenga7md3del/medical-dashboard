import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(
    page_title="نظام التنبؤ بالأعطال - لوحة القيادة",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص CSS لدعم اللغة العربية والخطوط
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0f2fe;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        text-align: right !important;
    }
    
    /* ضبط اتجاه العناوين */
    h1, h2, h3, h4, h5, h6 {
        text-align: right;
        color: #0b3b52;
    }
    
    /* ضبط الجداول */
    .stDataFrame { direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. دالة المحاكاة (في حال عدم رفع ملف) ---
def get_sample_data():
    # توليد بيانات وهمية لاختبار النظام
    data = {
        'Device_ID': [f'DEV-{i:03d}' for i in range(1, 21)],
        'Device_Type': np.random.choice(['MRI', 'CT Scan', 'X-Ray', 'Fluoroscopy'], 20),
        'Location': np.random.choice(['المستشفى الرئيسي', 'وحدة الطوارئ', 'العيادات الخارجية', 'مركز الأشعة'], 20),
        'Temperature_C': np.random.uniform(20, 85, 20),
        'Vibration_Hz': np.random.uniform(5, 100, 20),
        'Voltage_V': np.random.uniform(180, 240, 20), # الجهد الطبيعي 220
        'Humidity_Percent': np.random.uniform(30, 80, 20),
        'Helium_Level': np.random.uniform(30, 100, 20), # خاص بالرنين
        'Usage_Hours': np.random.randint(500, 10000, 20),
        'Last_Maint_Date': pd.date_range(start='2023-01-01', periods=20, freq='W')
    }
    return pd.DataFrame(data)

# --- 3. خوارزمية التنبؤ (قلب النظام الذكي) ---
def predict_risk(df):
    # التأكد من أن الأعمدة رقمية
    cols_to_numeric = ['Temperature_C', 'Vibration_Hz', 'Voltage_V', 'Humidity_Percent', 'Helium_Level', 'Usage_Hours']
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # --- معادلة حساب الخطر ---
    
    # 1. الحرارة والاهتزاز (أساس المشاكل الميكانيكية)
    # كلما زادت الحرارة عن 40 والاهتزاز عن 20، زاد الخطر
    base_risk = (df['Temperature_C'] * 0.4) + (df['Vibration_Hz'] * 0.3)
    
    # 2. الجهد الكهربائي (Electric Stability)
    # الانحراف عن 220 فولت يعتبر مشكلة
    voltage_risk = abs(df['Voltage_V'] - 220) * 0.5
    
    # 3. الهيليوم (Critical for MRI)
    # إذا كان الجهاز MRI ومستوى الهيليوم أقل من 60، الخطر يتضاعف
    helium_risk = np.where(
        (df['Device_Type'] == 'MRI') & (df['Helium_Level'] < 60), 
        (60 - df['Helium_Level']) * 1.5, 
        0
    )
    
    # 4. الرطوبة (Environmental Factor)
    # الرطوبة العالية جدا (>70) أو المنخفضة جدا (<30) تزيد الخطر قليلاً
    humidity_risk = np.where(
        (df['Humidity_Percent'] > 70) | (df['Humidity_Percent'] < 30), 
        10, 
        0
    )

    # تجميع النقاط
    df['Risk_Score'] = base_risk + voltage_risk + helium_risk + humidity_risk + (df['Usage_Hours'] / 2000)
    
    # تقييد النتيجة لتكون بين 0 و 100
    df['Risk_Score'] = df['Risk_Score'].clip(upper=100)

    # تصنيف الحالة (Status)
    conditions = [
        (df['Risk_Score'] >= 75),
        (df['Risk_Score'] >= 50)
    ]
    choices = ['حرج 🔴', 'تحذير 🟡']
    df['Status'] = np.select(conditions, choices, default='مستقر 🟢')
    
    # توقع وقت العطل (ETTF - Days)
    df['ETTF_Days'] = np.where(df['Status'] == 'حرج 🔴', np.random.randint(1, 5, len(df)), 
                               np.where(df['Status'] == 'تحذير 🟡', np.random.randint(5, 30, len(df)), 
                                        np.random.randint(30, 365, len(df))))
    
    return df

# --- 4. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063823.png", width=80)
    st.title("لوحة التحكم")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📂 رفع ملف البيانات (CSV/Excel)", type=['xlsx', 'csv'])
    
    st.markdown("---")
    st.subheader("⚙️ إعدادات الحساسية")
    threshold = st.slider("عتبة الخطر (Risk Threshold)", 0, 100, 75)
    
    st.info("""
    **تعليمات:**
    - النظام يقبل ملفات Excel/CSV.
    - الأعمدة المطلوبة: Device_ID, Temperature_C, Vibration_Hz, Voltage_V.
    """)

# --- 5. واجهة التطبيق الرئيسية ---
st.title("🚀 النظام الذكي للتنبؤ بأعطال الأجهزة الطبية")
st.markdown("**مرحباً بك في لوحة القيادة المركزية. يتم هنا تحليل البيانات الحيوية للأجهزة لحظياً.**")

# تحميل البيانات ومعالجتها
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file)
        else:
            df_raw = pd.read_excel(uploaded_file)
        st.success("✅ تم تحميل الملف بنجاح!")
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء قراءة الملف: {e}")
        df_raw = get_sample_data()
else:
    st.warning("⚠️ لم يتم رفع ملف. جاري عرض **بيانات تجريبية (Simulation)**.")
    df_raw = get_sample_data()

# تشغيل خوارزمية الذكاء الاصطناعي
df_analyzed = predict_risk(df_raw)

# تصفية البيانات الخطرة
high_risk_df = df_analyzed[df_analyzed['Risk_Score'] >= threshold]

# --- 6. مؤشرات الأداء الرئيسية (KPIs) ---
st.markdown("### 📊 نظرة عامة على الحالة")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("إجمالي الأجهزة المراقبة", len(df_analyzed))
with kpi2:
    st.metric("أجهزة في حالة حرجة", len(df_analyzed[df_analyzed['Status'] == 'حرج 🔴']), delta_color="inverse")
with kpi3:
    st.metric("متوسط درجة الحرارة", f"{df_analyzed['Temperature_C'].mean():.1f}°C")
with kpi4:
    safe_percent = ((len(df_analyzed) - len(high_risk_df)) / len(df_analyzed)) * 100
    st.metric("نسبة الجاهزية التشغيلية", f"{safe_percent:.1f}%")

st.markdown("---")

# --- 7. الرسوم البيانية التفاعلية ---
col_charts1, col_charts2 = st.columns([2, 1])

with col_charts1:
    st.subheader("توزيع المخاطر حسب نوع الجهاز")
    # تعريب أسماء الأعمدة للعرض فقط
    chart_df = df_analyzed.rename(columns={'Device_Type': 'نوع الجهاز', 'Risk_Score': 'مؤشر الخطر', 'Status': 'الحالة'})
    
    fig_bar = px.bar(chart_df, x='نوع الجهاز', y='مؤشر الخطر', color='الحالة', 
                     color_discrete_map={'حرج 🔴': '#ef4444', 'تحذير 🟡': '#f59e0b', 'مستقر 🟢': '#10b981'},
                     text_auto=True)
    fig_bar.update_layout(font_family="Tajawal")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_charts2:
    st.subheader("علاقة الحرارة بالاهتزاز")
    fig_scatter = px.scatter(df_analyzed, x='Temperature_C', y='Vibration_Hz', 
                             color='Status', size='Risk_Score', hover_data=['Device_ID'],
                             labels={'Temperature_C': 'درجة الحرارة', 'Vibration_Hz': 'الاهتزاز (Hz)'},
                             color_discrete_map={'حرج 🔴': '#ef4444', 'تحذير 🟡': '#f59e0b', 'مستقر 🟢': '#10b981'})
    fig_scatter.update_layout(font_family="Tajawal")
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- 8. جدول التنبيهات التفصيلي ---
st.subheader("🚨 الأجهزة التي تتطلب تدخلاً فورياً")

if not high_risk_df.empty:
    # تنسيق الجدول للعرض
    display_cols = ['Device_ID', 'Device_Type', 'Location', 'Status', 'Risk_Score', 'ETTF_Days', 'Temperature_C', 'Helium_Level']
    
    # تلوين الصفوف الخطرة
    def highlight_risk(val):
        color = '#fee2e2' if val > 75 else '#fffbeb' if val > 50 else ''
        return f'background-color: {color}; color: black'

    st.dataframe(
        high_risk_df[display_cols]
        .style.applymap(highlight_risk, subset=['Risk_Score'])
        .format({'Temperature_C': '{:.1f}°C', 'Risk_Score': '{:.1f}', 'Helium_Level': '{:.1f}%', 'ETTF_Days': '{:.0f} يوم'}),
        use_container_width=True
    )
    
    st.error(f"⚠️ تنبيه: تم رصد {len(high_risk_df)} جهاز تجاوزت عتبة الخطر المسموح بها!")
else:
    st.success("🎉 ممتاز! جميع الأجهزة تعمل بكفاءة ولا توجد مخاطر وشيكة.")

# --- 9. تصدير التقارير ---
st.markdown("### 📥 التقارير")
col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    st.download_button(
        label="تحميل تقرير التحليل الكامل (CSV)",
        data=df_analyzed.to_csv(index=False).encode('utf-8-sig'), # utf-8-sig لدعم العربي في إكسل
        file_name='medical_maintenance_report.csv',
        mime='text/csv',
    )
