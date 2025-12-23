import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="نظام التنبؤ الذكي بالأعطال", layout="wide", page_icon="⚙️")

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

# --- 2. لوحة الإعدادات (Settings Panel) ---
# نضعها في دالة لسهولة الاستدعاء
def get_user_thresholds():
    thresholds = {}
    
    with st.sidebar:
        st.title("⚙️ ضبط المعايير (Settings)")
        st.markdown("عدل القيم الحدية لإطلاق التنبيهات:")
        
        # 1. إعدادات الرنين
        with st.expander("🧲 إعدادات الرنين (MRI)", expanded=False):
            thresholds['mri_helium_crit'] = st.number_input("الحد الخطر للهيليوم (%)", value=40, step=1)
            thresholds['mri_helium_warn'] = st.number_input("الحد التحذيري للهيليوم (%)", value=60, step=1)
            thresholds['mri_chiller_max'] = st.number_input("أقصى حرارة للشيلر (°C)", value=20, step=1)
            thresholds['mri_room_max'] = st.number_input("أقصى حرارة للغرفة (°C)", value=24, step=1)

        # 2. إعدادات المقطعية
        with st.expander("☢️ إعدادات المقطعية (CT)", expanded=False):
            thresholds['ct_gantry_crit'] = st.number_input("حرارة الجانتري الخطرة (°C)", value=85, step=1)
            thresholds['ct_gantry_warn'] = st.number_input("حرارة الجانتري التحذيرية (°C)", value=60, step=1)
            thresholds['ct_volt_tol'] = st.number_input("سماحية تذبذب الجهد (±V)", value=20, step=1)

        # 3. إعدادات الفلورو
        with st.expander("📺 إعدادات الفلورو (Fluoro)", expanded=False):
            thresholds['fl_volt_min'] = st.number_input("أقل جهد مسموح (V)", value=190, step=5)
            thresholds['fl_volt_max'] = st.number_input("أعلى جهد مسموح (V)", value=250, step=5)
            thresholds['fl_humidity_max'] = st.slider("أقصى رطوبة مسموحة (%)", 0, 100, 75)

        # 4. إعدادات الأشعة
        with st.expander("🦴 إعدادات الأشعة (X-Ray)", expanded=False):
            thresholds['xr_tube_max'] = st.number_input("أقصى حرارة للأنبوب (°C)", value=55, step=1)
            thresholds['xr_life_hours'] = st.number_input("العمر الافتراضي (ساعة)", value=25000, step=1000)

    return thresholds

# --- 3. محرك التنبؤ (يستقبل الإعدادات الآن) ---
def predict_faults(df, device_type, limits):
    alerts = []
    
    for index, row in df.iterrows():
        device_id = row['Device_ID']
        risk_score = 0
        reasons = []
        status_label = "سليمة 🟢"
        status_cat = "Safe"
        action = "لا يوجد إجراء مطلوب"
        css_class = "safe"

        # ================== منطق الرنين (MRI) ==================
        if device_type == 'MRI':
            if row['Helium_Level'] < limits['mri_helium_crit']:
                risk_score += 50
                reasons.append(f"هيليوم حرج (<{limits['mri_helium_crit']}%)")
                action = "تعبئة طارئة وفحص التنفيس"
            elif row['Helium_Level'] < limits['mri_helium_warn']:
                risk_score += 20
                reasons.append("انخفاض هيليوم")
                action = "جدولة تعبئة"
            
            if row['Chiller_Temp'] > limits['mri_chiller_max']:
                risk_score += 30
                reasons.append(f"حرارة شيلر مرتفعة (>{limits['mri_chiller_max']}°C)")
            
            if row['Room_Temp'] > limits['mri_room_max']:
                risk_score += 15
                reasons.append("حرارة الغرفة مرتفعة")

        # ================== منطق المقطعية (CT) ==================
        elif device_type == 'CT':
            if row['Gantry_Temp'] > limits['ct_gantry_crit']:
                risk_score += 50
                reasons.append(f"حرارة جانتري خطرة (>{limits['ct_gantry_crit']}°C)")
                action = "إيقاف للتبريد فوراً"
            elif row['Gantry_Temp'] > limits['ct_gantry_warn']:
                risk_score += 20
                reasons.append("ارتفاع حرارة الجانتري")

            if abs(row['Gantry_Voltage'] - 220) > limits['ct_volt_tol']:
                risk_score += 30
                reasons.append("تذبذب كهرباء شديد")
                action = "فحص Stabilizer"

        # ================== منطق الفلورو (Fluoro) ==================
        elif device_type == 'Fluoro':
            if row['Voltage_V'] < limits['fl_volt_min'] or row['Voltage_V'] > limits['fl_volt_max']:
                risk_score += 40
                reasons.append("جهد كهربائي خارج النطاق")
                action = "فحص وحدة التغذية (PSU)"
            if row['Humidity'] > limits['fl_humidity_max']:
                risk_score += 15
                reasons.append(f"رطوبة عالية (>{limits['fl_humidity_max']}%)")

        # ================== منطق الأشعة (XRay) ==================
        elif device_type == 'XRay':
            if row['Tube_Temp'] > limits['xr_tube_max']:
                risk_score += 45
                reasons.append(f"حرارة الأنبوب مرتفعة (>{limits['xr_tube_max']}°C)")
                action = "استبدال الزيت / تبريد"
            if row['Usage_Hours'] > limits['xr_life_hours']:
                risk_score += 25
                reasons.append("تجاوز العمر الافتراضي")
                action = "خطة إحلال"

        # --- التصنيف النهائي ---
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
            "Status_Label": status_label,
            "Status_Category": status_cat,
            "Reasons": " + ".join(reasons),
            "Action": action,
            "Risk_Score": risk_score,
            "Class": css_class
        })

    return pd.DataFrame(alerts)

