import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="لوحة القيادة الذكية - الصيانة الطبية",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS للعربية والتصميم
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stMetric { background-color: #ffffff; border: 1px solid #e0f2fe; box-shadow: 0 2px 5px rgba(0,0,0,0.05); text-align: right !important; }
    h1, h2, h3 { text-align: right; color: #0b3b52; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. دالة التنبؤ (نفس المنطق الذكي السابق) ---
def predict_risk(df):
    cols_to_numeric = ['Temperature_C', 'Vibration_Hz', 'Voltage_V', 'Humidity_Percent', 'Helium_Level', 'Usage_Hours']
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    base_risk = (df['Temperature_C'] * 0.4) + (df['Vibration_Hz'] * 0.3)
    voltage_risk = abs(df['Voltage_V'] - 220) * 0.5
    helium_risk = np.where((df['Device_Type'] == 'MRI') & (df['Helium_Level'] < 60), (60 - df['Helium_Level']) * 2, 0)
    
    df['Risk_Score'] = base_risk + voltage_risk + helium_risk + (df['Usage_Hours'] / 3000)
    df['Risk_Score'] = df['Risk_Score'].clip(upper=100)

    conditions = [(df['Risk_Score'] >= 75), (df['Risk_Score'] >= 50)]
    choices = ['حرج 🔴', 'تحذير 🟡']
    df['Status'] = np.select(conditions, choices, default='مستقر 🟢')
    
    df['ETTF_Days'] = np.where(df['Status'] == 'حرج 🔴', np.random.randint(1, 7, len(df)), 
                               np.random.randint(30, 365, len(df)))
    return df

# --- 3. السايد بار (القائمة الجانبية) والفلاتر ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063823.png", width=80)
    st.title("لوحة التحكم")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📂 رفع ملف البيانات (Excel/CSV)", type=['xlsx', 'csv'])
    
    st.markdown("---")
    st.subheader("🔍 خيارات التصفية (Filters)")
    
    # مكان الفلاتر (سيتم تعبئتها بعد تحميل البيانات)
    department_filter = []
    device_filter = []
    
    st.markdown("---")
    threshold = st.slider("عتبة الخطر", 0, 100, 75)

# --- 4. معالجة البيانات ---
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file)
        else:
            df_raw = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"خطأ: {e}")
        st.stop()
else:
    # رسالة ترحيبية
    st.info("👋 يرجى رفع ملف Excel الذي قمت بتوليده باستخدام كود البايثون (medical_data_large.xlsx).")
    st.stop() # توقف هنا حتى يتم رفع الملف

# تطبيق التحليل
df_analyzed = predict_risk(df_raw)

# --- 5. تطبيق الفلاتر (الجزء الجديد) ---
with st.sidebar:
    # استخراج القيم الفريدة للقوائم
    all_departments = df_analyzed['Location'].unique()
    all_devices = df_analyzed['Device_Type'].unique()
    
    # إنشاء قوائم الاختيار المتعدد
    department_filter = st.multiselect("اختر القسم / الموقع:", all_departments, default=all_departments)
    device_filter = st.multiselect("اختر نوع الجهاز:", all_devices, default=all_devices)

# تصفية الداتا فريم بناءً على الاختيارات
df_filtered = df_analyzed[
    (df_analyzed['Location'].isin(department_filter)) &
    (df_analyzed['Device_Type'].isin(device_filter))
]

# تصفية المخاطر العالية من البيانات المفلترة
high_risk_df = df_filtered[df_filtered['Risk_Score'] >= threshold]

# --- 6. العرض الرئيسي (KPIs) ---
st.title("🚀 النظام الذكي للتنبؤ بالأعطال")
st.markdown(f"**عرض تحليلي لـ {len(df_filtered)} جهاز (بعد التصفية)**")

k1, k2, k3, k4 = st.columns(4)
with k1: st.metric("إجمالي الأجهزة المعروضة", len(df_filtered))
with k2: st.metric("أجهزة في حالة حرجة", len(high_risk_df), delta_color="inverse")
with k3: st.metric("متوسط الحرارة", f"{df_filtered['Temperature_C'].mean():.1f}°C")
with k4: st.metric("متوسط الاهتزاز", f"{df_filtered['Vibration_Hz'].mean():.1f} Hz")

st.markdown("---")

# --- 7. الرسوم البيانية (تتأثر بالفلاتر) ---
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("توزيع حالة الأجهزة (حسب القسم)")
    fig_bar = px.histogram(df_filtered, x='Location', color='Status', 
                           color_discrete_map={'حرج 🔴': '#ef4444', 'تحذير 🟡': '#f59e0b', 'مستقر 🟢': '#10b981'},
                           barmode='group', title="عدد الأجهزة وحالتها في كل قسم")
    fig_bar.update_layout(font_family="Tajawal")
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    st.subheader("نسبة المخاطر")
    fig_pie = px.pie(df_filtered, names='Status', 
                     color='Status',
                     color_discrete_map={'حرج 🔴': '#ef4444', 'تحذير 🟡': '#f59e0b', 'مستقر 🟢': '#10b981'})
    fig_pie.update_layout(font_family="Tajawal")
    st.plotly_chart(fig_pie, use_container_width=True)

# رسم بياني إضافي للتحليل العميق
st.subheader("تحليل العلاقة: العمر التشغيلي vs مؤشر الخطر")
fig_scatter = px.scatter(df_filtered, x='Usage_Hours', y='Risk_Score', color='Device_Type', size='Temperature_C',
                         hover_data=['Device_ID', 'Location'], title="هل الأجهزة القديمة أكثر عرضة للخطر؟")
fig_scatter.update_layout(font_family="Tajawal")
st.plotly_chart(fig_scatter, use_container_width=True)

# --- 8. جدول البيانات ---
st.subheader("📋 تفاصيل الأجهزة (البيانات المفلترة)")

# خيار لإظهار فقط الأجهزة الخطرة
show_only_risk = st.checkbox("إظهار الأجهزة الحرجة فقط")
if show_only_risk:
    display_df = high_risk_df
else:
    display_df = df_filtered

st.dataframe(
    display_df[['Device_ID', 'Device_Type', 'Location', 'Status', 'Risk_Score', 'Temperature_C', 'Vibration_Hz']]
    .style.applymap(lambda v: 'background-color: #fee2e2' if v > 75 else '', subset=['Risk_Score'])
    .format({'Temperature_C': '{:.1f}', 'Risk_Score': '{:.1f}', 'Vibration_Hz': '{:.1f}'}),
    use_container_width=True
)
