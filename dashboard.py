import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="التحليل المترابط للأجهزة الطبية", layout="wide", page_icon="📈")

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700&display=swap');
* { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
h1, h2, h3 { color: #1e3a8a; }
.stMetric { background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- 2. دوال التحليل المساعدة ---

# رسم مصفوفة الترابط (Correlation Heatmap)
def plot_correlation(df, title):
    # نحسب الترابط فقط للأعمدة الرقمية
    corr = df.select_dtypes(include=[np.number]).corr()
    fig = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r', 
                    title=f"مصفوفة الترابط: {title}")
    return fig

# --- 3. الواجهة الجانبية ---
with st.sidebar:
    st.title("📂 البيانات")
    uploaded_file = st.file_uploader("ارفع ملف Smart_Medical_Data.xlsx", type=['xlsx'])
    st.info("يجب أن يحتوي الملف على صفحات: MRI, CT, Fluoro, XRay")

# --- 4. العرض الرئيسي ---
st.title("📊 منصة التحليل العميق للأجهزة الطبية")

if uploaded_file:
    # قراءة كل صفحة على حدة
    try:
        xls = pd.ExcelFile(uploaded_file)
        df_mri = pd.read_excel(xls, 'MRI')
        df_ct = pd.read_excel(xls, 'CT')
        df_fl = pd.read_excel(xls, 'Fluoro')
        df_xr = pd.read_excel(xls, 'XRay')
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
        st.stop()

    # التبويبات
    tab1, tab2, tab3, tab4 = st.tabs(["🧲 الرنين (MRI)", "☢️ المقطعية (CT)", "📺 الفلورسكوبي", "🦴 الأشعة (X-Ray)"])

    # ==========================
    # 1. تحليل الرنين (MRI)
    # ==========================
    with tab1:
        st.header("تحليل علاقات الرنين المغناطيسي")
        
        # KPIs
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("متوسط حرارة الشيلر", f"{df_mri['Chiller_Temp'].mean():.1f}°C")
        c2.metric("متوسط الهيليوم", f"{df_mri['Helium_Level'].mean():.1f}%")
        c3.metric("معدل الحالات اليومي", f"{df_mri['Daily_Cases'].mean():.0f}")
        c4.metric("حرارة الغرفة", f"{df_mri['Room_Temp'].mean():.1f}°C")

        # الرسم البياني المركب (3 متغيرات)
        st.subheader("تحليل: كيف تؤثر حرارة الغرفة والتشغيل على الشيلر؟")
        # X=ساعات التشغيل, Y=حرارة الشيلر, اللون=حرارة الغرفة, الحجم=عدد الحالات
        fig_bub = px.scatter(df_mri, x="Continuous_Hours", y="Chiller_Temp", 
                             size="Daily_Cases", color="Room_Temp",
                             hover_name="Device_ID", title="كل نقطة تمثل قراءة يومية",
                             labels={"Continuous_Hours": "ساعات التشغيل", "Chiller_Temp": "حرارة الشيلر"},
                             color_continuous_scale="tropic")
        st.plotly_chart(fig_bub, use_container_width=True)

        # مصفوفة الترابط
        st.subheader("كشف العلاقات الخفية (Correlation)")
        st.write("اللون الأحمر الغامق يعني علاقة طردية قوية، الأزرق يعني عكسية.")
        st.plotly_chart(plot_correlation(df_mri, "متغيرات MRI"), use_container_width=True)
        
        # تحليل الهيليوم
        st.subheader("تنبؤ الخطر: الهيليوم vs الشيلر")
        fig_line = px.line(df_mri, y="Helium_Level", x="Chiller_Temp", title="هل انخفاض الهيليوم مرتبط بارتفاع حرارة الشيلر؟")
        st.plotly_chart(fig_line, use_container_width=True)

    # ==========================
    # 2. تحليل المقطعية (CT)
    # ==========================
    with tab2:
        st.header("تحليل علاقات الأشعة المقطعية")

        c1, c2, c3 = st.columns(3)
        c1.metric("حرارة الجانتري القصوى", f"{df_ct['Gantry_Temp'].max():.1f}°C")
        c2.metric("استقرار الفولتية (SD)", f"{df_ct['Gantry_Voltage'].std():.2f}")
        c3.metric("ساعات التشغيل المتواصل", f"{df_ct['Continuous_Hours'].mean():.1f} h")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("تأثير ضغط العمل على حرارة الجانتري")
            # X=عدد الحالات, Y=حرارة الجانتري, اللون=حرارة الغرفة
            fig_ct1 = px.scatter(df_ct, x="Daily_Cases", y="Gantry_Temp", color="Room_Temp",
                                 title="هل تزداد حرارة الجانتري مع زيادة الحالات؟",
                                 labels={"Daily_Cases": "عدد الحالات", "Gantry_Temp": "حرارة الجانتري"})
            st.plotly_chart(fig_ct1, use_container_width=True)
        
        with col2:
             st.subheader("استقرار الكهرباء تحت الضغط")
             fig_ct2 = px.scatter(df_ct, x="Continuous_Hours", y="Gantry_Voltage", color="Gantry_Temp",
                                  title="هل يتذبذب الفولت مع طول فترة التشغيل؟")
             fig_ct2.add_hline(y=220, line_dash="dash", line_color="green")
             st.plotly_chart(fig_ct2, use_container_width=True)

        st.plotly_chart(plot_correlation(df_ct, "متغيرات CT Scan"), use_container_width=True)

    # ==========================
    # 3. تحليل الفلورسكوبي
    # ==========================
    with tab3:
        st.header("تحليل الفلورسكوبي")
        # التركيز على الكهرباء والرطوبة
        st.subheader("تأثير الرطوبة على الدوائر الكهربائية")
        
        fig_fl = px.scatter_3d(df_fl, x='Humidity', y='Voltage_V', z='Tube_Temp',
                               color='Daily_Cases', opacity=0.7,
                               title="تحليل ثلاثي الأبعاد: الرطوبة - الفولت - الحرارة")
        fig_fl.update_layout(margin=dict(l=0, r=0, b=0, t=0))
        st.plotly_chart(fig_fl, use_container_width=True)
        
        st.plotly_chart(plot_correlation(df_fl, "Fluoro"), use_container_width=True)

    # ==========================
    # 4. تحليل الأشعة (X-Ray)
    # ==========================
    with tab4:
        st.header("تحليل الأشعة السينية")
        
        # ربط حرارة التيوب بعدد الحالات
        st.subheader("كفاءة التبريد: حرارة الأنبوب vs وقت الراحة")
        # نفترض أن الساعات القليلة تعني وقت راحة أكبر
        fig_xr = px.area(df_xr, x="Continuous_Hours", y="Tube_Temp", 
                         title="تراكم الحرارة مع استمرار التشغيل")
        st.plotly_chart(fig_xr, use_container_width=True)
        
        st.write("جدول الحالات الحرجة (حرارة > 40 أو فولتية غير مستقرة):")
        critical_xr = df_xr[(df_xr['Tube_Temp'] > 40) | (abs(df_xr['Voltage_V'] - 220) > 15)]
        st.dataframe(critical_xr, use_container_width=True)

else:
    st.info("الرجاء تشغيل ملف generate_smart_data.py أولاً لإنشاء البيانات، ثم رفع الملف الناتج هنا.")
