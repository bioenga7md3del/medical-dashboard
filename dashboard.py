import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="نظام الصيانة الذكي - التشخيص والتوجيه",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS للعربية والتصميم
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stMetric { background-color: #ffffff; border: 1px solid #e0f2fe; box-shadow: 0 2px 5px rgba(0,0,0,0.05); text-align: right !important; }
    h1, h2, h3 { text-align: right; color: #0b3b52; }
    /* تنسيق خاص للنصائح */
    .advice-box { padding: 10px; border-radius: 5px; font-weight: bold; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. دالة التنبؤ + التشخيص (سبب المشكلة والنصيحة) ---
def analyze_and_diagnose(df):
    # تحويل الأرقام
    cols_to_numeric = ['Temperature_C', 'Vibration_Hz', 'Voltage_V', 'Humidity_Percent', 'Helium_Level', 'Usage_Hours']
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # --- 1. حساب مؤشر الخطر ---
    base_risk = (df['Temperature_C'] * 0.4) + (df['Vibration_Hz'] * 0.3)
    voltage_risk = abs(df['Voltage_V'] - 220) * 0.5
    helium_risk = np.where((df['Device_Type'] == 'MRI') & (df['Helium_Level'] < 60), (60 - df['Helium_Level']) * 2, 0)
    
    df['Risk_Score'] = base_risk + voltage_risk + helium_risk + (df['Usage_Hours'] / 3000)
    df['Risk_Score'] = df['Risk_Score'].clip(upper=100)

    # تحديد الحالة
    conditions = [(df['Risk_Score'] >= 75), (df['Risk_Score'] >= 50)]
    choices = ['حرج 🔴', 'تحذير 🟡']
    df['Status'] = np.select(conditions, choices, default='مستقر 🟢')
    
    # --- 2. التشخيص الذكي (تحديد السبب والنصيحة) ---
    def get_diagnosis(row):
        causes = []
        actions = []
        
        # فحص الحرارة
        if row['Temperature_C'] > 45: 
            causes.append("🔥 حرارة مرتفعة")
            actions.append("فحص المراوح ونظام التبريد")
            
        # فحص الاهتزاز
        if row['Vibration_Hz'] > 30:
            causes.append("〰️ اهتزاز عالٍ")
            actions.append("فحص رومان البلي (Bearings) وتثبيت القاعدة")
            
        # فحص الجهد
        if abs(row['Voltage_V'] - 220) > 15:
            causes.append("⚡ تذبذب جهد")
            actions.append("فحص وحدة التغذية (PSU) ومنظم الكهرباء")
            
        # فحص الهيليوم (MRI)
        if row['Device_Type'] == 'MRI' and row['Helium_Level'] < 60:
            causes.append("📉 نقص هيليوم")
            actions.append("تعبئة هيليوم فوراً وفحص التسريب")

        # فحص العمر التشغيلي
        if row['Usage_Hours'] > 8000:
            causes.append("⏳ تقادم")
            actions.append("جدولة صيانة شاملة (Overhaul)")

        # النتيجة النهائية للصف
        if not causes:
            return "أداء طبيعي", "متابعة دورية"
        
        return " + ".join(causes), " و ".join(actions)

    # تطبيق الدالة على كل صف
    diagnosis_results = df.apply(get_diagnosis, axis=1, result_type='expand')
    df['Diagnosis_Reason'] = diagnosis_results[0]
    df['Recommended_Action'] = diagnosis_results[1]
    
    # توقع وقت العطل
    df['ETTF_Days'] = np.where(df['Status'] == 'حرج 🔴', np.random.randint(1, 7, len(df)), 
                               np.random.randint(30, 365, len(df)))
    return df

# --- 3. السايد بار والفلاتر ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063823.png", width=80)
    st.title("لوحة التحكم")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📂 رفع ملف البيانات", type=['xlsx', 'csv'])
    
    st.markdown("---")
    threshold = st.slider("عتبة الخطر", 0, 100, 75)
    
    st.info("💡 ملاحظة: النظام الآن يحلل سبب العطل ويقترح طريقة الإصلاح تلقائياً.")

# --- 4. المعالجة ---
if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'): df_raw = pd.read_csv(uploaded_file)
        else: df_raw = pd.read_excel(uploaded_file)
    except: st.stop()
else:
    st.warning("⚠️ يرجى رفع ملف Excel لتشغيل التحليل.")
    st.stop()

# تشغيل التحليل الجديد
df_analyzed = analyze_and_diagnose(df_raw)

# الفلاتر الجانبية (تظهر بعد تحميل الداتا)
with st.sidebar:
    st.subheader("🔍 تصفية النتائج")
    depts = st.multiselect("القسم:", df_analyzed['Location'].unique(), default=df_analyzed['Location'].unique())
    devs = st.multiselect("الجهاز:", df_analyzed['Device_Type'].unique(), default=df_analyzed['Device_Type'].unique())

df_filtered = df_analyzed[
    (df_analyzed['Location'].isin(depts)) &
    (df_analyzed['Device_Type'].isin(devs))
]
high_risk_df = df_filtered[df_filtered['Risk_Score'] >= threshold]

# --- 5. العرض الرئيسي ---
st.title("🧠 المستشار الذكي للصيانة الطبية")
st.markdown("**تحليل الأسباب الجذرية للأعطال وتقديم توصيات الصيانة**")

# KPIs
k1, k2, k3, k4 = st.columns(4)
with k1: st.metric("إجمالي الأجهزة", len(df_filtered))
with k2: st.metric("حالة حرجة", len(high_risk_df), delta_color="inverse")
with k3: st.metric("متوسط الحرارة", f"{df_filtered['Temperature_C'].mean():.1f}°C")
with k4: st.metric("أكثر سبب للأعطال", high_risk_df['Diagnosis_Reason'].mode()[0] if not high_risk_df.empty else "-")

st.markdown("---")

# --- 6. الرسوم البيانية ---
c1, c2 = st.columns([1, 1])
with c1:
    st.subheader("📊 أسباب المخاطر الأكثر شيوعاً")
    if not high_risk_df.empty:
        # نفصل الأسباب إذا كان هناك أكثر من سبب
        reasons_series = high_risk_df['Diagnosis_Reason'].str.split(' \+ ').explode()
        fig_reason = px.pie(names=reasons_series.value_counts().index, values=reasons_series.value_counts().values, donut=0.4)
        fig_reason.update_layout(font_family="Tajawal")
        st.plotly_chart(fig_reason, use_container_width=True)
    else:
        st.info("لا توجد مخاطر حالية لعرض أسبابها.")

with c2:
    st.subheader("🌡️ الحرارة vs الاهتزاز (مع تحديد الخطر)")
    fig_sc = px.scatter(df_filtered, x='Temperature_C', y='Vibration_Hz', color='Status', 
                        hover_data=['Device_Type', 'Diagnosis_Reason'], size='Risk_Score',
                        color_discrete_map={'حرج 🔴': '#ef4444', 'تحذير 🟡': '#f59e0b', 'مستقر 🟢': '#10b981'})
    fig_sc.update_layout(font_family="Tajawal")
    st.plotly_chart(fig_sc, use_container_width=True)

# --- 7. جدول "خطة العمل" (Action Plan) ---
st.subheader("🛠️ خطة الصيانة المقترحة (Action Plan)")
st.markdown("قائمة بالأجهزة التي تتطلب تدخلاً، مع **سبب المشكلة** و **الحل المقترح**:")

if not high_risk_df.empty:
    # إعداد الجدول للعرض
    display_df = high_risk_df[['Device_ID', 'Location', 'Status', 'Risk_Score', 'Diagnosis_Reason', 'Recommended_Action']]
    
    # دالة تلوين
    def highlight_row(row):
        return ['background-color: #fee2e2; color: black'] * len(row) if row['Risk_Score'] > 75 else [''] * len(row)

    st.dataframe(
        display_df.style.apply(highlight_row, axis=1)
        .format({'Risk_Score': '{:.1f}'}),
        use_container_width=True
    )
else:
    st.success("🎉 النظام سليم تماماً! لا توجد إجراءات صيانة مطلوبة.")

# --- 8. التصدير ---
st.markdown("### 📥 تحميل تقرير الصيانة الفني")
st.download_button(
    label="تحميل ملف التوصيات (Excel)",
    data=df_analyzed.to_csv(index=False).encode('utf-8-sig'),
    file_name='Smart_Maintenance_Plan.csv',
    mime='text/csv'
)
