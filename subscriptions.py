# subscriptions.py 
import streamlit as st
from auth import get_user_subscription, update_user_subscription, get_usage_count, load_users
from datetime import datetime

def show_subscription_page():
    """عرض صفحة الاشتراكات"""
    
    lang = st.session_state.get('language', 'العربية')
    username = st.session_state.get('username', '')
    current_subscription = get_user_subscription(username)
    
    st.title('🎁 إدارة الاشتراكات' if lang == 'العربية' else '🎁 Subscription Management')
    
    # CSS للباقات
    st.markdown("""
        <style>
            .subscription-card {
                border-radius: 15px;
                padding: 25px;
                margin: 10px 0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: transform 0.3s;
                color: white;
            }
            .subscription-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 12px rgba(0,0,0,0.2);
            }
            .free-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .premium-card {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            }
            .vip-card {
                background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
            }
            .current-badge {
                background-color: #10b981;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                display: inline-block;
                margin-top: 10px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # عرض الباقة الحالية
    st.info(f"📊 **{'باقتك الحالية' if lang == 'العربية' else 'Your Current Plan'}:** {current_subscription.upper()}")
    
    # عرض الإحصائيات
    col1, col2 = st.columns(2)
    with col1:
        st.metric('📈 عدد الاستخدامات' if lang == 'العربية' else '📈 Usage Count', get_usage_count(username))
    with col2:
        users = load_users()
        if username in users:
            sub_date = users[username].get('subscription_date', users[username].get('created_at', 'N/A'))
            if sub_date != 'N/A':
                sub_date = datetime.strptime(sub_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            st.metric('📅 تاريخ الاشتراك' if lang == 'العربية' else '📅 Subscription Date', sub_date)
    
    st.markdown("---")
    
    # عرض الباقات الثلاثة في صف واحد
    col1, col2, col3 = st.columns(3)
    
    # البطاقة 1: Free
    with col1:
        st.markdown(f"""
            <div class="subscription-card free-card">
                <h2>📦 {'مجاني' if lang == 'العربية' else 'Free'}</h2>
                <h3>$0/{'شهر' if lang == 'العربية' else 'month'}</h3>
                <ul>
                    <li>✅ {'لوحة القيادة' if lang == 'العربية' else 'Dashboard'}</li>
                    <li>✅ {'العملاء المعرضون للخطر' if lang == 'العربية' else 'High Risk Customers'}</li>
                    <li>✅ {'الاقتراحات الذكية' if lang == 'العربية' else 'Smart Suggestions'}</li>
                    <li>✅ {'بيانات العملاء' if lang == 'العربية' else 'Customer Data'}</li>
                    <li>✅ {'نظام التنبيهات' if lang == 'العربية' else 'Alerts System'}</li>
                    <li>✅ {'التسويق الآلي' if lang == 'العربية' else 'Marketing Automation'}</li>
                    <li>❌ {'مقارنة النماذج' if lang == 'العربية' else 'Model Comparison'}</li>
                    <li>❌ {'التحليلات المتقدمة' if lang == 'العربية' else 'Advanced Analytics'}</li>
                </ul>
                {'<span class="current-badge">الباقة الحالية ✓</span>' if current_subscription == 'free' else ''}
            </div>
        """, unsafe_allow_html=True)
    
    # البطاقة 2: Premium
    with col2:
        st.markdown(f"""
            <div class="subscription-card premium-card">
                <h2>⭐ {'بريميوم' if lang == 'العربية' else 'Premium'}</h2>
                <h3>$29/{'شهر' if lang == 'العربية' else 'month'}</h3>
                <ul>
                    <li>✅ {'كل ميزات المجاني' if lang == 'العربية' else 'All Free Features'}</li>
                    <li>✅ {'مقارنة النماذج' if lang == 'العربية' else 'Model Comparison'}</li>
                    <li>✅ {'التصدير المتقدم' if lang == 'العربية' else 'Advanced Export'}</li>
                    <li>✅ {'تقارير شاملة' if lang == 'العربية' else 'Comprehensive Reports'}</li>
                    <li>❌ {'التحليلات المتقدمة' if lang == 'العربية' else 'Advanced Analytics'}</li>
                </ul>
                {'<span class="current-badge">الباقة الحالية ✓</span>' if current_subscription == 'premium' else ''}
            </div>
        """, unsafe_allow_html=True)
        
        if current_subscription == 'free':
            if st.button('🚀 ترقية للبريميوم' if lang == 'العربية' else '🚀 Upgrade to Premium', 
                        key='upgrade_premium', width='stretch'):
                success, msg = update_user_subscription(username, 'premium')
                if success:
                    st.session_state.subscription = 'premium'
                    st.success('✅ تم الترقية بنجاح!' if lang == 'العربية' else '✅ Upgraded successfully!')
                    st.balloons()
                    st.rerun()
    
    # البطاقة 3: VIP
    with col3:
        st.markdown(f"""
            <div class="subscription-card vip-card">
                <h2>💎 VIP</h2>
                <h3>$99/{'شهر' if lang == 'العربية' else 'month'}</h3>
                <ul>
                    <li>✅ {'كل ميزات البريميوم' if lang == 'العربية' else 'All Premium Features'}</li>
                    <li>✅ {'التحليلات المتقدمة' if lang == 'العربية' else 'Advanced Analytics'}</li>
                    <li>✅ {'استخدام غير محدود' if lang == 'العربية' else 'Unlimited Usage'}</li>
                    <li>✅ {'دعم فوري' if lang == 'العربية' else 'Priority Support'}</li>
                    <li>✅ {'تقارير مخصصة' if lang == 'العربية' else 'Custom Reports'}</li>
                    <li>✅ {'واجهة API' if lang == 'العربية' else 'API Access'}</li>
                </ul>
                {'<span class="current-badge">الباقة الحالية ✓</span>' if current_subscription == 'vip' else ''}
            </div>
        """, unsafe_allow_html=True)
        
        if current_subscription != 'vip':
            if st.button('👑 ترقية لـ VIP' if lang == 'العربية' else '👑 Upgrade to VIP', 
                        key='upgrade_vip', width='stretch'):
                success, msg = update_user_subscription(username, 'vip')
                if success:
                    st.session_state.subscription = 'vip'
                    st.success('✅ تم الترقية بنجاح!' if lang == 'العربية' else '✅ Upgraded successfully!')
                    st.balloons()
                    st.rerun()
    
    # إعدادات متقدمة
    st.markdown("---")
    st.subheader("⚙️ إعدادات الاشتراك" if lang == 'العربية' else "⚙️ Subscription Settings")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if current_subscription != 'free':
            if st.button('⬇️ التراجع للمجاني' if lang == 'العربية' else '⬇️ Downgrade to Free', 
                        key='downgrade_free', width='stretch', type="secondary"):
                success, msg = update_user_subscription(username, 'free')
                if success:
                    st.session_state.subscription = 'free'
                    st.success('✅ تم التراجع بنجاح!' if lang == 'العربية' else '✅ Downgraded successfully!')
                    st.rerun()
    
    with col_b:
        if current_subscription == 'vip':
            if st.button('⬇️ التراجع للبريميوم' if lang == 'العربية' else '⬇️ Downgrade to Premium', 
                        key='downgrade_premium', width='stretch', type="secondary"):
                success, msg = update_user_subscription(username, 'premium')
                if success:
                    st.session_state.subscription = 'premium'
                    st.success('✅ تم التراجع بنجاح!' if lang == 'العربية' else '✅ Downgraded successfully!')
                    st.rerun()
    
    with col_c:
        st.empty()  # عمود فارغ للتناسق