# --- 4. دالة الرسم (Gauge) ---
def plot_site_health(all_data):
    total = len(all_data)
    safe = len(all_data[all_data['Status_Category'] == 'Safe'])
    score = (safe / total) * 100 if total > 0 else 0
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        title = {'text': "مؤشر الجاهزية العامة للموقع"},
        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#22c55e"},
                 'steps': [{'range': [0, 50], 'color': '#fee2e2'}, {'range': [50, 80], 'color': '#fef3c7'}, {'range': [80, 100], 'color': '#dcfce7'}]}))
    fig.update_layout(height=250, margin=dict(l=20,r=20,t=40,b=20))
    return fig

# --- 5. التطبيق الرئيسي ---
# استدعاء الإعدادات أولاً
user_limits = get_user_thresholds()

st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("📂 رفع البيانات (Excel)", type=['xlsx'])

# فلتر العرض
filter_options = {"Critical": "🔴 خطر", "Warning": "🟡 تحذير", "Safe": "🟢 سليم"}
selected_filters = st.sidebar.multiselect("تصفية العرض:", list(filter_options.keys()), default=["Critical", "Warning", "Safe"], format_func=lambda x: filter_options[x])

st.title("🏥 مركز القيادة الموحد (مع ضبط المعايير)")

if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        full_report = pd.DataFrame()
        processed_data = {}
        
        # معالجة البيانات مع تمرير الإعدادات (user_limits)
        for dtype in ['MRI', 'CT', 'Fluoro', 'XRay']:
            raw_df = pd.read_excel(xls, dtype)
            analyzed_df = predict_faults(raw_df, dtype, user_limits) # 👈 تمرير الإعدادات هنا
            processed_data[dtype] = analyzed_df
            full_report = pd.concat([full_report, analyzed_df])

        st.plotly_chart(plot_site_health(full_report), use_container_width=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["🧲 الرنين", "☢️ المقطعية", "📺 الفلورو", "🦴 الأشعة"])
        
        def display_tab(dtype):
            df = processed_data[dtype]
            df_filt = df[df['Status_Category'].isin(selected_filters)]
            
            c1, c2, c3 = st.columns(3)
            c1.metric("العدد الكلي", len(df_filt))
            c2.metric("الحرجة", len(processed_data[dtype][processed_data[dtype]['Status_Category']=='Critical']), delta_color="inverse")
            
            st.markdown("---")
            if df_filt.empty: st.info("لا توجد نتائج.")
            else:
                for i, row in df_filt.iterrows():
                    st.markdown(f"""
                    <div class="risk-card {row['Class']}">
                        <div style="display:flex; justify-content:space-between;">
                            <h3>{row['Device_ID']}</h3>
                            <b>{row['Status_Label']}</b>
                        </div>
                        <hr style="margin:5px 0; border-color:#eee">
                        <p><b>السبب:</b> {row['Reasons']}</p>
                        <p><b>الإجراء:</b> {row['Action']}</p>
                    </div>""", unsafe_allow_html=True)

        with tab1: display_tab('MRI')
        with tab2: display_tab('CT')
        with tab3: display_tab('Fluoro')
        with tab4: display_tab('XRay')

    except Exception as e: st.error(f"خطأ: {e}")
else:
    st.info("الرجاء رفع ملف البيانات.")
