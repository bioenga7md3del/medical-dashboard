import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="نظام التنبؤ الذكي بالأعطال", layout="wide", page_icon="🏥")

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700;800&display=swap');
* { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
h1, h2, h3 { color: #0f172a; }
.risk-card {
    padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #ddd;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
}
.critical { background-color: #fee2e2; border-right: 5px solid #ef4444; color: #7f1d1d; }
.warning { background-color: #fffbeb; border-right: 5px solid #f59e0b; color: #92400e; }
.safe { background-color: #f0fdf4; border-right: 5px solid #22c55e; color: #166534; }
</style>
""", unsafe_allow_html=True)

# --- 2. محرك التنبؤ وتصنيف الحالة ---
def predict_faults(df, device_type):
    alerts = []
    
    for index, row in df.iterrows():
        device_id = row['Device_ID']
        risk_score = 0
        reasons = []
        status_label = "سليمة 🟢"
        status_cat = "Safe" # للفلترة
        action = "لا يوجد إجراء مطلوب"
        css_class = "safe"

        # ================== منطق الرنين (MRI) ==================
        if device_type == 'MRI':
            if row['Helium_Level'] < 40:
                risk_score += 50
                reasons.append(f"مستوى الهيليوم حرج جداً ({row['Helium_Level']:.1f}%)")
                action = "تعبئة طارئة وفحص التنفيس"
            elif row['Helium_Level'] < 60:
                risk_score += 20
                reasons.append("انخفاض الهيليوم")
                action = "جدولة تعبئة"
            
            if row['Chiller_Temp'] > 20:
                risk_score += 30
                reasons.append(f"فشل تبريد الشيلر ({row['Chiller_Temp']:.1f}°C)")

        # ================== منطق المقطعية (CT) ==================
        elif device_type == 'CT':
            if row['Gantry_Temp'] > 85:
                risk_score += 50
                reasons.append(f"حرارة الجانتري خطرة ({row['Gantry_Temp']:.1f}°C)")
                action = "إيقاف للتبريد فوراً"
            elif row['Gantry_Temp'] > 60:
                risk_score += 20
                reasons.append("ارتفاع حرارة الجانتري")

            if abs(row['Gantry_Voltage'] - 220) > 20:
                risk_score += 30
                reasons.append("تذبذب كهرباء شديد")
                action = "فحص Stabilizer"

        # ================== منطق الفلورو (Fluoro) ==================
        elif device_type == 'Fluoro':
            if row['Voltage_V'] < 190 or row['Voltage_V'] > 250:
                risk_score += 40
                reasons.append("جهد كهربائي غير مستقر")
                action = "فحص وحدة التغذية (PSU)"
            if row['Humidity'] > 75:
                risk_score += 15
                reasons.append("رطوبة عالية (خطر كهربائي)")

        # ================== منطق الأشعة (XRay) ==================
        elif device_type == 'XRay':
            if row['Tube_Temp'] > 55:
                risk_score += 45
                reasons.append(f"حرارة الأنبوب ({row['Tube_Temp']:.1f}°C)")
                action = "استبدال الزيت / تبريد"
            if row['Usage_Hours'] > 25000:
                risk_score += 25
                reasons.append("تجاوز العمر الافتراضي")
                action = "خطة إحلال"

        # --- التصنيف النهائي بناءً على النقاط ---
        if risk_score >= 50:
            status_label = "توقف وشيك / خطر 🔴"
            status_cat = "Critical"
            css_class = "critical"
        elif risk_score >= 20:
            status_label = "تعمل ولكن حرجة 🟡"
            status_cat = "Warning"
            css_class = "warning"
        else:
            status_label = "تعمل بكفاءة (سليمة) 🟢"
            status_cat = "Safe"
            css_class = "safe"
            reasons.append("الأداء ضمن المعدلات الطبيعية")

        alerts.append({
            "Device_ID": device_id,
            "Status_Label": status_label,   # للعرض
            "Status_Category": status_cat,  # للفلترة
            "Reasons": " + ".join(reasons),
            "Action": action,
            "Risk_Score": risk_score,
            "Class": css_class,
            "Data_Row": row # نحتفظ بالبيانات للرسم
        })

    return pd.DataFrame(alerts)

# --- 3. دالة رسم مؤشر الموقع (Gauge) ---
def plot_site_health(all_data):
    # حساب نسبة الصحة العامة: (عدد الأجهزة السليمة / العدد الكلي) * 100
    total = len(all_data)
    safe = len(all_data[all_data['Status_Category'] == 'Safe'])
    score = (safe / total) * 100 if total > 0 else 0
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        title = {'text': "مؤشر الجاهزية العامة للموقع"},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#22c55e"}, # أخضر
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#fee2e2'}, # أحمر فاتح
                {'range': [50, 80], 'color': '#fef3c7'}, # أصفر فاتح
                {'range': [80, 100], 'color': '#dcfce7'}], # أخضر فاتح
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90}}))
    
    fig.update_layout(height=250, margin=dict(l=20,r=20,t=40,b=20))
    return fig

# --- 4. الواجهة الجانبية (Filters) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063823.png", width=70)
    st.title("لوحة التحكم")
    uploaded_file = st.file_uploader("📂 رفع البيانات (Smart_Medical_Data.xlsx)", type=['xlsx'])
    
    st.markdown("---")
    st.subheader("🔍 تصفية حسب الحالة")
    
    # خيارات الفلتر
    filter_options = {
        "Critical": "🔴 توقف وشيك (خطر)",
        "Warning": "🟡 تعمل ولكن حرجة",
        "Safe": "🟢 تعمل بكفاءة (سليمة)"
    }
    
    selected_filters = st.multiselect(
        "اعرض الأجهزة:",
        options=list(filter_options.keys()),
        format_func=lambda x: filter_options[x],
        default=["Critical", "Warning", "Safe"] # الافتراضي الكل
    )
    
    st.info("قم بإلغاء تحديد 'سليمة' للتركيز فقط على الأعطال.")

# --- 5. التطبيق الرئيسي ---
st.title("🏥 مركز القيادة الموحد للأجهزة الطبية")

if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        # تجميع كل البيانات لحساب المؤشر العام
        full_report = pd.DataFrame()
        
        # معالجة كل الأنواع أولاً
        processed_data = {}
        for dtype in ['MRI', 'CT', 'Fluoro', 'XRay']:
            raw_df = pd.read_excel(xls, dtype)
            analyzed_df = predict_faults(raw_df, dtype)
            processed_data[dtype] = analyzed_df
            full_report = pd.concat([full_report, analyzed_df])

        # 1. عرض مؤشر الموقع (Gauge)
        st.plotly_chart(plot_site_health(full_report), use_container_width=True)

        # 2. التبويبات
        tab1, tab2, tab3, tab4 = st.tabs(["🧲 الرنين (MRI)", "☢️ المقطعية (CT)", "📺 الفلورسكوبي", "🦴 الأشعة (X-Ray)"])
        
        # دالة العرض المتكررة
        def display_tab_content(device_type):
            df_curr = processed_data[device_type]
            
            # تطبيق الفلتر
            df_filtered = df_curr[df_curr['Status_Category'].isin(selected_filters)]
            
            # إحصائيات سريعة للنوع
            col1, col2, col3 = st.columns(3)
            col1.metric("إجمالي المعروض", len(df_filtered))
            col2.metric("الحرجة جداً", len(df_curr[df_curr['Status_Category']=='Critical']), delta_color="inverse")
            col3.metric("السليمة", len(df_curr[df_curr['Status_Category']=='Safe']))
            
            st.markdown("---")
            
            if df_filtered.empty:
                st.info("لا توجد أجهزة تطابق الفلتر المختار.")
            else:
                # عرض الكروت
                for i, row in df_filtered.iterrows():
                    st.markdown(f"""
                    <div class="risk-card {row['Class']}">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h3 style="margin:0;">{row['Device_ID']}</h3>
                            <span style="font-size:0.9em; font-weight:bold;">{row['Status_Label']}</span>
                        </div>
                        <hr style="margin: 8px 0; border-color: #eee;">
                        <div style="display:flex; justify-content:space-between;">
                            <div><b>🔍 السبب:</b> {row['Reasons']}</div>
                            <div><b>🛠️ الإجراء:</b> {row['Action']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        with tab1: display_tab_content('MRI')
        with tab2: display_tab_content('CT')
        with tab3: display_tab_content('Fluoro')
        with tab4: display_tab_content('XRay')

    except Exception as e:
        st.error(f"حدث خطأ: {e}")
        st.warning("تأكد من رفع ملف Smart_Medical_Data.xlsx الصحيح.")

else:
    st.info("الرجاء رفع ملف البيانات للبدء.")
