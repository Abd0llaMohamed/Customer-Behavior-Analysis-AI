# chatbot.py (النسخة النهائية - أزرار فقط)
import streamlit as st
import pandas as pd

class BusinessChatbot:
    
    def __init__(self, customer_data, business_metrics, alerts_list):
        """
        تهيئة الشات بوت بالبيانات الحية من التطبيق الرئيسي
        """
        self.df = customer_data
        self.metrics = business_metrics
        self.alerts = alerts_list
        
        # 1. الأسئلة العامة الثابتة
        self.static_qa_pairs = {
            "كيف يعمل النظام": 
                "• يحلل بيانات العملاء (مشتريات، قيمة، زيارات)\n• يتنبأ باحتمال ترك الخدمة\n• يقترح إجراءات مخصصة\n• يقدم تقارير وتحليلات",
            "ما أنواع الشرائح الموجودة": 
                "• 🏆 VIP Customers: قيمة عالية ونشاط كبير\n• 💎 Loyal High-Value: ولاء عالي وقيمة جيدة\n• 🚨 At High Risk: احتمال ترك عالي\n• 🔄 Inactive New: عملاء جدد غير نشطين\n• 📊 Standard: العملاء العاديين",
            "كيف أفسر نتائج التنبؤ": 
                "• ✅ 0-30%: عملاء مخلصين - حافظ عليهم\n• ⚠️ 30-70%: عملاء يحتاجون متابعة - قد يتركون\n• 🚨 70-100%: عملاء معرضون للخطر - تصرف فوراً",
            "ما أفضل استراتيجية للتسويق": 
                "• العملاء VIP: عروض حصرية ومميزات خاصة\n• العملاء المخلصين: برامج ولاء ومكافآت\n• العملاء المعرضين للخطر: خصومات كبيرة ومتابعة شخصية\n• العملاء الجدد: عروض ترحيبية وتوعية",
            "كيف أحمّل البيانات": 
                "1. حمّل ملف Excel أو CSV يحتوي الأعمدة: Name, Purchases, Total_Value, Visits\n2. استخدم القالب الموجود في الشريط الجانبي\n3. النظام سيتعرف على البيانات تلقائياً\n4. ستظهر النتائج فوراً في اللوحة",
            "ما الفرق بين نماذج الذكاء الاصطناعي": 
                "• 🤖 Random Forest: نموذج متوازن وموثوق\n• 🚀 XGBoost: نموذج دقيق وسريع\n• 🏆 Best Model: نختار تلقائياً أفضل نموذج لبياناتك",
        }

    def generate_dynamic_response(self, user_input):
        """
        تحليل سؤال المستخدم ومحاولة الإجابة عليه من البيانات الحية (df, metrics, alerts)
        """
        # التحقق أولاً من وجود بيانات
        if self.df is None or self.metrics is None or self.alerts is None:
            # هذه الرسالة لن تظهر إلا إذا حدث خطأ، لأن الأزرار ستكون معطلة
            return "يرجى تحميل ملف بيانات العملاء أولاً."

        query = user_input.lower().strip() # تنظيف السؤال

        # --- الإجابات المبنية على البيانات ---

        # سؤال عن عدد العملاء
        if "كم عدد العملاء" in query:
            total = len(self.df)
            return f"يوجد لدينا حالياً **{total}** عميل في البيانات التي تم تحميلها."

        # سؤال عن العملاء المعرضين للخطر
        if "كم عميل معرض" in query or "الخطر" in query and "عميل" in query:
            high_risk = len(self.df[self.df['Churn_Probability'] > 70])
            return f"يوجد **{high_risk}** عميل معرض للخطر (بنسبة أعلى من 70%)."

        # سؤال عن متوسط احتمال الرحيل
        if "ما هو متوسط" in query and ("الرحيل" in query or "churn" in query):
            avg_churn = self.df['Churn_Probability'].mean()
            return f"متوسط احتمال الرحيل لجميع العملاء هو **{avg_churn:.1f}%**."

        # سؤال عن معدل الاحتفاظ
        if "معدل الاحتفاظ" in query:
            rate = self.metrics.get('retention_rate', 0)
            return f"معدل الاحتفاظ التقديري (من بياناتك) هو **{rate:.1f}%**."

        # سؤال عن القيمة الدائمة
        if "القيمة الدائمة" in query or "ltv" in query.lower():
            ltv = self.metrics.get('ltv', 0)
            return f"القيمة الدائمة للعميل (LTV) تقدر بحوالي **${ltv:,.2f}**."

        # سؤال عن التنبيهات
        if "كم تنبيه" in query or "هل توجد تنبيهات" in query:
            if not self.alerts:
                return "🎉 لا توجد أي تنبيهات نشطة حالياً. عمل رائع!"
            else:
                titles = [a['title'] for a in self.alerts]
                response = f"نعم، يوجد **{len(self.alerts)}** تنبيهات نشطة حالياً:\n"
                for title in titles:
                    response += f"\n• 🚨 {title}"
                return response

        # سؤال عن العميل الأعلى خطورة
        if "من هو" in query and "أعلى" in query and ("خطر" in query or "رحيل" in query):
            top_customer = self.df.sort_values('Churn_Probability', ascending=False).iloc[0]
            return f"العميل الأعلى خطورة هو **{top_customer['Name']}**، بنسبة رحيل **{top_customer['Churn_Probability']:.1f}%**."

        # سؤال عن أفضل عميل (VIP)
        if "من هو" in query and ("أفضل عميل" in query or "vip" in query):
            vip_customers = self.df[self.df['Advanced_Segment'] == 'VIP Customers']
            if vip_customers.empty:
                return "لا يوجد عملاء مصنفين كـ 'VIP Customers' حالياً بناءً على التحليل."
            else:
                top_vip = vip_customers.sort_values('Total_Value', ascending=False).iloc[0]
                return f"يوجد **{len(vip_customers)}** عميل VIP. العميل الأعلى قيمة بينهم هو **{top_vip['Name']}** بإجمالي قيمة **${top_vip['Total_Value']:,.2f}**."

        # سؤال عن العميل الأكثر شراءً
        if "اكثر" in query and ("شراء" in query or "مشتريات" in query):
            top_purchaser = self.df.sort_values('Purchases', ascending=False).iloc[0]
            name = top_purchaser['Name']
            purchases = int(top_purchaser['Purchases'])
            return f"العميل صاحب أكبر عدد مشتريات هو **{name}**، بإجمالي **{purchases}** عملية شراء."

        # إذا لم يتم العثور على إجابة
        return None

    def get_response(self, user_input):
        """
        الحصول على الرد: أولاً من الأسئلة الثابتة، ثم من التحليل الديناميكي
        """
        # 1. البحث في الأسئلة الثابتة أولاً
        static_answer = self.static_qa_pairs.get(user_input)
        if static_answer:
            return static_answer
        
        # 2. إذا لم يجد، يحاول التحليل الديناميكي (بما في ذلك مفاتيح الأزرار)
        dynamic_answer = self.generate_dynamic_response(user_input)
        if dynamic_answer:
            return dynamic_answer
            
        # 3. إذا فشل كلاهما، يعطي رسالة افتراضية
        return "🤖 حدث خطأ ما. يرجى الضغط على الزر مرة أخرى."


