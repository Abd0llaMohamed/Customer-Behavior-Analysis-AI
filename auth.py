# auth.py - نظام المصادقة الكامل مع SQLite + حفظ الجلسة الصحيح
import streamlit as st
from datetime import datetime
import sqlite3
import random
import string
import json
import os
from database import get_connection


def save_session(username):
    """حفظ جلسة المستخدم (في session_state وفي ملف خارجي)"""
    subscription = get_user_subscription(username)
    
    # حفظ في session_state
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.subscription = subscription
    
    # حفظ في ملف خارجي (للانتقال بين login.py و app.py)
    with open('current_session.json', 'w', encoding='utf-8') as f:
        json.dump({
            'logged_in': True,
            'username': username,
            'subscription': subscription
        }, f)


def check_session():
    """التحقق من جلسة المستخدم"""
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        return True, st.session_state.get('username', '')
    return False, None


def clear_session():
    """مسح جلسة المستخدم"""
    st.session_state.clear()
    
    # مسح الملف الخارجي
    if os.path.exists('current_session.json'):
        os.remove('current_session.json')


def load_users():
    """تحميل جميع المستخدمين من قاعدة البيانات"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()
    
    users = {}
    for row in rows:
        users[row['username']] = {
            'password': row['password'],
            'email': row['email'] if 'email' in row.keys() else '',
            'subscription': row['subscription'],
            'subscription_date': row['subscription_date'],
            'usage_count': row['usage_count'],
            'created_at': row['created_at'],
            'verified': row['verified'] if 'verified' in row.keys() else 1,
            'verification_code': row['verification_code'] if 'verification_code' in row.keys() else ''
        }
    return users



def register_user(username, email, password):
    """تسجيل مستخدم جديد"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # التحقق من وجود المستخدم
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "اسم المستخدم موجود بالفعل", None
    
    # إنشاء كود تحقق
    verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute("""
            INSERT INTO users 
            (username, password, email, subscription, subscription_date, usage_count, created_at, verified, verification_code)
            VALUES (?, ?, ?, 'free', ?, 0, ?, 0, ?)
        """, (username, password, email, now, now, verification_code))
        conn.commit()
        conn.close()
        return True, "تم إنشاء الحساب بنجاح! استخدم كود التحقق لتفعيل حسابك", verification_code
    except Exception as e:
        conn.close()
        return False, f"خطأ في إنشاء الحساب: {str(e)}", None


def verify_login(username, password):
    """التحقق من تسجيل الدخول"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password, verified FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return False, "اسم المستخدم غير موجود"
    
    if row['password'] != password:
        return False, "كلمة المرور غير صحيحة"
    
    if row['verified'] == 0:
        return False, "الحساب غير مفعل! الرجاء تفعيل حسابك أولاً"
    
    return True, "تم تسجيل الدخول بنجاح!"


def verify_account(username, code):
    """تفعيل الحساب"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT verification_code, verified FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return False, "اسم المستخدم غير موجود"
    
    if row['verified'] == 1:
        conn.close()
        return False, "الحساب مفعل بالفعل"
    
    if row['verification_code'] != code:
        conn.close()
        return False, "كود التحقق غير صحيح"
    
    # تفعيل الحساب
    cursor.execute("UPDATE users SET verified = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    return True, "تم تفعيل الحساب بنجاح!"


def get_user_subscription(username):
    """الحصول على نوع اشتراك المستخدم"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT subscription FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row['subscription'] if row else 'free'


def update_user_subscription(username, subscription_type):
    """تحديث اشتراك المستخدم"""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        UPDATE users 
        SET subscription = ?, subscription_date = ?
        WHERE username = ?
    """, (subscription_type, now, username))
    
    conn.commit()
    conn.close()
    
    # تحديث الجلسة أيضاً
    if 'subscription' in st.session_state:
        st.session_state.subscription = subscription_type
    
    # تحديث الملف الخارجي
    if os.path.exists('current_session.json'):
        with open('current_session.json', 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        session_data['subscription'] = subscription_type
        with open('current_session.json', 'w', encoding='utf-8') as f:
            json.dump(session_data, f)
    
    return True, "تم التحديث بنجاح"


def increment_usage(username):
    """زيادة عداد الاستخدام"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET usage_count = usage_count + 1
        WHERE username = ?
    """, (username,))
    conn.commit()
    conn.close()


def get_usage_count(username):
    """الحصول على عدد مرات الاستخدام"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT usage_count FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row['usage_count'] if row else 0
