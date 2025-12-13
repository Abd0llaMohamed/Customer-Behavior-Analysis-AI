@echo off
echo Starting Customer AI Dashboard... Please wait.

REM التفعيل
call venv\Scripts\activate

REM تشغيل التطبيق باستخدام مسار Python (الأكثر ضماناً)
python -m streamlit run app.py

pause