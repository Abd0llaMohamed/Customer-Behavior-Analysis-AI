# database.py
import sqlite3
from datetime import datetime
import json
import streamlit as st
import struct


DB_NAME = "customer_analysis.db"


def get_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """إنشاء قاعدة البيانات والجداول"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()


    # ========== 1. جدول المستخدمين (موجود بالفعل) ==========
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            email TEXT,
            subscription TEXT DEFAULT 'free',
            subscription_date TEXT,
            usage_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            verified INTEGER DEFAULT 1,
            verification_code TEXT
        )
    """)


    # ========== 2. جدول ملخص التحليلات (جديد) ==========
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            analysis_date TEXT NOT NULL,
            total_customers INTEGER NOT NULL,
            high_risk_count INTEGER NOT NULL,
            medium_risk_count INTEGER NOT NULL,
            low_risk_count INTEGER NOT NULL,
            avg_churn_probability REAL NOT NULL,
            avg_customer_value REAL NOT NULL,
            avg_purchases REAL NOT NULL,
            revenue_at_risk REAL NOT NULL,
            predicted_future_value REAL NOT NULL,
            retention_rate REAL,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)


    # ========== 3. جدول بيانات العملاء المحللين (جديد) ==========
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyzed_customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            purchases INTEGER NOT NULL,
            total_value REAL NOT NULL,
            visits INTEGER NOT NULL,
            churn_probability_rf REAL NOT NULL,
            churn_probability_xgb REAL NOT NULL,
            churn_probability_best REAL NOT NULL,
            segment TEXT NOT NULL,
            advanced_segment TEXT NOT NULL,
            predicted_future_value REAL,
            FOREIGN KEY (analysis_id) REFERENCES analysis_summary(id)
        )
    """)


    # ========== إنشاء Indexes لتحسين الأداء ==========
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_analysis_username 
        ON analysis_summary(username)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_customers_analysis 
        ON analyzed_customers(analysis_id)
    """)


    conn.commit()
    conn.close()


# ========== دوال حفظ التحليلات ==========


