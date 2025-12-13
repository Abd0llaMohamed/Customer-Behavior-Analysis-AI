# database.py - إدارة قاعدة البيانات 
import sqlite3
from datetime import datetime
import json

DB_NAME = "customer_analysis.db"

def init_database():
    """إنشاء قاعدة البيانات والجداول"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # جدول المستخدمين
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
    
    conn.commit()
    conn.close()

def get_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def migrate_from_json():
    """نقل البيانات من users.json إلى SQL"""
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        conn = get_connection()
        cursor = conn.cursor()
        
        for username, data in users.items():
            cursor.execute("""
                INSERT OR REPLACE INTO users 
                (username, password, email, subscription, subscription_date, usage_count, created_at, verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                username,
                data.get('password', ''),
                data.get('email', ''),
                data.get('subscription', 'free'),
                data.get('subscription_date', data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
                data.get('usage_count', 0),
                data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            ))
        
        conn.commit()
        conn.close()
        print("✅ تم نقل البيانات من JSON إلى SQL بنجاح!")
        return True
    except FileNotFoundError:
        print("⚠️ لم يتم العثور على users.json")
        return False
    except Exception as e:
        print(f"❌ خطأ في نقل البيانات: {e}")
        return False

# إنشاء قاعدة البيانات عند استيراد الملف
init_database()
