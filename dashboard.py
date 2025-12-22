import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="نظام التنبؤ الذكي بالأعطال", layout="wide", page_icon="🚨")

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;800&display=swap');
* { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
h1, h2, h3 { color: #0f172a; }
.risk-card {
    padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #ddd;
}
.critical { background-color: #fee2e2; border-left: 5px solid #ef4444; color: #7f1d1d; }
.warning { background-color: #fef3c7; border-left: 5px solid #f59e0b; color: #78350f; }
.safe { background-color: #dcfce7; border-left: 5px solid #22c55e; color: #14532d; }
</style>
""", unsafe_allow_html=True)

# --- 2. محرك التنبؤ المنطقي (The Brain) ---
def predict_faults(df, device_type):
    alerts = []
    
    for index, row in df.iterrows():
        device_id = row['Device_ID']
        risk_score = 0
        reasons = []
        status = "آمن"
        action = "متابعة روتينية"

        # ================== منطق الرنين (MRI) ==================
        if device_type == 'MRI':
            # 1. الهيليوم (أخطر عامل)
            if row['Helium_Level'] < 40:
                risk_score += 50
                reasons.append(f"مستوى الهيليوم حرج ({row['Helium_Level']:.1f}%)")
                action = "تعبئة طارئة وفحص التنفيس"
            elif row['Helium_Level'] < 60:
                risk_score += 20
                reasons.append("انخفاض الهيليوم")
            
            # 2. الشيلر وحرارة الغرفة (علاقة مترابطة)
            if row['Chiller_Temp'] > 20:
                risk_score += 30
                reasons.append(f"فشل تبريد الشيلر ({row['Chiller_Temp']:.1f}°C)")
            if row['Room_Temp'] > 24:
                risk_score += 15
                reasons.append("حرارة الغرفة مرتفعة")

        # ================== منطق المقطعية (CT) ==================
        elif device_type == 'CT':
            # 1. حرارة الجانتري (مرتبطة بالضغط)
            if row['Gantry_Temp'] > 40:
                risk_score += 40
                reasons.append(f"سخونة الجانتري ({row['Gantry_Temp']:.1f}°C)")
                action = "إيقاف للتبريد فوراً"
            
            # 2. استقرار الكهرباء
            if abs(row['Gantry_Voltage'] - 220) > 15:
                risk_score += 30
                reasons.append("تذبذب الفولتية")
                action = "فحص منظم الجهد (Stabilizer)"
                
            # 3. ضغط العمل
            if row['Continuous_Hours'] > 20:
                risk_score += 10
                reasons.append("تشغيل متواصل > 20 ساعة")

        # ================== منطق الفلورو (Fluoro) ==================
        elif device_type == 'Fluoro':
            # الرطوبة والكهرباء (خطر الشورت)
            if row['Humidity'] > 70:
                risk_score += 25
                reasons.append(f"رطوبة عالية ({row['Humidity']:.1f}%) خطر كهربائي")
            if row['Voltage_V'] < 200:
                risk_score += 35
                reasons.append("ضعف التيار الكهربائي")
                action = "فحص مزود الطاقة (PSU)"

        # ================== منطق الأشعة (XRay) ==================
        elif device_type == 'XRay':
            # حرارة التيوب
            if row['Tube_Temp'] > 50:
                risk_score += 45
                reasons.append(f"حرارة الأنبوب خطرة ({row['Tube_Temp']:.1f}°C)")
                action = "استبدال الزيت / فحص المراوح"

        # --- التصنيف النهائي ---
        if risk_score >= 50:
            status = "خطر مرتفع 🔴"
            css_class = "critical"
        elif risk_score >= 20:
            status = "تحذير 🟡"
            css_class = "warning"
        else:
            status = "مستقر 🟢"
            css_class = "safe"

        # نضيف النتيجة للقائمة إذا كان هناك خطر أو تحذير
        if risk_score > 0:
            alerts.append({
                "Device_ID": device_id,
                "Status": status,
                "Reasons": " + ".join(reasons),
                "Action": action,
                "Risk_Score": risk_score,
                "Class": css_class
            })

    return pd.DataFrame(alerts)

# --- 3. الواجهة الجانبية ---
with st.sidebar:
    st.title("📂 البيانات")
    uploaded_file = st.file_uploader("ارفع ملف Smart_Medical_Data.xlsx", type=['xlsx'])

# --- 4. العرض الرئيسي ---
st.title("🚨 مركز التنبؤ بالأعطال (Predictive Alert System)")
st.markdown("يقوم النظام بتحليل الترابط بين (الحرارة، الرطوبة، الكهرباء، وساعات العمل) لإصدار توقعات دقيقة.")

if uploaded_file:
    # قراءة الصفحات
    try:
        xls = pd.ExcelFile(uploaded_file)
        df_mri = pd.read_excel(xls, 'MRI')
        df_ct = pd.read_excel(xls, 'CT')
        df_fl = pd.read_excel(xls, 'Fluoro')
        df_xr = pd.read_excel(xls, 'XRay')
    except:
        st.error("الملف لا يحتوي على الصفحات المطلوبة (MRI, CT, Fluoro, XRay)")
        st.stop()

    # التبويبات
    tab1, tab2, tab3, tab4 = st.tabs(["🧲 الرنين (MRI)", "☢️ المقطعية (CT)", "📺 الفلورسكوبي", "🦴 الأشعة (X-Ray)"])

    # === دالة مساعدة لعرض التنبؤات ===
    def show_predictions(df, type_name):
        alerts_df = predict_faults(df, type_name)
        
        if not alerts_df.empty:
            # ترتيب حسب الخطورة
            alerts_df = alerts_df.sort_values(by='Risk_Score', ascending=False)
            
            col_kpi1, col_kpi2 = st.columns(2)
            critical_count = len(alerts_df[alerts_df['Status'].str.contains('خطر')])
            warning_count = len(alerts_df[alerts_df['Status'].str.contains('تحذير')])
            
            col_kpi1.metric("أجهزة معرضة لتوقف تام (Critical)", critical_count, delta_color="inverse")
            col_kpi2.metric("أجهزة تحتاج صيانة وقائية (Warning)", warning_count, delta_color="off")
            
            st.subheader("📋 تقرير التنبؤ التفصيلي")
            
            # عرض الكروت
            for i, row in alerts_df.iterrows():
                st.markdown(f"""
                <div class="risk-card {row['Class']}">
                    <div style="display:flex; justify-content:space-between;">
                        <h3>{row['Device_ID']}</h3>
                        <b>{row['Status']}</b>
                    </div>
                    <p><b>🔍 سبب التنبؤ بالعطل:</b> {row['Reasons']}</p>
                    <p><b>🛠️ الإجراء الاستباقي الموصى به:</b> {row['Action']}</p>
                </div>
                """, unsafe_allow_html=True)
                
        else:
            st.success("✅ جميع الأنظمة تعمل بكفاءة تامة. لا توجد مؤشرات خطر.")

    # 1. الرنين
    with tab1:
        st.header("تحليل مخاطر الرنين المغناطيسي")
        # عرض البيانات الخام كإحصائية
        c1, c2 = st.columns(2)
        c1.info(f"متوسط الهيليوم: {df_mri['Helium_Level'].mean():.1f}%")
        c2.info(f"متوسط حرارة الشيلر: {df_mri['Chiller_Temp'].mean():.1f}°C")
        st.markdown("---")
        # تشغيل التنبؤ
        show_predictions(df_mri, 'MRI')
        
        # رسم بياني توضيحي
        st.subheader("تحليل بصري للمشكلة")
        fig = px.scatter(df_mri, x='Chiller_Temp', y='Helium_Level', color='Room_Temp', 
                         size='Daily_Cases', title="علاقة تبخر الهيليوم بحرارة الشيلر")
        st.plotly_chart(fig, use_container_width=True)

    # 2. المقطعية
    with tab2:
        st.header("تحليل مخاطر الأشعة المقطعية")
        show_predictions(df_ct, 'CT')
        
        st.subheader("تحليل بصري للمشكلة")
        fig = px.scatter(df_ct, x='Gantry_Temp', y='Gantry_Voltage', color='Continuous_Hours',
                         title="تأثير التشغيل المتواصل على حرارة وكهرباء الجانتري")
        fig.add_hline(y=220, line_dash="dash", annotation_text="Ideal Voltage")
        st.plotly_chart(fig, use_container_width=True)

    # 3. الفلورو
    with tab3:
        st.header("تحليل مخاطر الفلورسكوبي")
        show_predictions(df_fl, 'Fluoro')
        
        st.subheader("تحليل بصري للمشكلة")
        fig = px.bar(df_fl, x='Device_ID', y='Voltage_V', color='Humidity',
                     title="تذبذب الكهرباء وعلاقته بالرطوبة")
        st.plotly_chart(fig, use_container_width=True)

    # 4. الأشعة
    with tab4:
        st.header("تحليل مخاطر الأشعة السينية")
        show_predictions(df_xr, 'XRay')

else:
    st.info("الرجاء رفع ملف Smart_Medical_Data.xlsx للبدء في التحليل.")