def show_chatbot(df=None, business_metrics=None, alerts=None):
    """
    يعرض واجهة الشات بوت
    (تم تعديل هذه الدالة لإزالة مربع الإدخال الحر)
    """
    st.header("💬 مساعد الأعمال الذكي - الدعم الفوري")
    st.markdown("---")
    
    # تهيئة الشات بوت بالبيانات الحية
    chatbot = BusinessChatbot(df, business_metrics, alerts)
    
    # التحقق من تحميل البيانات لتفعيل الأزرار
    data_loaded = df is not None

    # ==== 1. قسم التحليلات السريعة (الجديد) ====
    st.subheader("📊 تحليلات سريعة (اسأل عن بياناتك الحالية)")
    
    if not data_loaded:
        st.warning("يرجى تحميل ملف بيانات العملاء أولاً لتفعيل هذه الأزرار.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("كم عدد العملاء؟ 👥", width='stretch', disabled=not data_loaded):
            st.session_state.selected_question = "كم عدد العملاء"
        if st.button("كم عدد العملاء المعرضين للخطر؟ 🚨", width='stretch', disabled=not data_loaded):
            st.session_state.selected_question = "كم عميل معرض للخطر"
        if st.button("من هو العميل الأعلى خطورة؟ 📈", width='stretch', disabled=not data_loaded):
            st.session_state.selected_question = "من هو العميل الأعلى خطورة"
    
    with col2:
        if st.button("هل توجد تنبيهات نشطة؟ 🔔", width='stretch', disabled=not data_loaded):
            st.session_state.selected_question = "هل توجد تنبيهات"
        if st.button("ما هو معدل الاحتفاظ؟ 🔁", width='stretch', disabled=not data_loaded):
            st.session_state.selected_question = "ما هو معدل الاحتفاظ"
        if st.button("من هو العميل الاكثر شراء؟ 🛒", width='stretch', disabled=not data_loaded):
            st.session_state.selected_question = "اكثر شراء" # المفتاح الذي تبحث عنه الدالة

    with col3:
        if st.button("ما هو متوسط احتمال الرحيل؟ 📉", width='stretch', disabled=not data_loaded):
            st.session_state.selected_question = "ما هو متوسط احتمال الرحيل"
        if st.button("ما هي القيمة الدائمة للعميل؟ 💎", width='stretch', disabled=not data_loaded):
            st.session_state.selected_question = "القيمة الدائمة"
        if st.button("من هو أفضل عميل VIP؟ 🏆", width='stretch', disabled=not data_loaded):
            st.session_state.selected_question = "من هو أفضل عميل vip"

    st.markdown("---")

    # ==== 2. قسم الأسئلة الشائعة (القديم) ====
    st.subheader("📋 الأسئلة الشائعة (معلومات عامة)")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("كيف يعمل النظام 🎯", width='stretch'):
            st.session_state.selected_question = "كيف يعمل النظام"
        if st.button("كيف أفسر التنبؤات 📊", width='stretch'):
            st.session_state.selected_question = "كيف أفسر نتائج التنبؤ"
        if st.button("استراتيجيات التسويق 💡", width='stretch'):
            st.session_state.selected_question = "ما أفضل استراتيجية للتسويق"
    
    with col2:
        if st.button("أنواع الشرائح 👥", width='stretch'):
            st.session_state.selected_question = "ما أنواع الشرائح الموجودة"
        if st.button("تحميل البيانات 📁", width='stretch'):
            st.session_state.selected_question = "كيف أحمّل البيانات"
        if st.button("الفرق بين النماذج 🤖", width='stretch'):
            st.session_state.selected_question = "ما الفرق بين نماذج الذكاء الاصطناعي"
    
    st.markdown("---")
    

    # ==== 4. عرض الإجابة ====
    # سيعمل هذا الجزء فقط عند الضغط على أحد الأزرار
    if 'selected_question' in st.session_state and st.session_state.selected_question:
        
        # استخدام st.session_state.selected_question كسؤال
        question = st.session_state.selected_question
        st.subheader(f"❓ سؤالك: {question}")
        
        # الحصول على الرد (سواء كان ثابتاً أو ديناميكياً)
        answer = chatbot.get_response(question)
        
        # تنسيق الإجابة
        st.success("🤖 **رد المساعد:**")
        
        # تحويل \n إلى <br> لضمان عرض الأسطر الجديدة في HTML
        answer_html = answer.replace('\n', '<br>')

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin: 10px 0;
            line-height: 1.6;
        ">
        {answer_html}
        </div>
        """, unsafe_allow_html=True)
        
        # حذف السؤال بعد عرضه لمنع التكرار
        st.session_state.selected_question = None

if __name__ == "__main__":
    show_chatbot()