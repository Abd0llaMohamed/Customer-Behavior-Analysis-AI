import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("📊 اختبار دقة النماذج على البيانات")
print("="*80)

# قراءة البيانات
try:
    df = pd.read_excel('customers_kaggle_improved.xlsx')
    print(f"\n✅ تم تحميل البيانات: {len(df)} عميل")
except FileNotFoundError:
    print("\n❌ الملف غير موجود: customers_kaggle.xlsx")
    print("📥 تأكد من تشغيل كود التحويل أولاً")
    input("\nاضغط Enter للخروج...")
    exit()

# الأعمدة المستخدمة في التدريب
feature_cols = ['Purchases', 'Total_Value', 'Visits']
X = df[feature_cols].values

print(f"\n📋 الأعمدة المستخدمة: {feature_cols}")
print(f"\n📊 إحصائيات البيانات:")
print(df[feature_cols].describe())

# ========== اختبار 1: Clustering (K-Means) ==========
print("\n" + "="*80)
print("📍 اختبار 1: Clustering (K-Means)")
print("="*80)

# تطبيع البيانات
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# تجربة أعداد مختلفة من الـ clusters
print("\n🔄 جاري اختبار أعداد مختلفة من الـ clusters...")
results = []

for n_clusters in [2, 3, 4, 5]:
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    # حساب مقاييس الجودة
    silhouette = silhouette_score(X_scaled, labels)
    davies_bouldin = davies_bouldin_score(X_scaled, labels)
    calinski = calinski_harabasz_score(X_scaled, labels)

    results.append({
        'n_clusters': n_clusters,
        'silhouette': silhouette,
        'davies_bouldin': davies_bouldin,
        'calinski': calinski
    })

    print(f"\n  {n_clusters} Clusters:")
    print(f"    Silhouette Score: {silhouette:.4f} (أعلى = أفضل، المدى: -1 إلى 1)")
    print(f"    Davies-Bouldin Index: {davies_bouldin:.4f} (أقل = أفضل)")
    print(f"    Calinski-Harabasz Score: {calinski:.2f} (أعلى = أفضل)")

# الأفضل
best_silhouette = max(results, key=lambda x: x['silhouette'])
print(f"\n✅ أفضل عدد clusters حسب Silhouette: {best_silhouette['n_clusters']}")
print(f"   Silhouette Score: {best_silhouette['silhouette']:.4f}")

# ========== اختبار 2: Classification (Churn Prediction) ==========
print("\n" + "="*80)
print("📍 اختبار 2: Churn Prediction (Random Forest)")
print("="*80)

# إنشاء target متوقع (churn simulation)
# العملاء بـ Purchases قليلة و Total_Value قليلة = محتمل يتركوا
df['churn'] = ((df['Purchases'] <= df['Purchases'].quantile(0.25)) & 
               (df['Total_Value'] <= df['Total_Value'].quantile(0.25))).astype(int)

print(f"\n📊 توزيع Churn:")
print(f"   Churned (1): {df['churn'].sum()} عميل ({df['churn'].sum()/len(df)*100:.1f}%)")
print(f"   Active (0): {(1-df['churn']).sum()} عميل ({(1-df['churn']).sum()/len(df)*100:.1f}%)")

# تقسيم البيانات
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, df['churn'], test_size=0.2, random_state=42, stratify=df['churn']
)

print(f"\n📊 حجم البيانات:")
print(f"   Training: {len(X_train)} عميل")
print(f"   Testing: {len(X_test)} عميل")

# تدريب النموذج
print(f"\n🔄 جاري تدريب Random Forest...")
rf_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
rf_model.fit(X_train, y_train)

# التنبؤ
y_pred = rf_model.predict(X_test)

# حساب الدقة
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)

print(f"\n✅ نتائج النموذج:")
print(f"   Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"   Precision: {precision:.4f} ({precision*100:.2f}%)")
print(f"   Recall: {recall:.4f} ({recall*100:.2f}%)")
print(f"   F1-Score: {f1:.4f} ({f1*100:.2f}%)")

# Cross-validation
print(f"\n🔄 جاري Cross-Validation (5-fold)...")
cv_scores = cross_val_score(rf_model, X_scaled, df['churn'], cv=5, scoring='accuracy')
print(f"\n✅ Cross-Validation Scores:")
print(f"   Scores: {[f'{s:.4f}' for s in cv_scores]}")
print(f"   Mean: {cv_scores.mean():.4f} ({cv_scores.mean()*100:.2f}%)")
print(f"   Std: {cv_scores.std():.4f}")

# Feature Importance
feature_importance = pd.DataFrame({
    'Feature': feature_cols,
    'Importance': rf_model.feature_importances_
}).sort_values('Importance', ascending=False)

print(f"\n📊 أهمية الخصائص (Feature Importance):")
for idx, row in feature_importance.iterrows():
    print(f"   {row['Feature']}: {row['Importance']:.4f} ({row['Importance']*100:.1f}%)")

# ========== التقرير النهائي ==========
print("\n" + "="*80)
print("📋 التقرير النهائي")
print("="*80)

print(f"\n1️⃣ Clustering Quality:")
print(f"   ✅ Silhouette Score: {best_silhouette['silhouette']:.4f}")
if best_silhouette['silhouette'] > 0.5:
    print(f"   🎉 ممتاز - البيانات تتجمع بشكل واضح")
elif best_silhouette['silhouette'] > 0.3:
    print(f"   ✅ جيد - البيانات تتجمع بشكل معقول")
elif best_silhouette['silhouette'] > 0.2:
    print(f"   ⚠️ متوسط - البيانات تتجمع بشكل ضعيف")
else:
    print(f"   ❌ ضعيف - البيانات لا تتجمع بشكل واضح")

print(f"\n2️⃣ Classification Accuracy:")
print(f"   ✅ Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"   ✅ CV Mean Accuracy: {cv_scores.mean():.4f} ({cv_scores.mean()*100:.2f}%)")
if accuracy > 0.85:
    print(f"   🎉 دقة ممتازة")
elif accuracy > 0.75:
    print(f"   ✅ دقة جيدة")
elif accuracy > 0.65:
    print(f"   ⚠️ دقة متوسطة")
else:
    print(f"   ❌ دقة ضعيفة - البيانات تحتاج تحسين")

print(f"\n3️⃣ Data Quality Assessment:")
if df['Purchases'].std() < 0.1 and df['Visits'].std() < 0.1:
    print(f"   ⚠️ تنوع منخفض جداً في البيانات (معظم القيم متشابهة)")
    print(f"   💡 توصية: استخدم الكود المحسّن لزيادة التنوع")
elif df['Purchases'].std() < 1.0 and df['Visits'].std() < 1.0:
    print(f"   ⚠️ تنوع منخفض في البيانات")
    print(f"   💡 توصية: قد يفيد تحسين البيانات")
else:
    print(f"   ✅ تنوع جيد في البيانات")

print("\n" + "="*80)
print("✅ انتهى الاختبار")
print("="*80)

input("\n\nاضغط Enter للخروج...")