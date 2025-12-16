import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os
import json
import importlib
from streamlit_option_menu import option_menu
from io import BytesIO
from datetime import datetime, timedelta
from chatbot import show_chatbot
from subscriptions import show_subscription_page
from auth import check_session, get_user_subscription, increment_usage, clear_session

# ============== تكوين الصفحة (يجب أن يكون الأول) ==============
st.set_page_config(page_title="📊 Dashboard", layout="wide", initial_sidebar_state="expanded")

# ============== التحقق من الجلسة ==============
# تحميل الجلسة من الملف أولاً
if 'logged_in' not in st.session_state:
    if os.path.exists('current_session.json'):
        try:
            with open('current_session.json', 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                st.session_state.logged_in = session_data.get('logged_in', False)
                st.session_state.username = session_data.get('username', '')
                st.session_state.subscription = session_data.get('subscription', 'free')
        except:
            pass

# فحص الجلسة مرة واحدة فقط
is_logged_in, username = check_session()
if not is_logged_in:
    st.error("⚠️ يرجى تسجيل الدخول أولاً!")
    st.info("👈 اذهب للصفحة الرئيسية من القائمة الجانبية")
    st.stop()

# حفظ بيانات المستخدم في session_state
if 'username' not in st.session_state:
    st.session_state.username = username
if 'subscription' not in st.session_state:
    st.session_state.subscription = get_user_subscription(username)

# زيادة عداد الاستخدام
increment_usage(username)

# ============== تحميل gdown ==============
try:
    import gdown
except ImportError:
    st.warning("gdown not available, using fallback")
    gdown = None

# ============== تحميل النماذج من Google Drive ==============
MODEL_URLS = {
    'rf_churn_model.pkl': 'https://drive.google.com/uc?id=1idlcUhdY2iEig13jnqy4QMAOUnfgw_RI&export=download',
    'xgb_churn_model.pkl': 'https://drive.google.com/uc?id=1ZiTC5OEMWOpjp2rMoBFtCWi-gxVWnlPw&export=download',
    'best_churn_model.pkl': 'https://drive.google.com/uc?id=1bWSqxCFri4UHeb4KP3p-try70E7nkLuq&export=download'
}

@st.cache_resource
def load_models():
    """تحميل النماذج من Google Drive"""
    models = {}
    for model_name, drive_url in MODEL_URLS.items():
        model_path = model_name
        if not os.path.exists(model_path):
            st.info(f"جاري تحميل {model_name}...")
            try:
                if gdown:
                    gdown.download(drive_url, model_path, quiet=True)
                    st.success(f"✅ تم تحميل {model_name}")
            except Exception as e:
                st.warning(f"⚠️ خطأ في تحميل {model_name}: {e}")
        
        if os.path.exists(model_path):
            try:
                models[model_name.replace('.pkl', '')] = joblib.load(model_path)
            except Exception as e:
                st.error(f"❌ خطأ في فتح {model_name}: {e}")
    
    return models

# تحميل النماذج
models = load_models()

# ============== إعداد اللغة ==============
if 'language' not in st.session_state:
    st.session_state.language = 'العربية'

# ============== القواميس (translations) ==============
# ... (باقي الكود كما هو)


# ---------------- Page config (call early) ----------------

# تحميل الجلسة من الملف الخارجي أولاً
if 'logged_in' not in st.session_state:
    if os.path.exists('current_session.json'):
        try:
            with open('current_session.json', 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                st.session_state.logged_in = session_data.get('logged_in', False)
                st.session_state.username = session_data.get('username', '')
                st.session_state.subscription = session_data.get('subscription', 'free')
        except:
            pass

# التحقق من الجلسة
is_logged_in, username = check_session()
if not is_logged_in:
    st.error("⚠️ يرجى تسجيل الدخول أولاً!")
    st.stop()

# حفظ username في session_state
if 'username' not in st.session_state:
    st.session_state.username = username

# حفظ subscription في session_state
if 'subscription' not in st.session_state:
    st.session_state.subscription = get_user_subscription(username)

# زيادة عداد الاستخدام
increment_usage(username)

# ---------------- Language Setup ----------------
if 'language' not in st.session_state:
    st.session_state.language = 'العربية'

# ---------------- Translations ----------------
translations = {
    'العربية': {
        # Navigation
        'dashboard': 'لوحة القيادة',
        'high_risk': 'العملاء المعرضون للخطر', 
        'suggestions': 'الاقتراحات الذكية',
        'customer_data': 'بيانات العملاء',
        'model_comparison': 'مقارنة النماذج',
        'feature_matrix': 'مصفوفة الميزات', # (موجود في القاموس ولكن لن نستخدمه)
        'about': 'عن النظام', # (موجود في القاموس ولكن لن نستخدمه)
        'advanced_analytics': 'التحليلات المتقدمة',
        'alerts_system': 'نظام التنبيهات',
        'marketing_automation': 'التسويق الآلي', 
        'live_support': '💬 الدعم الفوري',
        'subscriptions': '🎁 الاشتراكات',


        # General
        'upload_file': '📁 اختر ملف Excel للعملاء (Name, Purchases, Total_Value, Visits)',
        'file_required': 'الملف يجب أن يحتوي الأعمدة: Name, Purchases, Total_Value, Visits',
        'download_template': '📥 تنزيل قالب Excel (آخر توليد)',
        'generate_random': '🔄 توليد بيانات عشوائية جديدة',
        
        # Dashboard
        'total_customers': '👥 إجمالي العملاء',
        'avg_churn_prob': '📉 متوسط احتمال الرحيل',
        'retention_rate': '🔁 معدل الاحتفاظ (تقديري)',
        'high_risk_customers': '⚠️ عملاء معرضون للخطر',
        'avg_customer_value': '💰 متوسط قيمة العميل (CLV)',
        'avg_purchases': '🛒 متوسط المشتريات',
        'revenue_at_risk': '💸 إيرادات معرضة للخطر',
        'highest_lowest': '🔎 أعلى/أدنى احتمال',
        
        # High Risk Page
        'high_risk_title': '⚠️ العملاء المعرضون لخطر ترك الخدمة',
        'risk_customers_found': 'يوجد {} عميل باحتمال ترك أعلى من 70%',
        'no_high_risk': 'حالياً لا يوجد عملاء في خطر كبير!',
        
        # Suggestions Page
        'smart_suggestions': '💡 نظام الاقتراحات الذكي',
        'select_customer': 'اختر عميل لرؤية الاقتراحات:',
        'risk_level': '🎯 مستوى الخطر:',
        'category': '📋 التصنيف:',
        'churn_probability': '📊 احتمالية الرحيل:',
        'proposed_suggestions': '💡 الاقتراحات المقترحة:',
        'recommended_actions': '⚡ الإجراءات الموصى بها:',
        
        # Data Page
        'customer_data_title': '📋 بيانات العملاء مع التنبؤات',
        'view_options': ['🤖 نتيجة أفضل نموذج', '📊 مقارنة النماذج الثلاثة', '📈 التفاصيل الكاملة المتقدمة'],
        'columns_ar': ['الاسم', 'المشتريات', 'القيمة', 'الزيارات', 'احتمال الرحيل'],
        
        # Model Comparison
        'model_comparison_title': '📊 مقارنة النماذج: RF vs XGB',
        'model_comparison_desc': 'عرض حالات الفرق بين النماذج للمراجعة اليدوية',
        
        # Feature Matrix
        'feature_matrix_title': '📋 مصفوفة الميزات',
        
        # Advanced Analytics
        'advanced_analytics_title': '📈 التحليلات المتقدمة',
        'customer_segmentation': 'تقسيم العملاء المتقدم',
        'business_metrics': 'مقاييس الأعمال',
        'retention_analysis': 'تحليل الاحتفاظ',
        'lifetime_value': 'القيمة الدائمة للعميل',
        
        # Alerts System
        'alerts_title': '🚨 نظام التنبيهات الذكي',
        'active_alerts': 'التنبيهات النشطة',
        'alert_settings': 'إعدادات التنبيهات',
        
        # Marketing Automation - جديد
        'marketing_automation_title': '🤖 التسويق الآلي',
        'segment_actions': 'الإجراءات الآلية للشرائح',
        'campaign_results': 'نتائج الحملات',
        'auto_recommendations': 'التوصيات الآلية',
        
        # About
        'about_title': 'عن النظام',
        'about_content': """
        ### 🎯 الهدف
        نظام تنبؤي للاحتبال الرحيل + لوحة KPIs + اقتراحات هجينة.

        ### ملاحظات مهمة حول XGBoost
        - إن لم تكن مكتبة `xgboost` منصبة أو لم يتم رفع ملف `xgb_churn_model.pkl`، سيستخدم التطبيق نتائج RF كبديل آمن.
        - لتفعيل XGBoost: أضف `xgboost` في requirements.txt ثم أعد النشر أو نفّذ `pip install xgboost`.
        """
    },
    'English': {
        # Navigation
        'dashboard': 'Dashboard',
        'high_risk': 'High Risk Customers', 
        'suggestions': 'Smart Suggestions',
        'customer_data': 'Customer Data',
        'model_comparison': 'Model Comparison',
        'feature_matrix': 'Feature Matrix', # (Exists but won't be used)
        'about': 'About System', # (Exists but won't be used)
        'advanced_analytics': 'Advanced Analytics',
        'alerts_system': 'Alerts System',
        'marketing_automation': 'Marketing Automation',
        'live_support': '💬 Live Support',

        
        # General
        'upload_file': '📁 Choose Excel file for customers (Name, Purchases, Total_Value, Visits)',
        'file_required': 'File must contain columns: Name, Purchases, Total_Value, Visits',
        'download_template': '📥 Download Excel Template (Last Generated)',
        'generate_random': '🔄 Generate New Random Data',
        
        # Dashboard
        'total_customers': '👥 Total Customers',
        'avg_churn_prob': '📉 Average Churn Probability',
        'retention_rate': '🔁 Estimated Retention Rate',
        'high_risk_customers': '⚠️ High Risk Customers',
        'avg_customer_value': '💰 Average Customer Value (CLV)',
        'avg_purchases': '🛒 Average Purchases',
        'revenue_at_risk': '💸 Revenue at Risk',
        'highest_lowest': '🔎 Highest/Lowest Probability',
        
        # High Risk Page
        'high_risk_title': '⚠️ Customers at Risk of Churn',
        'risk_customers_found': 'Found {} customers with churn probability > 70%',
        'no_high_risk': 'Currently no high-risk customers!',
        
        # Suggestions Page
        'smart_suggestions': '💡 Smart Suggestions System',
        'select_customer': 'Select customer to see suggestions:',
        'risk_level': '🎯 Risk Level:',
        'category': '📋 Category:',
        'churn_probability': '📊 Churn Probability:',
        'proposed_suggestions': '💡 Proposed Suggestions:',
        'recommended_actions': '⚡ Recommended Actions:',
        
        # Data Page
        'customer_data_title': '📋 Customer Data with Predictions',
        'view_options': ['🤖 Best Model Result', '📊 Three Models Comparison', '📈 Full Advanced Details'],
        'columns_en': ['Name', 'Purchases', 'Value', 'Visits', 'Churn Probability'],
        
        # Model Comparison
        'model_comparison_title': '📊 Model Comparison: RF vs XGB',
        'model_comparison_desc': 'Displaying cases with differences between models for manual review',
        
        # Feature Matrix
        'feature_matrix_title': '📋 Feature Matrix',
        
        # Advanced Analytics
        'advanced_analytics_title': '📈 Advanced Analytics',
        'customer_segmentation': 'Advanced Customer Segmentation',
        'business_metrics': 'Business Metrics',
        'retention_analysis': 'Retention Analysis',
        'lifetime_value': 'Customer Lifetime Value',
        
        # Alerts System
        'alerts_title': '🚨 Smart Alerts System',
        'active_alerts': 'Active Alerts',
        'alert_settings': 'Alert Settings',
        
        # Marketing Automation - جديد
        'marketing_automation_title': '🤖 Marketing Automation',
        'segment_actions': 'Automated Segment Actions',
        'campaign_results': 'Campaign Results',
        'auto_recommendations': 'Automated Recommendations',
        
        # About
        'about_title': 'About System',
        'about_content': """
        ### 🎯 Objective
        Predictive system for churn probability + KPIs dashboard + hybrid suggestions.

        ### Important Notes about XGBoost
        - If `xgboost` library is not installed or `xgb_churn_model.pkl` file is not uploaded, the app will use RF results as safe alternative.
        - To enable XGBoost: add `xgboost` to requirements.txt then redeploy or run `pip install xgboost`.
        """
    }
}

def get_text(key):
    """Get translated text based on current language"""
    lang = st.session_state.language
    return translations[lang].get(key, key)

# ---------------- CSS ----------------
st.markdown("""
    <style>
        .block-container { max-width: 1350px; margin: auto; background: #f7fafc; }
        .stMetric { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; padding: 25px; border-radius: 14px; box-shadow: 0 2px 8px 0 #0002; color: white !important; font-weight: bold; }
        .suggestion-box { background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 15px; border-radius: 10px; color: white; margin: 10px 0; font-weight: bold;}
        .warning-box { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 15px; border-radius: 10px; color: white; margin: 10px 0; font-weight: bold;}
        .danger-box { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); padding: 15px; border-radius: 10px; color: white; margin: 10px 0; font-weight: bold;}
        .feature-table { border-collapse: collapse; width: 100%; }
        .feature-table th, .feature-table td { border: 1px solid #ddd; padding: 8px; text-align: center; }
        .feature-table th { background-color: #f3f4f6; color: #111827; }
        .alert-info { background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); padding: 15px; border-radius: 10px; color: white; margin: 10px 0; }
        .alert-warning { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 15px; border-radius: 10px; color: white; margin: 10px 0; }
        .alert-danger { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); padding: 15px; border-radius: 10px; color: white; margin: 10px 0; }
        .segment-card { background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #3b82f6; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .automation-card { background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); padding: 20px; border-radius: 10px; color: white; margin: 10px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .campaign-card { background: white; padding: 15px; border-radius: 10px; border: 2px solid #e5e7eb; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# ---------------- Marketing Automation Functions ----------------
def get_automated_segment_actions(segment_name, language='العربية'):
    """إرجاع الإجراءات الآلية الموصى بها لكل شريحة"""
    actions = {
        'VIP Customers': {
            'العربية': {
                'action': 'إرسال عرض VIP حصري',
                'channel': 'البريد الإلكتروني والواتساب',
                'message': 'عرض خاص حصري للعملاء VIP - خصم 25% على المنتجات الجديدة',
                'expected_impact': 'معدل تحويل مرتفع + تعزيز الولاء'
            },
            'English': {
                'action': 'Send exclusive VIP offer',
                'channel': 'Email and WhatsApp', 
                'message': 'Special exclusive offer for VIP customers - 25% discount on new products',
                'expected_impact': 'High conversion rate + loyalty enhancement'
            }
        },
        'Loyal High-Value': {
            'العربية': {
                'action': 'برنامج مكافآت الولاء',
                'channel': 'البريد الإلكتروني',
                'message': 'مبروك! لقد ربحت 1000 نقطة في برنامج الولاء. استخدمها للحصول على مزايا حصرية.',
                'expected_impact': 'زيادة الاحتفاظ + تكرار الشراء'
            },
            'English': {
                'action': 'Loyalty rewards program',
                'channel': 'Email',
                'message': 'Congratulations! You have earned 1000 points in the loyalty program. Use them for exclusive benefits.',
                'expected_impact': 'Increased retention + repeat purchases'
            }
        },
        'At High Risk': {
            'العربية': {
                'action': 'حملة إنقاذ عاجلة',
                'channel': 'الاتصال المباشر + البريد الإلكتروني',
                'message': 'نفتقدك! هذا العرض الخاص لك فقط: خصم 30% على مشترياتك القادمة.',
                'expected_impact': 'منع التسرب + استعادة الثقة'
            },
            'English': {
                'action': 'Urgent rescue campaign', 
                'channel': 'Direct call + Email',
                'message': 'We miss you! This special offer is just for you: 30% discount on your next purchases.',
                'expected_impact': 'Churn prevention + trust restoration'
            }
        },
        'Inactive New': {
            'العربية': {
                'action': 'حملة إعادة تفعيل',
                'channel': 'البريد الإلكتروني والرسائل النصية',
                'message': 'اهلاً بعودتك! خصم ترحيبي 20% على أول عملية شراء.',
                'expected_impact': 'إعادة التفاعل + تحويل العملاء الجدد'
            },
            'English': {
                'action': 'Reactivation campaign',
                'channel': 'Email and SMS',
                'message': 'Welcome back! 20% welcome discount on your first purchase.',
                'expected_impact': 'Re-engagement + new customer conversion'
            }
        }
    }
    
    return actions.get(segment_name, {}).get(language, {
        'action': 'مراجعة إستراتيجية عامة',
        'channel': 'البريد الإلكتروني',
        'message': 'عرض ترويجي عام',
        'expected_impact': 'تحسين عام في التفاعل'
    })

def simulate_campaign_execution(segment_name, action_details, customer_count, language='العربية'):
    """محاكاة تنفيذ حملة والعوائد المتوقعة"""
    # تقديرات بسيطة للنتائج بناءً على نوع الشريحة
    base_conversion = {
        'VIP Customers': 0.35,  # 35% conversion
        'Loyal High-Value': 0.25,
        'At High Risk': 0.15, 
        'Inactive New': 0.20
    }
    
    conversion_rate = base_conversion.get(segment_name, 0.15)
    expected_conversions = int(customer_count * conversion_rate)
    
    # تقدير القيمة المتوقعة
    avg_order_value = {
        'VIP Customers': 500,
        'Loyal High-Value': 300,
        'At High Risk': 200,
        'Inactive New': 150
    }
    
    expected_revenue = expected_conversions * avg_order_value.get(segment_name, 200)
    
    if language == 'العربية':
        return {
            'expected_conversions': expected_conversions,
            'conversion_rate': conversion_rate * 100,
            'expected_revenue': expected_revenue,
            'summary': f'متوقع تحقيق {expected_conversions} عملية شراء ({conversion_rate*100:.1f}%) بإيرادات تقديرية ${expected_revenue:,.0f}'
        }
    else:
        return {
            'expected_conversions': expected_conversions,
            'conversion_rate': conversion_rate * 100,
            'expected_revenue': expected_revenue,
            'summary': f'Expected {expected_conversions} purchases ({conversion_rate*100:.1f}%) with estimated revenue ${expected_revenue:,.0f}'
        }

# ---------------- باقي الدوال الموجودة (بدون تغيير) ----------------
# [جميع الدوال السابقة تبقى كما هي بدون تغيير]
# Advanced Customer Segmentation, Business Metrics, Smart Alerts, etc.

# ---------------- Advanced Customer Segmentation ----------------
def advanced_customer_segmentation(df):
    """تقسيم العملاء متعدد الأبعاد"""
    # تقسيم حسب القيمة
    df['Value_Segment'] = pd.cut(df['Total_Value'], 
                                 bins=[0, 100, 500, float('inf')], 
                                 labels=['Low Value', 'Medium Value', 'High Value'])
    
    # تقسيم حسب النشاط
    df['Activity_Segment'] = pd.cut(df['Visits'], 
                                    bins=[0, 5, 20, float('inf')], 
                                    labels=['Inactive', 'Active', 'Very Active'])
    
    # تقسيم حسب الولاء (بناءً على عدد المشتريات)
    df['Loyalty_Segment'] = pd.cut(df['Purchases'], 
                                   bins=[0, 2, 10, float('inf')], 
                                   labels=['New', 'Regular', 'Loyal'])
    
    # تقسيم متقدم يجمع بين الأبعاد
    conditions = [
        (df['Total_Value'] > 500) & (df['Visits'] > 20),
        (df['Total_Value'] > 200) & (df['Churn_Probability'] < 30),
        (df['Churn_Probability'] > 70),
        (df['Purchases'] == 0)
    ]
    choices = ['VIP Customers', 'Loyal High-Value', 'At High Risk', 'Inactive New']
    df['Advanced_Segment'] = np.select(conditions, choices, default='Standard')
    
    return df

# ---------------- Advanced Business Metrics ----------------
def calculate_business_metrics(df):
    """حساب مقاييس الأعمال المتقدمة"""
    metrics = {}
    
    # معدل الاحتفاظ (تقديري)
    repeat_customers = df[df['Purchases'] > 1].shape[0]
    metrics['retention_rate'] = (repeat_customers / df.shape[0]) * 100 if df.shape[0] > 0 else 0
    
    # القيمة الدائمة للعميل (LTV) تقديرية
    avg_purchase_value = df['Total_Value'].mean() / df['Purchases'].mean() if df['Purchases'].mean() > 0 else 0
    avg_purchase_freq = df['Purchases'].mean()
    customer_lifespan = 12  # تقدير بـ 12 شهر
    metrics['ltv'] = avg_purchase_value * avg_purchase_freq * customer_lifespan
    
    # معدل التحويل (تقديري)
    metrics['conversion_rate'] = (df[df['Purchases'] > 0].shape[0] / df.shape[0]) * 100 if df.shape[0] > 0 else 0
    
    # قيمة العميل المتوقعة
    df['predicted_future_value'] = df['Total_Value'] * (1 - df['Churn_Probability']/100) * 1.2
    
    return metrics, df

# ---------------- Smart Alerts System  ----------------
def generate_smart_alerts(df):
    """نظام التنبيهات الذكي - (نسخة معدلة تقرأ من الإعدادات)"""
    
    # الخطوة 1: قراءة الإعدادات من session_state أو استخدام القيم الافتراضية
    # هذه المفاتيح (keys) هي نفسها المستخدمة في st.number_input في صفحة الإعدادات
    risk_thresh = st.session_state.get('risk_threshold', 20)
    inactive_thresh_pct = st.session_state.get('inactive_threshold', 10)
    revenue_thresh_pct = st.session_state.get('revenue_threshold', 30)
    new_customer_thresh_pct = st.session_state.get('new_customer_threshold', 40)

    # الخطوة 2: تحويل النسب المئوية (مثل 10) إلى قيم عشرية (مثل 0.1) لاستخدامها في المقارنات
    inactive_thresh = inactive_thresh_pct / 100.0
    revenue_thresh = revenue_thresh_pct / 100.0
    new_customer_thresh = new_customer_thresh_pct / 100.0
    
    alerts = []
    
    # === تحليل نسبة العملاء المعرضين للخطر ===
    high_risk_count = (df['Churn_Probability'] > 70).sum()
    high_risk_percentage = (high_risk_count / len(df)) * 100 if len(df) > 0 else 0
    
    # (تم التعديل) استخدام risk_thresh بدلاً من 20
    if high_risk_percentage > risk_thresh:
        alerts.append({
            'type': 'danger',
            'title': 'نسبة عالية من العملاء المعرضين للخطر' if st.session_state.language == 'العربية' else 'High Percentage of At-Risk Customers',
            'message': f'{high_risk_percentage:.1f}% من العملاء معرضون للرحيل (الحد: {risk_thresh}%)' if st.session_state.language == 'العربية' else f'{high_risk_percentage:.1f}% of customers are at risk (Threshold: {risk_thresh}%)',
            'priority': 'high'
        })
    
    # === تحليل العملاء غير النشطين ===
    inactive_customers = df[df['Visits'] == 0].shape[0]
    
    # (تم التعديل) استخدام inactive_thresh بدلاً من 0.1
    if inactive_customers > len(df) * inactive_thresh and len(df) > 0:
        alerts.append({
            'type': 'warning',
            'title': 'عدد كبير من العملاء غير النشطين' if st.session_state.language == 'العربية' else 'Large Number of Inactive Customers',
            'message': f'{inactive_customers} عميل غير نشط (الحد: {inactive_thresh_pct}%)' if st.session_state.language == 'العربية' else f'{inactive_customers} inactive customers (Threshold: {inactive_thresh_pct}%)',
            'priority': 'medium'
        })
    
    # === تحليل القيمة المفقودة المحتملة ===
    revenue_at_risk = df[df['Churn_Probability'] > 70]['Total_Value'].sum()
    total_revenue = df['Total_Value'].sum()
    
    # (تم التعديل) استخدام revenue_thresh بدلاً من 0.3
    if revenue_at_risk > total_revenue * revenue_thresh and total_revenue > 0:
        alerts.append({
            'type': 'danger',
            'title': 'إيرادات عالية معرضة للخطر' if st.session_state.language == 'العربية' else 'High Revenue at Risk',
            'message': f'${revenue_at_risk:,.2f} من الإيرادات معرضة للخطر (الحد: {revenue_thresh_pct}%)' if st.session_state.language == 'العربية' else f'${revenue_at_risk:,.2f} revenue at risk (Threshold: {revenue_thresh_pct}%)',
            'priority': 'high'
        })
    
    # === تحليل العملاء الجدد ===
    new_customers = df[df['Purchases'] <= 1].shape[0]
    
    # (تم التعديل) استخدام new_customer_thresh بدلاً من 0.4
    if new_customers > len(df) * new_customer_thresh and len(df) > 0:
        alerts.append({
            'type': 'info',
            'title': 'تركيز عالٍ على العملاء الجدد' if st.session_state.language == 'العربية' else 'High Concentration of New Customers',
            'message': f'فرصة لتحسين استراتيجية الاحتفاظ (الحد: {new_customer_thresh_pct}%)' if st.session_state.language == 'العربية' else f'Opportunity to improve retention strategy (Threshold: {new_customer_thresh_pct}%)',
            'priority': 'medium'
        })
    
    return sorted(alerts, key=lambda x: x['priority'], reverse=True)
# ---------------- Hybrid suggestions function (الأصلية) ----------------
def get_smart_suggestions(churn_prob, total_value, purchases, visits):
    lang = st.session_state.language
    
    if lang == 'English':
        suggestions = []
        actions = []
        priority = "Very High 🚨"
        if churn_prob <= 30:
            priority = "Low ✅"
            suggestions = [
                "✅ Customer is very loyal - maintain this level",
                "💎 Offer periodic appreciation gifts",
                "🎁 Simple and easy loyalty program", 
                "📧 Send special offers to loyal customers"
            ]
            actions = ["Maintain", "Appreciation", "Loyalty"]
        elif churn_prob <= 50:
            priority = "Medium ⚠️"
            suggestions = [
                "⚠️ Customer is committed but should be monitored",
                "🎯 Offer exclusive and new offers",
                "📞 Contact to understand their needs",
                "🚀 Suggest new products matching their history"
            ]
            actions = ["Monitor", "Offers", "Contact"]
        elif churn_prob <= 70:
            priority = "High ⚠️"
            suggestions = [
                "🔴 Customer showing signs of weak commitment",
                "💰 Offer limited-time special discount (15-20%)",
                "📞 Call personally to check satisfaction",
                "🎁 Offer gift or extra reward",
                "⭐ Ask for service rating for improvement"
            ]
            actions = ["Discount", "Call", "Improvement"]
        else:
            priority = "Critical 🚨"
            suggestions = [
                "🚨 This customer is about to leave - act now!",
                "💰 Offer very large discount (25-30%)",
                "📞 Call immediately - there might be a problem",
                "🎁 Offer valuable gift or large reward",
                "👥 Have customer service team follow up personally",
                "📋 Ask for reasons of dissatisfaction"
            ]
            actions = ["Immediate Rescue", "Big Discount", "Personal Follow-up"]

        ai_note = ""
        if purchases > 5 and total_value > 500:
            ai_note = "Suggestion: Target with VIP offers as customer has high value."
        elif purchases == 0:
            ai_note = "Suggestion: Reactivation campaign with welcome discount."

        category = "Loyal" if churn_prob <= 30 else ("Normal" if churn_prob <= 50 else ("Medium Risk" if churn_prob <= 70 else "Very High Risk"))
    else:
        # Arabic version (original)
        suggestions = []
        actions = []
        priority = "عالية جداً 🚨"
        if churn_prob <= 30:
            priority = "منخفضة ✅"
            suggestions = [
                "✅ العميل مخلص جداً - حافظ على هذا المستوى",
                "💎 قدم هدايا تقديرية دورية",
                "🎁 برنامج ولاء بسيط وسهل",
                "📧 إرسال عروض خاصة للعملاء المخلصين"
            ]
            actions = ["الحفاظ", "التقدير", "الولاء"]
        elif churn_prob <= 50:
            priority = "متوسطة ⚠️"
            suggestions = [
                "⚠️ العميل ملتزم لكن يجب مراقبته",
                "🎯 قدم له عروض حصرية وجديدة",
                "📞 تواصل معه للتعرف على احتياجاته",
                "🚀 اقترح منتجات جديدة تناسب تاريخه"
            ]
            actions = ["المراقبة", "العروض", "التواصل"]
        elif churn_prob <= 70:
            priority = "عالية ⚠️"
            suggestions = [
                "🔴 العميل بدأ يظهر علامات ضعف الالتزام",
                "💰 قدم خصم خاص محدود الوقت (15-20%)",
                "📞 اتصل به شخصياً للتحقق من رضاه",
                "🎁 قدم هدية أو مكافأة إضافية",
                "⭐ اطلب منه تقييم خدمتك للتحسين"
            ]
            actions = ["الخصم", "الاتصال", "التحسين"]
        else:
            priority = "حرجة جداً 🚨"
            suggestions = [
                "🚨 هذا العميل على وشب الرحيل - تصرف الآن!",
                "💰 عرض خصم كبير جداً (25-30%)",
                "📞 اتصل به فوراً - قد يكون هناك مشكلة",
                "🎁 قدم هدية قيمة أو مكافأة كبيرة",
                "👥 اجعل فريق خدمة العملاء يتابعه شخصياً",
                "📋 اطلب منه أسباب عدم رضاه"
            ]
            actions = ["الإنقاذ الفوري", "الخصم الكبير", "المتابعة الشخصية"]

        ai_note = ""
        if purchases > 5 and total_value > 500:
            ai_note = "اقتراح: استهداف بعروض VIP لأن العميل قيمة عالية."
        elif purchases == 0:
            ai_note = "اقتراح: حملة إعادة تفعيل مع خصم ترحيبي."

        category = "مخلص" if churn_prob <= 30 else ("عادي" if churn_prob <= 50 else ("خطر متوسط" if churn_prob <= 70 else "خطر جداً"))

    return {"priority": priority, "suggestions": suggestions, "actions": actions, "category": category, "ai_note": ai_note}

# ---------------- Model loading with safe XGB handling ----------------
@st.cache_resource
def load_model_safe(path):
    """
    تحميل النموذج مع معالجة الأخطاء ورسائل واضحة
    """
    if not path:
        st.warning("⚠️ مسار الملف غير محدد")
        return None
        
    if not os.path.exists(path):
        st.warning(f"📁 الملف غير موجود: {path}")
        return None
        
    try:
        model = joblib.load(path)
        # Model loaded successfully
        return model
    except Exception as e:
        st.error(f"❌ خطأ في تحميل النموذج {path}: {str(e)}")
        return None
# check xgboost availability
xgb_available = importlib.util.find_spec("xgboost") is not None
if not xgb_available:
    st.warning("XGBoost package not installed. You can add 'xgboost' to requirements.txt then redeploy to enable XGBoost." if st.session_state.language == 'English' else "حزمة xgboost غير منصبة. يمكنك إضافة 'xgboost' إلى requirements.txt ثم إعادة النشر لتفعيل XGBoost.")

# دالة إنشاء نموذج افتراضي للطوارئ
def create_fallback_model():
    """إنشاء نموذج احتياطي بسيط"""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    try:
        # نموذج بسيط جداً
        X, y = make_classification(n_samples=100, n_features=3, n_informative=2, 
                                   n_redundant=0, n_repeated=0, random_state=42)
        
        model = RandomForestClassifier(n_estimators=5, random_state=42)
        model.fit(X, y)
        
        st.success("تم إنشاء النموذج الاحتياطي بنجاح!" if st.session_state.language == 'العربية' else "Fallback model created successfully!")
        return model
    except Exception as e:
        st.error(f"خطأ في إنشاء النموذج: {e}" if st.session_state.language == 'العربية' else f"Failed to create fallback model: {e}")
        return None

    
    try:
        with st.spinner("🔄 جاري إنشاء نموذج افتراضي..." if st.session_state.language == 'العربية' else "🔄 Creating fallback model..."):
            # بيانات تدريب بسيطة
            X, y = make_classification(n_samples=50, n_features=3, random_state=42)
            
            # نموذج بسيط
            model = RandomForestClassifier(n_estimators=5, random_state=42)
            model.fit(X, y)
            
        st.success("✅ تم إنشاء نموذج افتراضي بنجاح!" if st.session_state.language == 'العربية' else "✅ Fallback model created successfully!")
        return model
        
    except Exception as e:
        st.error(f"❌ فشل إنشاء النموذج الافتراضي: {e}" if st.session_state.language == 'العربية' else f"❌ Failed to create fallback model: {e}")
        return None

# تحميل النماذج مع معالجة أفضل
#st.sidebar.markdown("### 🤖 حالة النماذج" if st.session_state.language == 'العربية' else "### 🤖 Model Status")

# تحميل Random Forest
rf_model = load_model_safe("rf_churn_model.pkl")

# تحميل XGBoost
xgb_model = None
if xgb_available:
    xgb_model = load_model_safe("xgb_churn_model.pkl")
else:
    st.sidebar.info("🔧 حزمة XGBoost غير مثبتة" if st.session_state.language == 'العربية' else "🔧 XGBoost package not installed")

# تحديد النموذج الأفضل
if rf_model and xgb_model:
    best_model = xgb_model
    st.sidebar.success("🎯 جميع النماذج جاهزة" if st.session_state.language == 'العربية' else "🎯 All models ready")
elif rf_model:
    best_model = rf_model
    st.sidebar.info("ℹ️ يتم استخدام Random Forest" if st.session_state.language == 'العربية' else "ℹ️ Using Random Forest")
elif xgb_model:
    best_model = xgb_model 
    st.sidebar.info("ℹ️ يتم استخدام XGBoost" if st.session_state.language == 'العربية' else "ℹ️ Using XGBoost")
else:
    # إنشاء نموذج افتراضي في حال عدم وجود أي نموذج
    st.sidebar.warning("🚨 جاري إنشاء نموذج افتراضي..." if st.session_state.language == 'العربية' else "🚨 Creating fallback model...")
    best_model = create_fallback_model()

# ---------------- helper: safe predict_proba ----------------
def safe_predict_proba(model, X):
    n = len(X)
    if model is None:
        return np.zeros((n, 2))
    try:
        proba = model.predict_proba(X)
        proba = np.asarray(proba)
        if proba.ndim == 1:
            proba = np.vstack([1 - proba, proba]).T
        if proba.shape[1] == 1:
            proba = np.hstack([1-proba, proba])
        return proba
    except Exception:
        # try predict -> map to probabilities 0/1
        try:
            preds = model.predict(X)
            preds = np.asarray(preds).astype(int)
            proba = np.zeros((n, 2))
            proba[np.arange(n), preds] = 1
            return proba
        except Exception as e:
            warning_msg = f"Model exists but failed prediction (predict/proba). Will use default values (0%). Internal error: {e}"
            if st.session_state.language == 'العربية':
                warning_msg = f"موديل موجود لكنه فشل في التنبؤ (predict/proba). سيتم استخدام قيم افتراضية (0%). خطأ داخلي: {e}"
            st.warning(warning_msg)
            return np.zeros((n, 2))

# ---------------- sample template helpers ----------------
def make_sample_df():
    return pd.DataFrame({
        "Name": ["Ali", "Sara", "Omar", "Nour"],
        "Purchases": [5, 2, 10, 1],
        "Total_Value": [250.0, 80.0, 1200.0, 30.0],
        "Visits": [10, 4, 25, 2]
    })

def to_excel_bytes(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="clients")
    return buffer.getvalue()

# ---------------- Sidebar ----------------
# ========== بيانات أولية الزرين ==========
if "sample" not in st.session_state:
    st.session_state["sample"] = pd.DataFrame({
        "Name": [f"عميل {i+1}" for i in range(15)],
        "Purchases": np.random.randint(1, 20, 15),
        "Total_Value": np.random.randint(100, 5000, 15),
        "Visits": np.random.randint(1, 50, 15)
    })

# ========== الشريط الجانبي ==========
with st.sidebar:
    st.image("logo.png", width='stretch')
    
    # Language Selector
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button('🇺🇸 English', width='stretch'):
            st.session_state.language = 'English'
            st.rerun()
    with col2:
        if st.button('🇸🇦 العربية', width='stretch'):
            st.session_state.language = 'العربية'
            st.rerun()
    
    st.title("Customer Behavior Analysis System Using Artificial Intelligence")
   # st.markdown(f"<small>{'Checks for XGBoost and maintains operation when absent' if st.session_state.language == 'English' else 'يتحقق من وجود XGBoost ويحافظ على التشغيل عند غيابه'}</small>\n<hr>", unsafe_allow_html=True)
    
    # ========== أزرار توليد وتحميل البيانات العشوائية ==========
    st.markdown("### 📊 إدارة بيانات القالب" if st.session_state.language == 'العربية' else "### 📊 Template Data Management")
    
    # الزر الأول: توليد بيانات عشوائية جديدة
    if st.button(get_text('generate_random'), width='stretch'):
        n = np.random.randint(10, 30)  # من 10 إلى 30 صف عشوائي
        if st.session_state.language == 'English':
            names = [f"Customer {i+1}" for i in range(n)]
        else:
            names = [f"عميل {i+1}" for i in range(n)]
            
        st.session_state["sample"] = pd.DataFrame({
            "Name": names,
            "Purchases": np.random.randint(1, 20, n),
            "Total_Value": np.random.randint(100, 5000, n),
            "Visits": np.random.randint(1, 50, n)
        })
        success_msg = f"✅ Generated {n} rows of random data!" if st.session_state.language == 'English' else f"✅ تم توليد {n} صف من البيانات العشوائية!"
        st.success(success_msg)
    
    # الزر الثاني: تحميل آخر بيانات مولدة
    st.download_button(
        get_text('download_template'),
        data=to_excel_bytes(st.session_state["sample"]),
        file_name="sample_clients.xlsx",
        width='stretch'
    )
    
    st.markdown("---")
    
    # --- (بداية التعديل) ---
    # Navigation menu - إزالة مصفوفة الميزات وعن النظام
    menu_options = [

        get_text('dashboard'),
        get_text('high_risk'), 
        get_text('suggestions'),
        get_text('customer_data'),
        get_text('advanced_analytics'),
        get_text('alerts_system'),
        get_text('marketing_automation'),  
        get_text('live_support'),
        get_text('model_comparison'),
        get_text('subscriptions')  
]

    
    page = option_menu(
    menu_title="Main Menu",
    options=menu_options,
    icons=["bar-chart-fill", "exclamation-circle-fill", "lightbulb-fill", "table", "graph-up", "bell-fill", "robot", "bar-chart", "gift"],
    menu_icon="graph-up",
    default_index=0
)

## زر تسجيل الخروج
st.sidebar.markdown("---")

if st.sidebar.button("🚪 تسجيل الخروج" if st.session_state.get('language', 'العربية') == 'العربية' else "🚪 Logout", width='stretch', type="secondary"):
    clear_session()
    st.success("تم تسجيل الخروج بنجاح!" if st.session_state.get('language', 'العربية') == 'العربية' else "Logged out successfully!")
    st.info("الرجاء إعادة تشغيل login.py" if st.session_state.get('language', 'العربية') == 'العربية' else "Please restart login.py")
    st.stop()


    # --- (نهاية التعديل) ---

# ---------------- File uploader ----------------
uploaded_file = st.file_uploader(get_text('upload_file'), type=["xlsx", "csv"])

if not uploaded_file:
    info_msg = "📁 Upload .xlsx file with columns: Name, Purchases, Total_Value, Visits. You can download a template for testing." if st.session_state.language == 'English' else "📁 قم برفع ملف .xlsx يحتوي الأعمدة: Name, Purchases, Total_Value, Visits. يمكنك تنزيل قالب للتجربة."
    st.info(info_msg)
    st.stop()

# ---------------- Read and validate data ----------------
try:
    # (هذا هو التعديل)
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
        
except Exception as e:
    st.error(f"Failed to read file: {e}" if st.session_state.language == 'English' else f"فشل قراءة الملف: {e}")
    st.stop()

required_cols = ["Name", "Purchases", "Total_Value", "Visits"]
missing_cols = [c for c in required_cols if c not in df.columns]
if missing_cols:
    error_msg = f"File missing columns: {', '.join(missing_cols)}" if st.session_state.language == 'English' else f"الملف مفقود الأعمدة التالية: {', '.join(missing_cols)}"
    st.error(error_msg)
    st.stop()

df['Purchases'] = pd.to_numeric(df['Purchases'], errors='coerce').fillna(0).astype(int)
df['Total_Value'] = pd.to_numeric(df['Total_Value'], errors='coerce').fillna(0.0)
df['Visits'] = pd.to_numeric(df['Visits'], errors='coerce').fillna(0).astype(int)
df['Name'] = df['Name'].astype(str)

success_msg = f"File loaded successfully: {uploaded_file.name}" if st.session_state.language == 'English' else f"تم تحميل الملف: {uploaded_file.name}"
st.success(success_msg)

feature_cols = ['Purchases', 'Total_Value', 'Visits']
X_input = df[feature_cols]

# ---------------- Compute probabilities with safe fallback for XGB ----------------
df['Churn_Probability_RF'] = safe_predict_proba(rf_model, X_input)[:, 1] * 100

if xgb_available and xgb_model is not None:
    df['Churn_Probability_XGB'] = safe_predict_proba(xgb_model, X_input)[:, 1] * 100
else:
    # fallback: use RF as substitute and inform user
    df['Churn_Probability_XGB'] = df['Churn_Probability_RF']
    if not xgb_available:
        st.info("XGBoost not installed; using Random Forest results as substitute for display." if st.session_state.language == 'English' else "XGBoost غير منصب؛ تم استخدام نتيجة Random Forest كبديل للعرض.")
    elif xgb_model is None:
        st.info("XGBoost model file (xgb_churn_model.pkl) not found or corrupted; using Random Forest as temporary substitute." if st.session_state.language == 'English' else "ملف نموذج XGBoost (xgb_churn_model.pkl) غير موجود أو تالف؛ تم استخدام Random Forest كبديل مؤقت.")

if best_model is not None:
    df['Churn_Probability'] = safe_predict_proba(best_model, X_input)[:, 1] * 100
else:
    # if no best model, use average of RF and XGB as a simple ensemble
    df['Churn_Probability'] = ((df['Churn_Probability_RF'] + df['Churn_Probability_XGB']) / 2.0)

for col in ['Churn_Probability_RF', 'Churn_Probability_XGB', 'Churn_Probability']:
    df[col] = df[col].clip(0, 100)

# ---------------- Additional columns ----------------
if st.session_state.language == 'English':
    df['Segment'] = pd.cut(df['Churn_Probability'], bins=[-1,30,70,100], labels=["Loyal","Medium","At Risk"])
    df['Final_Label'] = df['Churn_Probability'].apply(lambda x: '✅ Loyal' if x <= 30 else ('⚠️ Medium' if x <= 70 else '🚨 At Risk'))
else:
    df['Segment'] = pd.cut(df['Churn_Probability'], bins=[-1,30,70,100], labels=["مخلص","متوسط","معرض"])
    df['Final_Label'] = df['Churn_Probability'].apply(lambda x: '✅ مخلص' if x <= 30 else ('⚠️ متوسط' if x <= 70 else '🚨 معرض للرحيل'))

# ---------------- تطبيق الميزات الجديدة ----------------
# تقسيم العملاء المتقدم
df = advanced_customer_segmentation(df)

# حساب مقاييس الأعمال المتقدمة
business_metrics, df = calculate_business_metrics(df)

# توليد التنبيهات
alerts = generate_smart_alerts(df)

high_risk = df[df['Churn_Probability'] > 70]

# ---------------- Pages ----------------
# Dashboard
if page == get_text('dashboard'):
    st.title("Dashboard - KPIs" if st.session_state.language == 'English' else "لوحة القيادة - KPIs")
    
    # عرض التنبيهات أولاً
    if alerts:
        st.subheader("🚨 التنبيهات المهمة" if st.session_state.language == 'العربية' else "🚨 Important Alerts")
        for alert in alerts[:3]:  # عرض أهم 3 تنبيهات فقط
            alert_class = f"alert-{alert['type']}"
            st.markdown(f"""<div class="{alert_class}"><strong>{alert['title']}</strong><br>{alert['message']}</div>""", unsafe_allow_html=True)
    
    total_customers = len(df)
    high_risk_count = (df['Churn_Probability'] > 70).sum()
    high_risk_pct = (high_risk_count / total_customers) * 100 if total_customers else 0
    avg_churn = df['Churn_Probability'].mean() if total_customers else 0
    estimated_retention = 100 - avg_churn
    avg_total_value = df['Total_Value'].mean() if total_customers else 0
    avg_purchases = df['Purchases'].mean() if total_customers else 0
    revenue_at_risk = df.loc[df['Churn_Probability'] > 70, 'Total_Value'].sum()
    max_churn = df['Churn_Probability'].max() if total_customers else 0
    min_churn = df['Churn_Probability'].min() if total_customers else 0

    # الصف الأول من المؤشرات
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(get_text('total_customers'), f"{total_customers}")
    k2.metric(get_text('avg_churn_prob'), f"{avg_churn:.1f}%")
    k3.metric(get_text('retention_rate'), f"{estimated_retention:.1f}%")
    k4.metric(get_text('high_risk_customers'), f"{high_risk_count} ({high_risk_pct:.1f}%)")

    # الصف الثاني من المؤشرات
    st.write("### Additional Metrics" if st.session_state.language == 'English' else "### مزيد من المؤشرات")
    k5, k6, k7, k8 = st.columns(4)
    k5.metric(get_text('avg_customer_value'), f"${avg_total_value:,.2f}")
    k6.metric(get_text('avg_purchases'), f"{avg_purchases:.2f}")
    k7.metric(get_text('revenue_at_risk'), f"${revenue_at_risk:,.2f}")
    k8.metric(get_text('highest_lowest'), f"{max_churn:.1f}% / {min_churn:.1f}%")

    # الصف الثالث: مقاييس الأعمال المتقدمة
    st.write("### Advanced Business Metrics" if st.session_state.language == 'English' else "### مقاييس الأعمال المتقدمة")
    k9, k10, k11, k12 = st.columns(4)
    k9.metric("📊 Retention Rate", f"{business_metrics['retention_rate']:.1f}%")
    k10.metric("💎 Customer LTV", f"${business_metrics['ltv']:,.2f}")
    k11.metric("🔄 Conversion Rate", f"{business_metrics['conversion_rate']:.1f}%")
    predicted_future_value = df['predicted_future_value'].sum()
    k12.metric("🚀 Predicted Future Value", f"${predicted_future_value:,.2f}")

    st.markdown("---")
    
    # رسوم بيانية
    col1, col2 = st.columns(2)
    
    with col1:
        # توزيع الشرائح
        pie_data = df['Segment'].value_counts().reset_index()
        pie_data.columns = ['Segment', 'count']
        
        if st.session_state.language == 'English':
            color_map = {"Loyal":"#31c48d","Medium":"#60a5fa","At Risk":"#f87171"}
            title = "Customer Segments Distribution"
        else:
            color_map = {"مخلص":"#31c48d","متوسط":"#60a5fa","معرض":"#f87171"}
            title = "توزيع شرائح العملاء"
            
        fig = px.pie(pie_data, names='Segment', values='count', color='Segment',
                     color_discrete_map=color_map, title=title)
        fig.update_traces(textinfo='label+percent')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        # توزيع الشرائح المتقدمة
        advanced_segment_data = df['Advanced_Segment'].value_counts().reset_index()
        advanced_segment_data.columns = ['Segment', 'count']
        
        fig2 = px.bar(advanced_segment_data, x='Segment', y='count', 
                       title="Advanced Customer Segments" if st.session_state.language == 'English' else "الشرائح المتقدمة للعملاء",
                       color='count', color_continuous_scale='viridis')
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    st.write("#### Most Risky Customers (Top 10)" if st.session_state.language == 'English' else "#### العملاء الأكثر خطورة (Top 10)")
    top_risk = df.sort_values('Churn_Probability', ascending=False).head(10)
    disp = top_risk[['Name','Purchases','Total_Value','Visits','Churn_Probability', 'Advanced_Segment']].copy()
    disp['Churn_Probability'] = disp['Churn_Probability'].apply(lambda x: f"{x:.1f}%")
    st.dataframe(disp, width='stretch')

    csv = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("📥 Download Full Report (CSV)" if st.session_state.language == 'English' else "📥 تنزيل تقرير كامل (CSV)",
                    data=csv, 
                    file_name="clients_full_report.csv",
                    key="download_report_1") 


    # ========== أضف هنا! ========== ⬇️⬇️⬇️
    
    # حفظ التحليل في Database
    if 'last_analysis_saved' not in st.session_state:
        st.session_state.last_analysis_saved = False

    st.divider()
    st.write("### 💾 حفظ التحليل" if st.session_state.language == 'العربية' else "### 💾 Save Analysis")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("احفظ هذا التحليل لمراجعته لاحقاً من صفحة 'سجل التحليلات'" if st.session_state.language == 'العربية' else "Save this analysis to review it later from 'Analysis History' page")
    with col2:
        button_text = "💾 حفظ التحليل" if st.session_state.language == 'العربية' else "💾 Save Analysis"
        if st.button(button_text, type="primary", use_container_width=True):
            with st.spinner("جاري حفظ التحليل..." if st.session_state.language == 'العربية' else "Saving analysis..."):
                from database import save_analysis, delete_old_analyses
                
                analysis_id = save_analysis(df, st.session_state.username)
                
                if analysis_id:
                    success_msg = f"✅ تم حفظ التحليل بنجاح! (رقم #{analysis_id})" if st.session_state.language == 'العربية' else f"✅ Analysis saved successfully! (ID #{analysis_id})"
                    st.success(success_msg)
                    st.session_state.last_analysis_saved = True
                    
                    delete_old_analyses(st.session_state.username, keep_count=10)
                else:
                    error_msg = "❌ فشل حفظ التحليل" if st.session_state.language == 'العربية' else "❌ Failed to save analysis"
                    st.error(error_msg)
    
    # ========== نهاية الإضافة ========== ⬆️⬆️⬆️

# Marketing Automation Page - الصفحة الجديدة# Marketing Automation Page
elif page == get_text('marketing_automation'):
    st.header(get_text('marketing_automation_title'))
    
    tab1, tab2, tab3 = st.tabs([
        get_text('segment_actions'),
        get_text('auto_recommendations'),
        get_text('campaign_results')
    ])
    
    with tab1:
        st.subheader(get_text('segment_actions'))

# Marketing Automation Page - الصفحة الجديدة
    tab1, tab2, tab3 = st.tabs([
        get_text('segment_actions'),
        get_text('auto_recommendations'),
        get_text('campaign_results')
    ])
    
    with tab1:
        st.subheader(get_text('segment_actions'))
        st.info("🤖 الإجراءات الآلية الموصى بها لكل شريحة عملاء" if st.session_state.language == 'العربية' else "🤖 Automated actions recommended for each customer segment")
        
        # عرض الإجراءات الآلية لكل شريحة
        segment_stats = df['Advanced_Segment'].value_counts()
        
        for segment in segment_stats.index:
            customer_count = segment_stats[segment]
            action_details = get_automated_segment_actions(segment, st.session_state.language)
            
            st.markdown(f"""
            <div class="automation-card">
                <h3>🎯 {segment}</h3>
                <p><strong>عدد العملاء:</strong> {customer_count}</p>
                <p><strong>الإجراء الموصى به:</strong> {action_details['action']}</p>
                <p><strong>قناة التواصل:</strong> {action_details['channel']}</p>
                <p><strong>الرسالة:</strong> {action_details['message']}</p>
                <p><strong>التأثير المتوقع:</strong> {action_details['expected_impact']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # زر تنفيذ الحملة
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button(f"🚀 تنفيذ لشريحة {segment}" if st.session_state.language == 'العربية' else f"🚀 Execute for {segment}", key=f"execute_{segment}"):
                    # محاكاة تنفيذ الحملة
                    campaign_results = simulate_campaign_execution(segment, action_details, customer_count, st.session_state.language)
                    
                    st.success(f"✅ تم تنفيذ الحملة بنجاح!" if st.session_state.language == 'العربية' else f"✅ Campaign executed successfully!")
                    st.info(campaign_results['summary'])
                    
                    # حفظ نتائج الحملة في session state
                    if 'campaign_history' not in st.session_state:
                        st.session_state.campaign_history = []
                    
                    st.session_state.campaign_history.append({
                        'segment': segment,
                        'action': action_details['action'],
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'results': campaign_results
                    })
            
            with col2:
                if st.button(f"📊 محاكاة النتائج" if st.session_state.language == 'العربية' else f"📊 Simulate Results", key=f"simulate_{segment}"):
                    campaign_results = simulate_campaign_execution(segment, action_details, customer_count, st.session_state.language)
                    
                    st.info("🎯 نتائج المحاكاة المتوقعة:" if st.session_state.language == 'العربية' else "🎯 Expected simulation results:")
                    st.metric("🛒 عمليات الشراء المتوقعة", campaign_results['expected_conversions'])
                    st.metric("📈 معدل التحويل", f"{campaign_results['conversion_rate']:.1f}%")
                    st.metric("💰 الإيرادات المتوقعة", f"${campaign_results['expected_revenue']:,.0f}")
            
            st.markdown("---")
    
    with tab2:
        st.subheader(get_text('auto_recommendations'))
        
        # توصيات آلية ذكية
        st.success("🎯 التوصيات الآلية الذكية بناءً على تحليل البيانات" if st.session_state.language == 'العربية' else "🎯 Smart automated recommendations based on data analysis")
        
        # توصية بناءً على تحليل البيانات
        total_customers = len(df)
        high_risk_count = len(high_risk)
        inactive_customers = len(df[df['Visits'] == 0])
        
        recommendations = []
        
        if high_risk_count > total_customers * 0.2:
            recommendations.append({
                'priority': 'high',
                'message': '🚨 تنفيذ حملة إنقاذ عاجلة للعملاء المعرضين للخطر' if st.session_state.language == 'العربية' else '🚨 Execute urgent rescue campaign for at-risk customers',
                'action': 'تنفيذ فوري' if st.session_state.language == 'العربية' else 'Immediate execution'
            })
        
        if inactive_customers > total_customers * 0.15:
            recommendations.append({
                'priority': 'medium',
                'message': '🔄 حملة إعادة تفعيل للعملاء غير النشطين' if st.session_state.language == 'العربية' else '🔄 Reactivation campaign for inactive customers',
                'action': 'جدولة هذا الأسبوع' if st.session_state.language == 'العربية' else 'Schedule this week'
            })
        
        if business_metrics['retention_rate'] < 60:
            recommendations.append({
                'priority': 'high',
                'message': '💎 تحسين استراتيجية الولاء لزيادة معدل الاحتفاظ' if st.session_state.language == 'العربية' else '💎 Improve loyalty strategy to increase retention rate',
                'action': 'تطوير برنامج ولاء' if st.session_state.language == 'العربية' else 'Develop loyalty program'
            })
        
        # عرض التوصيات
        for rec in sorted(recommendations, key=lambda x: x['priority'], reverse=True):
            priority_color = "🔴" if rec['priority'] == 'high' else "🟡"
            st.markdown(f"""
            <div class="campaign-card">
                <h4>{priority_color} {rec['message']}</h4>
                <p><strong>الإجراء:</strong> {rec['action']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # توصيات مخصصة بناءً على الشرائح
        st.subheader("🎯 توصيات مخصصة للشرائح" if st.session_state.language == 'العربية' else "🎯 Customized segment recommendations")
        
        for segment in df['Advanced_Segment'].unique():
            segment_data = df[df['Advanced_Segment'] == segment]
            segment_size = len(segment_data)
            avg_churn = segment_data['Churn_Probability'].mean()
            
            if segment_size > 0:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{segment}** ({segment_size} عميل)")
                with col2:
                    if st.button(f"توصيات {segment}" if st.session_state.language == 'العربية' else f"Recommend {segment}", key=f"rec_{segment}"):
                        action_details = get_automated_segment_actions(segment, st.session_state.language)
                        st.info(f"📋 {action_details['action']}")
    
    with tab3:
        st.subheader(get_text('campaign_results'))
        
        # سجل الحملات المنفذة
        if 'campaign_history' in st.session_state and st.session_state.campaign_history:
            st.success("📊 سجل الحملات المنفذة" if st.session_state.language == 'العربية' else "📊 Campaign execution history")
            
            for campaign in reversed(st.session_state.campaign_history[-5:]):  # آخر 5 حملات
                st.markdown(f"""
                <div class="campaign-card">
                    <h4>🎯 حملة {campaign['segment']}</h4>
                    <p><strong>الإجراء:</strong> {campaign['action']}</p>
                    <p><strong>الوقت:</strong> {campaign['timestamp']}</p>
                    <p><strong>النتائج:</strong> {campaign['results']['summary']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📝 لم يتم تنفيذ أي حملات بعد. انتقل إلى علامة التبويب 'الإجراءات الآلية' لبدء التنفيذ." if st.session_state.language == 'العربية' else "📝 No campaigns executed yet. Go to the 'Automated Actions' tab to start execution.")
        
        # إحصائيات الأداء
        st.subheader("📈 إحصائيات أداء التسويق الآلي" if st.session_state.language == 'العربية' else "📈 Marketing Automation Performance Statistics")
        
        if 'campaign_history' in st.session_state and st.session_state.campaign_history:
            total_campaigns = len(st.session_state.campaign_history)
            total_expected_revenue = sum([campaign['results']['expected_revenue'] for campaign in st.session_state.campaign_history])
            total_expected_conversions = sum([campaign['results']['expected_conversions'] for campaign in st.session_state.campaign_history])
            
            col1, col2, col3 = st.columns(3)
            col1.metric("🔄 عدد الحملات", total_campaigns)
            col2.metric("🛒 إجمالي العمليات المتوقعة", total_expected_conversions)
            col3.metric("💰 إجمالي الإيرادات المتوقعة", f"${total_expected_revenue:,.0f}")
            
            # رسم بياني لأداء الحملات
            campaign_data = []
            for campaign in st.session_state.campaign_history:
                campaign_data.append({
                    'Campaign': campaign['segment'],
                    'Expected Revenue': campaign['results']['expected_revenue'],
                    'Expected Conversions': campaign['results']['expected_conversions']
                })
            
            if campaign_data:
                campaign_df = pd.DataFrame(campaign_data)
                fig = px.bar(campaign_df, x='Campaign', y='Expected Revenue', 
                             title="الإيرادات المتوقعة للحملات" if st.session_state.language == 'العربية' else "Expected Revenue by Campaign",
                             color='Expected Revenue', color_continuous_scale='viridis')
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("📊 ستظهر إحصائيات الأداء هنا بعد تنفيذ الحملات الأولى." if st.session_state.language == 'العربية' else "📊 Performance statistics will appear here after executing the first campaigns.")
# الدعم الفوري - أضف هذا السطر هنا مباشرة بعد التسويق الآلي
elif page == get_text('live_support'):
    show_chatbot(df, business_metrics, alerts)
# باقي الصفحات تبقى كما هي بدون تغيير
# [High risk customers, Smart suggestions, Data page, Advanced Analytics, Alerts System, Model comparison]
# ... (جميع الصفحات الأخرى تبقى كما هي بدون أي تغيير) ...

# High risk customers
elif page == get_text('high_risk'):
    st.header(get_text('high_risk_title'))
    risk_msg = get_text('risk_customers_found').format(len(high_risk))
    st.info(risk_msg)
    
    if len(high_risk) > 0:
        title = "Most Risky Customers" if st.session_state.language == 'English' else "العملاء الأكثر خطورة"
        fig = px.bar(high_risk, x="Name", y="Churn_Probability",
                     color="Churn_Probability", color_continuous_scale=["#f87171", "#fdba74"],
                     title=title)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        for _, r in high_risk.iterrows():
            with st.expander(f"👤 {r['Name']} — {r['Churn_Probability']:.1f}% — {r['Advanced_Segment']}"):
                st.metric("Churn Probability" if st.session_state.language == 'English' else "احتمال الرحيل", f"{r['Churn_Probability']:.1f}%")
                st.write(f"- Purchases: {int(r['Purchases'])}" if st.session_state.language == 'English' else f"- المشتريات: {int(r['Purchases'])}")
                st.write(f"- Total Value: {r['Total_Value']:.2f}" if st.session_state.language == 'English' else f"- القيمة الإجمالية: {r['Total_Value']:.2f}")
                st.write(f"- Visits: {int(r['Visits'])}" if st.session_state.language == 'English' else f"- الزيارات: {int(r['Visits'])}")
                st.write(f"- Segment: {r['Advanced_Segment']}" if st.session_state.language == 'English' else f"- الشريحة: {r['Advanced_Segment']}")
                
                suggestions_data = get_smart_suggestions(
                    r['Churn_Probability'], 
                    r['Total_Value'], 
                    r['Purchases'], 
                    r['Visits']
                )
                for i, s in enumerate(suggestions_data['suggestions'], 1):
                    st.markdown(f"- **{i}.** {s}")
                    
                if suggestions_data['ai_note']:
                    st.info(suggestions_data['ai_note'])
    else:
        st.success(get_text('no_high_risk'))

# Smart suggestions
elif page == get_text('suggestions'):
    st.header(get_text('smart_suggestions'))
    selected_customer = st.selectbox(get_text('select_customer'), df['Name'].tolist())
    
    if selected_customer:
        customer = df[df['Name'] == selected_customer].iloc[0]
        suggestions_data = get_smart_suggestions(
            float(customer['Churn_Probability']), 
            float(customer['Total_Value']), 
            int(customer['Purchases']), 
            int(customer['Visits'])
        )
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👤 Name" if st.session_state.language == 'English' else "👤 الاسم", customer['Name'])
        col2.metric("💰 Total Value" if st.session_state.language == 'English' else "💰 القيمة الكلية", f"${customer['Total_Value']:.2f}")
        col3.metric("🛒 Purchases" if st.session_state.language == 'English' else "🛒 المشتريات", int(customer['Purchases']))
        col4.metric("📍 Visits" if st.session_state.language == 'English' else "📍 الزيارات", int(customer['Visits']))
        
        st.divider()
        st.markdown(f"### {get_text('risk_level')} {suggestions_data['priority']}")
        st.markdown(f"### {get_text('category')} **{suggestions_data['category']}**")
        st.markdown(f"### 📊 Advanced Segment: **{customer['Advanced_Segment']}**")
        st.markdown(f"### {get_text('churn_probability')} **{customer['Churn_Probability']:.1f}%**")
        st.divider()
        st.markdown(f"### {get_text('proposed_suggestions')}")
        
        box_class = "suggestion-box" if customer['Churn_Probability'] <= 50 else ("warning-box" if customer['Churn_Probability'] <= 70 else "danger-box")
        for i, suggestion in enumerate(suggestions_data['suggestions'], 1):
            st.markdown(f"""<div class="{box_class}">{i}. {suggestion}</div>""", unsafe_allow_html=True)
            
        if suggestions_data['ai_note']:
            st.info(suggestions_data['ai_note'])
            
        st.divider()
        st.markdown(f"### {get_text('recommended_actions')}")
        for i, action in enumerate(suggestions_data['actions'], 1):
            st.write(f"**{i}. {action}**")

# Data page
elif page == get_text('customer_data'):
    st.header(get_text('customer_data_title'))
    view = st.radio("Choose view method:" if st.session_state.language == 'English' else "اختر طريقة العرض:", 
                  get_text('view_options'), horizontal=True)
    
    if view == get_text('view_options')[0]:  # Best model result
        show_df = df[['Name','Purchases','Total_Value','Visits','Churn_Probability', 'Advanced_Segment']].copy()
        show_df['Churn_Probability'] = show_df['Churn_Probability'].apply(lambda x: f"{x:.1f}%")
        
        if st.session_state.language == 'English':
            show_df.columns = ['Name', 'Purchases', 'Value', 'Visits', 'Churn Probability', 'Advanced Segment']
        else:
            show_df.columns = ['الاسم', 'المشتريات', 'القيمة', 'الزيارات', 'احتمال الرحيل', 'الشريحة المتقدمة']
            
        st.dataframe(show_df, width='stretch')
        
    elif view == get_text('view_options')[1]:  # Three models comparison
        show_df = df[['Name','Churn_Probability_RF','Churn_Probability_XGB','Churn_Probability', 'Advanced_Segment']].copy()
        show_df['Difference'] = abs(show_df['Churn_Probability_RF'] - show_df['Churn_Probability_XGB'])
        
        for col in ['Churn_Probability_RF','Churn_Probability_XGB','Churn_Probability','Difference']:
            show_df[col] = show_df[col].apply(lambda x: f"{x:.1f}%")
            
        if st.session_state.language == 'English':
            show_df.columns = ['Name', 'Random Forest', 'XGBoost', 'Best', 'Advanced Segment', 'Difference']
        else:
            show_df.columns = ['الاسم', 'Random Forest', 'XGBoost', 'الأفضل', 'الشريحة المتقدمة', 'الفرق']
            
        st.dataframe(show_df, width='stretch')
        
        st.write("#### Model Comparison Chart (First 10 Customers)" if st.session_state.language == 'English' else "#### رسم بياني للمقارنة (أول 10 عملاء)")
        top_df = df.head(10)
        fig = go.Figure()
        fig.add_trace(go.Bar(name='RF', x=top_df['Name'], y=top_df['Churn_Probability_RF']))
        fig.add_trace(go.Bar(name='XGB', x=top_df['Name'], y=top_df['Churn_Probability_XGB']))
        fig.add_trace(go.Bar(name='Best' if st.session_state.language == 'English' else 'الأفضل', x=top_df['Name'], y=top_df['Churn_Probability']))
        fig.update_layout(title="Model Comparison" if st.session_state.language == 'English' else "مقارنة النماذج", barmode='group', height=400)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
    else:  # Full advanced details
        show_df = df.copy()
        if st.session_state.language == 'English':
            show_df['Classification'] = show_df['Churn_Probability'].apply(lambda x: '✅ Loyal' if x <= 30 else ('⚠️ Medium' if x <= 70 else '🚨 At Risk'))
            show_df_display = show_df[['Name','Purchases','Total_Value','Visits','Churn_Probability_RF','Churn_Probability_XGB','Churn_Probability','Advanced_Segment','Classification']].copy()
            for col in ['Churn_Probability_RF','Churn_Probability_XGB','Churn_Probability']:
                show_df_display[col] = show_df_display[col].apply(lambda x: f"{x:.1f}%")
            show_df_display.columns = ['Name', 'Purchases', 'Value', 'Visits', 'RF %', 'XGB %', 'Best %', 'Advanced Segment', 'Final Classification']
        else:
            show_df['تصنيف'] = show_df['Churn_Probability'].apply(lambda x: '✅ مخلص' if x <= 30 else ('⚠️ متوسط' if x <= 70 else '🚨 معرض للرحيل'))
            show_df_display = show_df[['Name','Purchases','Total_Value','Visits','Churn_Probability_RF','Churn_Probability_XGB','Churn_Probability','Advanced_Segment','تصنيف']].copy()
            for col in ['Churn_Probability_RF','Churn_Probability_XGB','Churn_Probability']:
                show_df_display[col] = show_df_display[col].apply(lambda x: f"{x:.1f}%")
            show_df_display.columns = ['الاسم', 'المشتريات', 'القيمة', 'الزيارات', 'RF %', 'XGB %', 'الأفضل %', 'الشريحة المتقدمة', 'التصنيف النهائي']
            
        st.dataframe(show_df_display, width='stretch')

# Advanced Analytics Page
elif page == get_text('advanced_analytics'):
    if st.session_state.get('subscription') != 'vip':
        st.warning('⚠️ التحليلات المتقدمة حصرية لباقة VIP!' if st.session_state.language == 'العربية' else '⚠️ Advanced Analytics exclusive to VIP!')
        st.info('👑 قم بالترقية لـ VIP' if st.session_state.language == 'العربية' else '👑 Upgrade to VIP')
        st.stop()
    st.header(get_text('advanced_analytics_title'))
    
    tab1, tab2, tab3, tab4 = st.tabs([
        get_text('customer_segmentation'),
        get_text('business_metrics'),
        get_text('retention_analysis'),
        get_text('lifetime_value')
    ])
    
    with tab1:
        st.subheader(get_text('customer_segmentation'))
        
        # عرض إحصائيات الشرائح المتقدمة
        segment_stats = df['Advanced_Segment'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(values=segment_stats.values, names=segment_stats.index,
                         title="توزيع الشرائح المتقدمة" if st.session_state.language == 'العربية' else "Advanced Segments Distribution")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            # إحصائيات مفصلة لكل شريحة
            for segment in segment_stats.index:
                segment_data = df[df['Advanced_Segment'] == segment]
                avg_churn = segment_data['Churn_Probability'].mean()
                avg_value = segment_data['Total_Value'].mean()
                
                st.markdown(f"""
                <div class="segment-card">
                    <h4>{segment}</h4>
                    <p><strong>عدد العملاء:</strong> {len(segment_data)}</p>
                    <p><strong>متوسط احتمال الرحيل:</strong> {avg_churn:.1f}%</p>
                    <p><strong>متوسط القيمة:</strong> ${avg_value:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader(get_text('business_metrics'))
        
        # عرض مقاييس الأعمال في شبكة
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📊 معدل الاحتفاظ", f"{business_metrics['retention_rate']:.1f}%")
        m2.metric("💎 القيمة الدائمة", f"${business_metrics['ltv']:,.2f}")
        m3.metric("🔄 معدل التحويل", f"{business_metrics['conversion_rate']:.1f}%")
        m4.metric("🚀 القيمة المستقبلية", f"${df['predicted_future_value'].sum():,.2f}")
        
        # رسوم بيانية إضافية
        col1, col2 = st.columns(2)
        
        with col1:
            # توزيع القيم
            fig = px.histogram(df, x='Total_Value', nbins=20, 
                               title="توزيع قيم العملاء" if st.session_state.language == 'العربية' else "Customer Value Distribution")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            # علاقة الزيارات بالمشتريات
            fig = px.scatter(df, x='Visits', y='Purchases', color='Advanced_Segment',
                             title="العلاقة بين الزيارات والمشتريات" if st.session_state.language == 'العربية' else "Visits vs Purchases Relationship")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with tab3:
        st.subheader(get_text('retention_analysis'))
        
        # تحليل الاحتفاظ حسب الشرائح
        retention_by_segment = df.groupby('Advanced_Segment').apply(
            lambda x: (x[x['Purchases'] > 1].shape[0] / x.shape[0]) * 100
        ).reset_index()
        retention_by_segment.columns = ['Segment', 'Retention Rate']
        
        fig = px.bar(retention_by_segment, x='Segment', y='Retention Rate',
                     title="معدل الاحتفاظ حسب الشريحة" if st.session_state.language == 'العربية' else "Retention Rate by Segment")
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # عملاء جدد مقابل عملاء متكررين
        new_customers = df[df['Purchases'] <= 1].shape[0]
        repeat_customers = df[df['Purchases'] > 1].shape[0]
        
        st.write("### تحليل قاعدة العملاء" if st.session_state.language == 'العربية' else "### Customer Base Analysis")
        col1, col2 = st.columns(2)
        col1.metric("👥 عملاء جدد", new_customers)
        col2.metric("🔄 عملاء متكررين", repeat_customers)
    
    with tab4:
        st.subheader(get_text('lifetime_value'))
        
        # توزيع LTV
        fig = px.histogram(df, x='predicted_future_value', nbins=20,
                           title="توزيع القيمة الدائمة للعملاء" if st.session_state.language == 'العربية' else "Customer Lifetime Value Distribution")
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # أفضل 10 عملاء من حيث القيمة المستقبلية
        st.write("### أفضل 10 عملاء من حيث القيمة المستقبلية" if st.session_state.language == 'العربية' else "### Top 10 Customers by Future Value")
        top_value_customers = df.nlargest(10, 'predicted_future_value')[['Name', 'Total_Value', 'predicted_future_value', 'Advanced_Segment']]
        st.dataframe(top_value_customers, width='stretch')

# Alerts System Page
elif page == get_text('alerts_system'):
    st.header(get_text('alerts_title'))
    
    tab1, tab2 = st.tabs([get_text('active_alerts'), get_text('alert_settings')])
    
    with tab1:
        st.subheader(get_text('active_alerts'))
        
        if alerts:
            for alert in alerts:
                alert_class = f"alert-{alert['type']}"
                priority_icon = "🔴" if alert['priority'] == 'high' else "🟡" if alert['priority'] == 'medium' else "🔵"
                
                st.markdown(f"""
                <div class="{alert_class}">
                    {priority_icon} <strong>{alert['title']}</strong><br>
                    {alert['message']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 لا توجد تنبيهات نشطة حالياً" if st.session_state.language == 'العربية' else "🎉 No active alerts at the moment")
        
        # إحصائيات التنبيهات
        if alerts:
            st.write("### إحصائيات التنبيهات" if st.session_state.language == 'العربية' else "### Alerts Statistics")
            high_priority = len([a for a in alerts if a['priority'] == 'high'])
            medium_priority = len([a for a in alerts if a['priority'] == 'medium'])
            low_priority = len([a for a in alerts if a['priority'] == 'low'])
            
            col1, col2, col3 = st.columns(3)
            col1.metric("🔴 عالية الأولوية", high_priority)
            col2.metric("🟡 متوسطة الأولوية", medium_priority)
            col3.metric("🔵 منخفضة الأولوية", low_priority)
    
    with tab2:
        st.subheader(get_text('alert_settings'))
        
        st.info("⚙️ إعدادات نظام التنبيهات" if st.session_state.language == 'العربية' else "⚙️ Alert System Settings")
        
        # إعدادات التنبيهات
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input(
                "نسبة التنبيه للعملاء المعرضين للخطر (%)" if st.session_state.language == 'العربية' else "Alert threshold for at-risk customers (%)",
                min_value=1, max_value=100, value=20, key="risk_threshold"
            )
            
            st.number_input(
                "الحد الأدنى للعملاء غير النشطين" if st.session_state.language == 'العربية' else "Minimum inactive customers threshold",
                min_value=1, max_value=100, value=10, key="inactive_threshold"
            )
        
        with col2:
            st.number_input(
                "نسبة التنبيه للإيرادات المعرضة للخطر (%)" if st.session_state.language == 'العربية' else "Alert threshold for revenue at risk (%)",
                min_value=1, max_value=100, value=30, key="revenue_threshold"
            )
            
            st.number_input(
                "نسبة التنبيه للعملاء الجدد (%)" if st.session_state.language == 'العربية' else "Alert threshold for new customers (%)",
                min_value=1, max_value=100, value=40, key="new_customer_threshold"
            )
        
        if st.button("💾 حفظ الإعدادات" if st.session_state.language == 'العربية' else "💾 Save Settings"):
            st.success("✅ تم حفظ الإعدادات بنجاح" if st.session_state.language == 'العربية' else "✅ Settings saved successfully")

# Model comparison page
elif page == get_text('model_comparison'):
    if st.session_state.get('subscription') == 'free':
        st.warning('⚠️ هذه الميزة للباقات المدفوعة!' if st.session_state.language == 'العربية' else '⚠️ Paid plans only!')
        st.info('🚀 قم بالترقية للوصول لهذه الميزة' if st.session_state.language == 'العربية' else '🚀 Upgrade to access this feature')
        st.stop()

    st.header(get_text('model_comparison_title'))
    st.info(get_text('model_comparison_desc'))
    
    cmp_df = df[['Name','Churn_Probability_RF','Churn_Probability_XGB','Churn_Probability', 'Advanced_Segment']].copy()
    cmp_df['Diff'] = (cmp_df['Churn_Probability_RF'] - cmp_df['Churn_Probability_XGB']).abs()
    cmp_df = cmp_df.sort_values('Diff', ascending=False).head(50)
    cmp_df_display = cmp_df.copy()
    
    for col in ['Churn_Probability_RF','Churn_Probability_XGB','Churn_Probability','Diff']:
        cmp_df_display[col] = cmp_df_display[col].apply(lambda x: f"{x:.1f}%")
    
    if st.session_state.language == 'English':
        cmp_df_display.columns = ['Name', 'RF %', 'XGB %', 'Best %', 'Advanced Segment', 'Difference']
        review_note = "### Review highest differences and check training data/model features."
    else:
        cmp_df_display.columns = ['الاسم', 'RF %', 'XGB %', 'الأفضل %', 'الشريحة المتقدمة', 'الفرق']
        review_note = "### راجع أعلى الاختلافات وتحقق من بيانات التدريب/مزايا النماذج."
    
    st.dataframe(cmp_df_display, width='stretch')
    st.write(review_note)

# صفحة الاشتراكات
elif page == get_text('subscriptions'):
    show_subscription_page()