def save_analysis(df, username):
    """
    حفظ نتائج التحليل الكامل
    
    Parameters:
    - df: DataFrame يحتوي على نتائج التحليل
    - username: اسم المستخدم
    
    Returns:
    - analysis_id: رقم التحليل المحفوظ
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # حساب الإحصائيات
        total_customers = len(df)
        high_risk = len(df[df['Churn_Probability'] > 70])
        medium_risk = len(df[(df['Churn_Probability'] > 30) & (df['Churn_Probability'] <= 70)])
        low_risk = len(df[df['Churn_Probability'] <= 30])
        
        avg_churn = df['Churn_Probability'].mean()
        avg_value = df['Total_Value'].mean()
        avg_purchases = df['Purchases'].mean()
        revenue_risk = df[df['Churn_Probability'] > 70]['Total_Value'].sum()
        predicted_value = df['predicted_future_value'].sum() if 'predicted_future_value' in df.columns else 0
        
        # حساب معدل الاحتفاظ
        repeat_customers = len(df[df['Purchases'] > 1])
        retention_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
        
        # 1. حفظ ملخص التحليل
        cursor.execute("""
            INSERT INTO analysis_summary 
            (username, analysis_date, total_customers, high_risk_count, 
             medium_risk_count, low_risk_count, avg_churn_probability, 
             avg_customer_value, avg_purchases, revenue_at_risk, 
             predicted_future_value, retention_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_customers,
            high_risk,
            medium_risk,
            low_risk,
            avg_churn,
            avg_value,
            avg_purchases,
            revenue_risk,
            predicted_value,
            retention_rate
        ))
        
        analysis_id = cursor.lastrowid
        
        # 2. حفظ تفاصيل كل عميل
        for _, customer in df.iterrows():
            cursor.execute("""
                INSERT INTO analyzed_customers
                (analysis_id, customer_name, purchases, total_value, 
                 visits, churn_probability_rf, churn_probability_xgb, 
                 churn_probability_best, segment, advanced_segment, 
                 predicted_future_value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id,
                customer['Name'],
                int(customer['Purchases']),
                float(customer['Total_Value']),
                int(customer['Visits']),
                float(customer['Churn_Probability_RF']),
                float(customer['Churn_Probability_XGB']),
                float(customer['Churn_Probability']),
                customer['Segment'] if 'Segment' in customer else '',
                customer['Advanced_Segment'],
                float(customer['predicted_future_value']) if 'predicted_future_value' in customer else 0
            ))
        
        conn.commit()
        return analysis_id
        
    except Exception as e:
        conn.rollback()
        st.error(f"خطأ في حفظ التحليل: {e}")
        return None
    finally:
        conn.close()


def get_user_analyses(username, limit=10):
    """
    الحصول على تاريخ التحليلات للمستخدم
    
    Parameters:
    - username: اسم المستخدم
    - limit: عدد التحليلات المطلوبة
    
    Returns:
    - list: قائمة التحليلات
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM analysis_summary
        WHERE username = ?
        ORDER BY analysis_date DESC
        LIMIT ?
    """, (username, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    def safe_float(value):
        """تحويل آمن من bytes أو أي نوع إلى float"""
        try:
            if value is None:
                return 0.0
            if isinstance(value, bytes):
                # محاولة فك تشفير bytes إلى float
                if len(value) == 4:  # float32
                    return struct.unpack('f', value)[0]
                elif len(value) == 8:  # float64
                    return struct.unpack('d', value)[0]
                else:
                    return 0.0
            return float(value)
        except:
            return 0.0
    
    def safe_int(value):
        """تحويل آمن إلى int"""
        try:
            if value is None:
                return 0
            if isinstance(value, bytes):
                if len(value) <= 4:
                    return int.from_bytes(value, byteorder='little', signed=False)
                else:
                    return 0
            return int(value)
        except:
            return 0
    
    # تحويل sqlite3.Row إلى dictionary عادي مع تحويل الأنواع
    analyses = []
    for row in rows:
        analyses.append({
            'id': row['id'],
            'username': row['username'],
            'analysis_date': row['analysis_date'],
            'total_customers': safe_int(row['total_customers']),
            'high_risk_count': safe_int(row['high_risk_count']),
            'medium_risk_count': safe_int(row['medium_risk_count']),
            'low_risk_count': safe_int(row['low_risk_count']),
            'avg_churn_probability': safe_float(row['avg_churn_probability']),
            'avg_customer_value': safe_float(row['avg_customer_value']),
            'avg_purchases': safe_float(row['avg_purchases']),
            'revenue_at_risk': safe_float(row['revenue_at_risk']),
            'predicted_future_value': safe_float(row['predicted_future_value']),
            'retention_rate': safe_float(row['retention_rate']) if row['retention_rate'] else None
        })
    
    return analyses


def get_analysis_details(analysis_id):
    """
    الحصول على تفاصيل تحليل معين
    
    Parameters:
    - analysis_id: رقم التحليل
    
    Returns:
    - DataFrame: بيانات العملاء المحللين
    """
    import pandas as pd
    
    conn = get_connection()
    
    df = pd.read_sql_query("""
        SELECT * FROM analyzed_customers
        WHERE analysis_id = ?
        ORDER BY churn_probability_best DESC
    """, conn, params=(analysis_id,))
    
    conn.close()
    
    return df


def delete_old_analyses(username, keep_count=10):
    """
    حذف التحليلات القديمة (الاحتفاظ بآخر X تحليل فقط)
    
    Parameters:
    - username: اسم المستخدم
    - keep_count: عدد التحليلات للاحتفاظ بها
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # الحصول على IDs التحليلات القديمة
    cursor.execute("""
        SELECT id FROM analysis_summary
        WHERE username = ?
        ORDER BY analysis_date DESC
        LIMIT -1 OFFSET ?
    """, (username, keep_count))
    
    old_ids = [row[0] for row in cursor.fetchall()]
    
    if old_ids:
        placeholders = ','.join(['?'] * len(old_ids))
        
        # حذف بيانات العملاء
        cursor.execute(f"""
            DELETE FROM analyzed_customers
            WHERE analysis_id IN ({placeholders})
        """, old_ids)
        
        # حذف ملخصات التحليل
        cursor.execute(f"""
            DELETE FROM analysis_summary
            WHERE id IN ({placeholders})
        """, old_ids)
        
        conn.commit()
    
    conn.close()


# إنشاء قاعدة البيانات عند استيراد الملف
init_database()
# Updated: 2025-12-14
