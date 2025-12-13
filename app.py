# app.py - الصفحة الرئيسية (Login)
import streamlit as st
from auth import register_user, verify_login, save_session, check_session, verify_account

st.set_page_config(
    page_title="نظام تحليل سلوك العملاء",
    page_icon="🔐",
    layout="centered"
)

# اختيار اللغة
if 'language' not in st.session_state:
    st.session_state.language = 'العربية'

col1, col2 = st.columns(2)
with col1:
    if st.button("🇸🇦 العربية", use_container_width=True, type="primary" if st.session_state.language == 'العربية' else "secondary"):
        st.session_state.language = 'العربية'
        st.rerun()
with col2:
    if st.button("🇬🇧 English", use_container_width=True, type="primary" if st.session_state.language == 'English' else "secondary"):
        st.session_state.language = 'English'
        st.rerun()

lang = st.session_state.language

# التحقق من الجلسة
is_logged_in, username = check_session()

if is_logged_in:
    if lang == 'العربية':
        st.success(f"مرحباً {username}! ✅")
        st.info("📊 استخدم القائمة الجانبية للانتقال إلى Dashboard")
    else:
        st.success(f"Welcome {username}! ✅")
        st.info("📊 Use the sidebar to navigate to Dashboard")
    st.balloons()
    st.stop()

# صفحة تسجيل الدخول
if lang == 'العربية':
    st.title("🔐 تسجيل الدخول")
    tab1, tab2, tab3 = st.tabs(["تسجيل الدخول", "إنشاء حساب جديد", "تفعيل الحساب"])
else:
    st.title("🔐 Login")
    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Verify Account"])

st.markdown("---")

# تسجيل الدخول
with tab1:
    with st.form("login_form"):
        if lang == 'العربية':
            username_input = st.text_input("اسم المستخدم", key="login_user")
            password_input = st.text_input("كلمة المرور", type="password", key="login_pass")
            submit = st.form_submit_button("دخول 🚀", use_container_width=True, type="primary")
        else:
            username_input = st.text_input("Username", key="login_user")
            password_input = st.text_input("Password", type="password", key="login_pass")
            submit = st.form_submit_button("Login 🚀", use_container_width=True, type="primary")
        
        if submit:
            success, message = verify_login(username_input, password_input)
            if success:
                save_session(username_input)
                st.success("✅ " + ("تم تسجيل الدخول بنجاح!" if lang == 'العربية' else "Login successful!"))
                st.info("📊 " + ("استخدم القائمة الجانبية للانتقال إلى Dashboard" if lang == 'العربية' else "Use the sidebar to navigate to Dashboard"))
                st.rerun()
            else:
                st.error("❌ " + message)

# إنشاء حساب جديد
with tab2:
    with st.form("register_form"):
        if lang == 'العربية':
            new_username = st.text_input("اسم المستخدم الجديد", key="reg_user")
            new_email = st.text_input("البريد الإلكتروني", key="reg_email")
            new_password = st.text_input("كلمة المرور", type="password", key="reg_pass")
            confirm_password = st.text_input("تأكيد كلمة المرور", type="password", key="reg_confirm")
            register_submit = st.form_submit_button("إنشاء حساب ✨", use_container_width=True)
        else:
            new_username = st.text_input("Username", key="reg_user")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_pass")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            register_submit = st.form_submit_button("Register ✨", use_container_width=True)
        
        if register_submit:
            if new_password != confirm_password:
                st.error("❌ " + ("كلمات المرور غير متطابقة!" if lang == 'العربية' else "Passwords do not match!"))
            elif len(new_password) < 4:
                st.error("❌ " + ("كلمة المرور يجب أن تكون 4 أحرف على الأقل" if lang == 'العربية' else "Password must be at least 4 characters"))
            else:
                success, message, code = register_user(new_username, new_email, new_password)
                if success and code:
                    st.success(message)
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); 
                                padding: 20px; border-radius: 10px; color: white; 
                                margin: 20px 0; text-align: center;'>
                        <h3>🔐 {"كود التحقق الخاص بك:" if lang == 'العربية' else "Your Verification Code:"}</h3>
                        <span style='font-size: 2em; letter-spacing: 5px;'>{code}</span><br>
                        <small>{"استخدم هذا الكود في تبويب تفعيل الحساب" if lang == 'العربية' else "Use this code in the Verify Account tab"}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.error(message if message else ("خطأ في عملية التسجيل" if lang == 'العربية' else "Registration error"))

# تفعيل الحساب
with tab3:
    if lang == 'العربية':
        st.subheader("✅ تفعيل الحساب")
        st.info("أدخل اسم المستخدم وكود التحقق")
    else:
        st.subheader("✅ Verify Account")
        st.info("Enter your username and verification code")
    
    with st.form("verify_form"):
        if lang == 'العربية':
            verify_username = st.text_input("اسم المستخدم", key="verify_user")
            verify_code = st.text_input("كود التحقق (6 أحرف)", key="verify_code", max_chars=6)
            verify_submit = st.form_submit_button("تفعيل الحساب 🎉", use_container_width=True)
        else:
            verify_username = st.text_input("Username", key="verify_user")
            verify_code = st.text_input("Verification Code (6 characters)", key="verify_code", max_chars=6)
            verify_submit = st.form_submit_button("Verify Account 🎉", use_container_width=True)
        
        if verify_submit:
            if not verify_username or not verify_code:
                st.error("❌ " + ("يرجى ملء جميع الحقول" if lang == 'العربية' else "Please fill all fields"))
            else:
                success, message = verify_account(verify_username, verify_code.upper())
                if success:
                    st.success(message)
                    st.info("🎉 " + ("يمكنك الآن تسجيل الدخول!" if lang == 'العربية' else "You can now login!"))
                    st.balloons()
                else:
                    st.error(message)

st.markdown("---")
st.caption("© 2025 Customer AI Dashboard")
