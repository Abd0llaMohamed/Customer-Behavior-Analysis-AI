# pages/02_analysis_history.py
import streamlit as st
import pandas as pd
from database import get_user_analyses, get_analysis_details
from auth import check_session


# التحقق من الجلسة
is_logged_in, username = check_session()
if not is_logged_in:
    st.error("⚠️ يرجى تسجيل الدخول أولاً!")
    st.stop()



# إعداد اللغة
if 'language' not in st.session_state:
    st.session_state.language = 'العربية'


st.title("📜 سجل التحليلات السابقة" if st.session_state.language == 'العربية' else "📜 Analysis History")


# الحصول على التحليلات
analyses = get_user_analyses(username, limit=20)


if not analyses:
    st.info("📭 لا توجد تحليلات محفوظة بعد. قم بحفظ تحليل من لوحة القيادة." if st.session_state.language == 'العربية' else "📭 No saved analyses yet. Save an analysis from the dashboard.")
    st.stop()


# عرض عدد التحليلات
st.write(f"**عدد التحليلات المحفوظة:** {len(analyses)}" if st.session_state.language == 'العربية' else f"**Number of saved analyses:** {len(analyses)}")


# عرض التحليلات
for analysis in analyses:
    with st.expander(
        f"📊 التحليل #{analysis['id']} - {analysis['analysis_date']} ({analysis['total_customers']} عميل)" 
        if st.session_state.language == 'العربية' 
        else f"📊 Analysis #{analysis['id']} - {analysis['analysis_date']} ({analysis['total_customers']} customers)"
    ):
        # الإحصائيات الرئيسية
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "إجمالي العملاء" if st.session_state.language == 'العربية' else "Total Customers",
                analysis['total_customers']
            )
        
        with col2:
            high_risk_pct = (analysis['high_risk_count'] / analysis['total_customers'] * 100) if analysis['total_customers'] > 0 else 0
            st.metric(
                "معرضون للخطر" if st.session_state.language == 'العربية' else "At Risk",
                analysis['high_risk_count'],
                f"{high_risk_pct:.1f}%"
            )
        
        with col3:
            st.metric(
                "متوسط احتمال الرحيل" if st.session_state.language == 'العربية' else "Avg Churn Probability",
                f"{analysis['avg_churn_probability']:.1f}%"
            )
        
        with col4:
            st.metric(
                "إيرادات معرضة للخطر" if st.session_state.language == 'العربية' else "Revenue at Risk",
                f"${analysis['revenue_at_risk']:,.0f}"
            )
        
        st.divider()
        
        # معلومات إضافية
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**{'متوسط قيمة العميل' if st.session_state.language == 'العربية' else 'Avg Customer Value'}:** ${analysis['avg_customer_value']:,.2f}")
            st.write(f"**{'متوسط المشتريات' if st.session_state.language == 'العربية' else 'Avg Purchases'}:** {analysis['avg_purchases']:.1f}")
        
        with col2:
            st.write(f"**{'عملاء خطر منخفض' if st.session_state.language == 'العربية' else 'Low Risk Customers'}:** {analysis['low_risk_count']}")
            st.write(f"**{'عملاء خطر متوسط' if st.session_state.language == 'العربية' else 'Medium Risk Customers'}:** {analysis['medium_risk_count']}")
        
        with col3:
            if analysis['retention_rate']:
                st.write(f"**{'معدل الاحتفاظ' if st.session_state.language == 'العربية' else 'Retention Rate'}:** {analysis['retention_rate']:.1f}%")
            if analysis['predicted_future_value']:
                st.write(f"**{'القيمة المستقبلية' if st.session_state.language == 'العربية' else 'Future Value'}:** ${analysis['predicted_future_value']:,.0f}")
        
        # زر لعرض التفاصيل
        if st.button(
            f"عرض تفاصيل العملاء" if st.session_state.language == 'العربية' else f"View Customer Details", 
            key=f"details_{analysis['id']}"
        ):
            st.write("### تفاصيل العملاء المحللين" if st.session_state.language == 'العربية' else "### Analyzed Customers Details")
            
            details_df = get_analysis_details(analysis['id'])
            
            # عرض أعلى 10 عملاء معرضين للخطر
            st.write("**أعلى 10 عملاء معرضين للخطر:**" if st.session_state.language == 'العربية' else "**Top 10 At-Risk Customers:**")
            top_risk = details_df.head(10)[[
                'customer_name', 'purchases', 'total_value', 
                'visits', 'churn_probability_best', 'advanced_segment'
            ]].copy()
            
            if st.session_state.language == 'العربية':
                top_risk.columns = ['الاسم', 'المشتريات', 'القيمة', 'الزيارات', 'احتمال الرحيل', 'الشريحة']
            else:
                top_risk.columns = ['Name', 'Purchases', 'Value', 'Visits', 'Churn Probability', 'Segment']
            
            st.dataframe(top_risk, use_container_width=True)
            
            # زر لتحميل التفاصيل الكاملة
            csv = details_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                "📥 تحميل التفاصيل الكاملة (CSV)" if st.session_state.language == 'العربية' else "📥 Download Full Details (CSV)",
                data=csv,
                file_name=f"analysis_{analysis['id']}_details.csv",
                mime="text/csv",
                key=f"download_details_{analysis['id']}"  # ✅ أضفت key فريد
            )
