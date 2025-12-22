import pandas as pd
import numpy as np
import datetime

# إعدادات البيانات العشوائية ولكن بمنطق واقعي
np.random.seed(42) # لضمان ثبات النتائج
num_records = 200 # عدد الأجهزة

# القوائم الأساسية
departments = ['الطوارئ', 'العناية المركزة (ICU)', 'العمليات', 'الأشعة', 'العيادات الخارجية', 'المختبر']
device_types = ['MRI', 'CT Scan', 'X-Ray', 'Ventilator', 'Patient Monitor', 'Ultrasound', 'Anesthesia Machine']

# توليد البيانات
data = {
    'Device_ID': [f'DEV-{1000+i}' for i in range(num_records)],
    'Device_Type': np.random.choice(device_types, num_records),
    'Location': np.random.choice(departments, num_records),
    'Usage_Hours': np.random.randint(100, 15000, num_records),
    'Last_Maint_Date': [datetime.date(2023, 1, 1) + datetime.timedelta(days=np.random.randint(0, 365)) for _ in range(num_records)]
}

df = pd.DataFrame(data)

# إضافة البيانات الحيوية بناءً على نوع الجهاز ليكون التحليل منطقياً
# 1. الحرارة (Temperature)
def get_temp(row):
    if row['Device_Type'] == 'MRI': return np.random.uniform(18, 26) # MRI needs cooling
    if row['Device_Type'] == 'CT Scan': return np.random.uniform(20, 90) # CT gets hot
    return np.random.uniform(20, 45) # Others

# 2. الاهتزاز (Vibration)
def get_vib(row):
    if row['Device_Type'] in ['CT Scan', 'MRI']: return np.random.uniform(10, 120)
    return np.random.uniform(0, 10) # Static devices don't vibrate much

# 3. الجهد (Voltage)
def get_volt(row):
    return np.random.normal(220, 15) # Mean 220, SD 15

# 4. الهيليوم (Helium - MRI Only)
def get_helium(row):
    if row['Device_Type'] == 'MRI': return np.random.uniform(30, 100)
    return 0

# 5. الرطوبة (Humidity)
def get_humidity(row):
    return np.random.uniform(30, 70)

# تطبيق الدوال
df['Temperature_C'] = df.apply(get_temp, axis=1)
df['Vibration_Hz'] = df.apply(get_vib, axis=1)
df['Voltage_V'] = df.apply(get_volt, axis=1)
df['Helium_Level'] = df.apply(get_helium, axis=1)
df['Humidity_Percent'] = df.apply(get_humidity, axis=1)

# إضافة بعض "الأعطال المصطنعة" لكي تظهر في الداشبورد باللون الأحمر
# نختار 10 أجهزة عشوائية ونجعل حرارتها عالية جداً
random_indices = np.random.choice(df.index, 15, replace=False)
df.loc[random_indices, 'Temperature_C'] += 50
df.loc[random_indices, 'Vibration_Hz'] += 40

# حفظ الملف
file_name = 'medical_data_large.xlsx'
df.to_excel(file_name, index=False)
print(f"✅ تم إنشاء الملف بنجاح: {file_name}")
