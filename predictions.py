import pandas as pd

def calculate_churn_risk(df):
    """حساب احتمالية هجرة العميل"""
    max_purchases = df['Purchases'].max()
    min_purchases = df['Purchases'].min()
    
    df['Churn_Risk'] = (
        (max_purchases - df['Purchases']) / 
        (max_purchases - min_purchases) * 100
    ).round(2)
    
    return df

def get_recommendations(df):
    """توصيات التسويق"""
    def generate_recommendation(row):
        churn_risk = row['Churn_Risk']
        
        if churn_risk > 75:
            return "🚨 خصم 35% فوراً"
        elif churn_risk > 50:
            return "📞 اتصل + عرض 20%"
        else:
            return "✅ زود السعر"
    
    df['Action'] = df.apply(generate_recommendation, axis=1)
    return df
