import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def load_data(file_path):
    """تحميل البيانات من Excel"""
    df = pd.read_excel(file_path)
    return df

def perform_segmentation(df):
    """تقسيم العملاء لـ 3 مجموعات"""
    features = ['Purchases', 'Total_Value', 'Visits']
    
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(df[features])
    
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['Segment'] = kmeans.fit_predict(data_scaled)
    
    segment_names = {
        0: '🌟 مخلصون', 
        1: '📊 متوسطون', 
        2: '⚠️ معرضون للرحيل'
    }
    df['Segment_Name'] = df['Segment'].map(segment_names)
    
    return df
