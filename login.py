# login.py
from database import migrate_from_json
migrate_from_json()

import streamlit as st
import subprocess
import sys
from auth import register_user, verify_login, save_session, check_session, verify_account

st.set_page_config(page_title="سجل دخولك", page_icon="🔐", layout="centered")

# التحقق من الجلسة النشطة
is_logged_in, username = check_session()
if is_logged_in:
    st.success(f"مرحباً {username}! أنت مسجل دخول بالفعل.")
    if st.button("🚀 الذهاب للتطبيق", width='stretch', type="primary"):
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py"])
        st.stop()
    st.stop()

# CSS للتصميم
st.markdown("""
    <style>
        .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .stButton>button { 
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            font-weight: bold;
            border: none;
            padding: 12px;
            border-radius: 10px;
            width: 100%;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .stTextInput>div>div>input {
            background-color: rgba(255,255,255,0.9);
            border-radius: 10px;
            padding: 12px;
        }
        .verification-box {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin: 20px 0;
            text-align: center;
            font-size: 1.2em;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# العنوان الرئيسي
st.markdown("""
    <div style="text-align: center; padding: 40px; color: white;">
        <h1 style="font-size: 3em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🔐 سجل دخولك</h1>
        <p style="font-size: 1.2em;">نظام تحليل سلوك العملاء بالذكاء الاصطناعي</p>
    </div>
""", unsafe_allow_html=True)

# اختيار اللغة
col1, col2 = st.columns([1, 1])
with col1:
    if st.button('🇺🇸 English', width='stretch'):
        st.session_state.language = 'English'
with col2:
    if st.button('🇸🇦 العربية', width='stretch'):
        st.session_state.language = 'العربية'

lang = st.session_state.get('language', 'العربية')

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs([
    '🔑 تسجيل الدخول' if lang == 'العربية' else '🔑 Login',
    '📝 إنشاء حساب' if lang == 'العربية' else '📝 Register',
    '✅ تفعيل الحساب' if lang == 'العربية' else '✅ Verify Account'
])

# Tab 1: تسجيل الدخول
with tab1:
    st.subheader('🔑 تسجيل الدخول' if lang == 'العربية' else '🔑 Login')
    
    with st.form("login_form"):
        username = st.text_input('👤 اسم المستخدم' if lang == 'العربية' else '👤 Username', 
                                key='login_username')
        password = st.text_input('🔒 كلمة المرور' if lang == 'العربية' else '🔒 Password', 
                                type='password', key='login_password')
        
        submit = st.form_submit_button('🚀 دخول' if lang == 'العربية' else '🚀 Login', 
                                      width='stretch')
        
        if submit:
            if not username or not password:
                st.error('⚠️ الرجاء إدخال جميع البيانات' if lang == 'العربية' else '⚠️ Please fill all fields')
            else:
                success, message = verify_login(username, password)
                if success:
                    save_session(username)
                    st.success(message)
                    st.balloons()
                    st.info('🚀 جاري تحويلك للتطبيق...' if lang == 'العربية' else '🚀 Redirecting to app...')
                    subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py"])
                    st.stop()
                else:
                    st.error(f'❌ {message}')

# Tab 2: إنشاء حساب
with tab2:
    st.subheader('📝 إنشاء حساب جديد' if lang == 'العربية' else '📝 Create New Account')
    
    with st.form("register_form"):
        new_username = st.text_input('👤 اسم المستخدم' if lang == 'العربية' else '👤 Username',
                                    key='register_username')
        new_email = st.text_input('📧 البريد الإلكتروني' if lang == 'العربية' else '📧 Email',
                                 key='register_email')
        new_password = st.text_input('🔒 كلمة المرور' if lang == 'العربية' else '🔒 Password',
                                    type='password', key='register_password')
        confirm_password = st.text_input('🔒 تأكيد كلمة المرور' if lang == 'العربية' else '🔒 Confirm Password',
                                        type='password', key='confirm_password')
        
        submit_register = st.form_submit_button('✅ إنشاء الحساب' if lang == 'العربية' else '✅ Create Account',
                                               width='stretch')
        
        if submit_register:
            if not new_username or not new_email or not new_password or not confirm_password:
                st.error('⚠️ الرجاء إدخال جميع البيانات' if lang == 'العربية' else '⚠️ Please fill all fields')
            elif new_password != confirm_password:
                st.error('❌ كلمات المرور غير متطابقة' if lang == 'العربية' else '❌ Passwords do not match')
            elif len(new_password) < 6:
                st.error('⚠️ كلمة المرور يجب أن تكون 6 أحرف على الأقل' if lang == 'العربية' else '⚠️ Password must be at least 6 characters')
            else:
                success, message, code = register_user(new_username, new_email, new_password)
                if success:
                    st.success(message)
                    st.markdown(f"""
                        <div class="verification-box">
                            🔑 كود التحقق الخاص بك:<br>
                            <span style="font-size: 2em; letter-spacing: 5px;">{code}</span><br>
                            <small>انسخ هذا الكود واذهب لتبويب "تفعيل الحساب"</small>
                        </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.error(f'❌ {message}')

# Tab 3: تفعيل الحساب
with tab3:
    st.subheader('✅ تفعيل الحساب' if lang == 'العربية' else '✅ Verify Account')
    
    st.info('💡 أدخل اسم المستخدم وكود التحقق الذي حصلت عليه' if lang == 'العربية' else '💡 Enter your username and verification code')
    
    with st.form("verify_form"):
        verify_username = st.text_input('👤 اسم المستخدم' if lang == 'العربية' else '👤 Username',
                                       key='verify_username')
        verify_code = st.text_input('🔑 كود التحقق' if lang == 'العربية' else '🔑 Verification Code',
                                   key='verify_code', max_chars=6)
        
        submit_verify = st.form_submit_button('✅ تفعيل الحساب' if lang == 'العربية' else '✅ Verify Account',
                                             width='stretch')
        
        if submit_verify:
            if not verify_username or not verify_code:
                st.error('⚠️ الرجاء إدخال جميع البيانات' if lang == 'العربية' else '⚠️ Please fill all fields')
            else:
                success, message = verify_account(verify_username, verify_code.upper())
                if success:
                    st.success(message)
                    st.info('✅ يمكنك الآن تسجيل الدخول!' if lang == 'العربية' else '✅ You can now login!')
                    st.balloons()
                else:
                    st.error(f'❌ {message}')

st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: white; padding: 20px;">
        <p>© 2025 Customer AI Dashboard | Powered by Streamlit</p>
    </div>
""", unsafe_allow_html=True)
