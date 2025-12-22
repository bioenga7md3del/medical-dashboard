import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="منصة إدارة الأجهزة الطبية",
    page_icon="🏥",
    layout="wide"
)

# تنسيق CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    h1, h2, h3 { text-align: right; color: #0f172a; }
    .stMetric { background-color: #fff; border: 1px solid #e2e8f0; border-radius: 8px; text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك الذكاء الاصطناعي (التشخيص) ---
def analyze_data(df):
    # تحويل البيانات
    for col in ['Temperature_C', 'Vibration_Hz', 'Voltage_V', 'Helium_Level', 'Usage_Hours']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # حساب المخاطر (Logic)
    def calculate_row_risk(row):
        score = 0
        reasons = []
        actions = []

        # 1. منطق الرنين (MRI)
        if row['Device_Type'] == 'MRI':
            if row['Helium_Level'] < 50:
                score += 50
                reasons.append("نقص حاد في الهيليوم")
                actions.append("تعبئة Quench Pipe / فحص التسريب")
            elif row['Helium_Level'] < 70:
                score += 20
                reasons.append("مستوى هيليوم منخفض")
                actions.append("جدولة تعبئة")
            if row['Temperature_C'] > 24:
                score += 30
                reasons.append("حرارة الغرفة مرتفعة")
                actions.append("فحص تكييف غرفة الرنين")

        # 2. منطق المقطعية (CT)
        elif row['Device_Type'] == 'CT Scan':
            if row['Temperature_C'] > 80:
                score += 40
                reasons.append("حرارة الأنبوب (Tube) حرجة")
                actions.append("إيقاف الجهاز للتبريد فوراً")
            if row['Vibration_Hz'] > 50:
                score += 40
                reasons.append("اهتزاز القنطرة (Gantry)")
                actions.append("فحص التوازن والمحامل")

        # 3. منطق الفلورو (Fluoro)
        elif row['Device_Type'] == 'Fluoroscopy':
            if abs(row['Voltage_V'] - 220) > 15:
                score += 45
                reasons.append("تذبذب كهرباء (Power)")
                actions.append("فحص الـ UPS ومنظم الجهد")

        # 4. منطق الإكس راي (X-Ray)
        elif row['Device_Type'] == 'X-Ray':
            if row['Usage_Hours'] > 20000:
                score += 30
                reasons.append("انتهاء العمر الافتراضي للأنبوب")
                actions.append("خطط لاستبدال الـ Tube")

        # تقييم عام للكل
        if score == 0 and row['Usage_Hours'] > 10000:
            score += 15
            reasons.append("تقادم عام")
            actions.append("صيانة وقائية")

        # تحديد الحالة النهائية
        risk_label = "مستقر 🟢"
        if score >= 60: risk_label = "حرج 🔴"
        elif score >= 30: risk_label = "تحذير 🟡"

        return pd.Series([score, risk_label, " + ".join(reasons), " + ".join(actions)])

    df[['Risk_Score', 'Status', 'Diagnosis', 'Action']] = df.apply(calculate_row_risk, axis=1)
    return df

# --- 3. الواجهة الجانبية ---
with st.sidebar:
    st.title("⚙️ الإعدادات")
    uploaded_file = st.file_uploader("ارفع ملف البيانات (Specialized Excel)", type=['xlsx'])
    st.info("قم برفع ملف: Specialized_Medical_Data.xlsx")

# --- 4. العرض الرئيسي ---
st.title("مركز القيادة الموحد للأجهزة الطبية")

if uploaded_file:
    df_raw = pd.read_excel(uploaded_file)
    df = analyze_data(df_raw)
    
    # تقسيم الشاشة لـ 4 تبويبات
    tab1, tab2, tab3, tab4 = st.tabs(["🧲 الرنين (MRI)", "☢️ المقطعية (CT)", "📺 الفلورسكوبي (Fluoro)", "🦴 الأشعة (X-Ray)"])

    # ------------------ TAB 1: MRI ------------------
    with tab1:
        st.header("لوحة مراقبة الرنين المغناطيسي")
        mri_df = df[df['Device_Type'] == 'MRI']
        
        # مؤشرات خاصة بالرنين
        c1, c2, c3 = st.columns(3)
        c1.metric("عدد أجهزة الرنين", len(mri_df))
        c2.metric("متوسط مستوى الهيليوم", f"{mri_df['Helium_Level'].mean():.1f}%")
        critical_mri = len(mri_df[mri_df['Status'] == 'حرج 🔴'])
        c3.metric("تنبيهات حرجة", critical_mri, delta_color="inverse")
        
        col_chart, col_table = st.columns([1, 2])
        with col_chart:
            st.subheader("مستويات الهيليوم")
            fig = px.bar(mri_df, x='Device_ID', y='Helium_Level', color='Status', 
                         title="مراقبة الهيليوم (الحد الأدنى 60%)",
                         color_discrete_map={'حرج 🔴':'#ef4444', 'تحذير 🟡':'#f59e0b', 'مستقر 🟢':'#10b981'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col_table:
            st.subheader("الأجهزة التي تحتاج تعبئة")
            st.dataframe(mri_df[mri_df['Risk_Score']>0][['Device_ID', 'Location', 'Helium_Level', 'Action']], use_container_width=True)

    # ------------------ TAB 2: CT Scan ------------------
    with tab2:
        st.header("لوحة مراقبة الأشعة المقطعية")
        ct_df = df[df['Device_Type'] == 'CT Scan']
        
        c1, c2, c3 = st.columns(3)
        c1.metric("عدد أجهزة CT", len(ct_df))
        c2.metric("متوسط حرارة الأنبوب", f"{ct_df['Temperature_C'].mean():.1f}°C")
        c3.metric("متوسط الاهتزاز", f"{ct_df['Vibration_Hz'].mean():.1f} Hz")
        
        # رسم علاقة الحرارة بالاهتزاز (مهم جداً للمقطعية)
        st.subheader("تحليل العلاقة: الحرارة vs الاهتزاز")
        fig_ct = px.scatter(ct_df, x='Temperature_C', y='Vibration_Hz', color='Status', size='Risk_Score',
                            hover_data=['Device_ID', 'Diagnosis'],
                            color_discrete_map={'حرج 🔴':'#ef4444', 'تحذير 🟡':'#f59e0b', 'مستقر 🟢':'#10b981'})
        st.plotly_chart(fig_ct, use_container_width=True)
        
        st.error(f"يوجد {len(ct_df[ct_df['Status']=='حرج 🔴'])} أجهزة مقطعية في حالة حرجة تتطلب إيقاف التشغيل!")

    # ------------------ TAB 3: Fluoroscopy ------------------
    with tab3:
        st.header("لوحة مراقبة الفلورسكوبي")
        fl_df = df[df['Device_Type'] == 'Fluoroscopy']
        
        # التركيز هنا على الكهرباء
        c1, c2 = st.columns(2)
        c1.metric("عدد الأجهزة", len(fl_df))
        c2.metric("استقرار الجهد الكهربائي", f"{fl_df['Voltage_V'].mean():.1f} V")
        
        st.subheader("مراقبة استقرار التيار الكهربائي")
        # رسم خطي للجهد
        fig_fl = px.line(fl_df, x='Device_ID', y='Voltage_V', markers=True, title="الجهد الكهربائي (المثالي 220 فولت)")
        fig_fl.add_hline(y=220, line_dash="dash", line_color="green")
        fig_fl.add_hline(y=235, line_dash="dot", line_color="red")
        fig_fl.add_hline(y=205, line_dash="dot", line_color="red")
        st.plotly_chart(fig_fl, use_container_width=True)

    # ------------------ TAB 4: X-Ray ------------------
    with tab4:
        st.header("لوحة مراقبة الأشعة السينية")
        xr_df = df[df['Device_Type'] == 'X-Ray']
        
        c1, c2 = st.columns(2)
        c1.metric("عدد الأجهزة", len(xr_df))
        c2.metric("الأجهزة القديمة (>20k ساعة)", len(xr_df[xr_df['Usage_Hours']>20000]))
        
        st.subheader("حالة الأجهزة وتوصيات الاستبدال")
        # فلتر للأجهزة القديمة فقط
        old_devices = xr_df[xr_df['Usage_Hours'] > 15000]
        if not old_devices.empty:
            st.dataframe(old_devices[['Device_ID', 'Location', 'Usage_Hours', 'Action']], use_container_width=True)
        else:
            st.success("جميع أجهزة الأشعة حديثة وبحالة جيدة.")

else:
    st.warning("الرجاء رفع ملف البيانات للبدء...")
