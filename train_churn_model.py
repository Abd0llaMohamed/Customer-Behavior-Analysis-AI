import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_curve, auc,
    accuracy_score, precision_score, recall_score, f1_score
)
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier

# ==================== تحميل البيانات ====================
df = pd.read_excel('customers_churn.xlsx')
X = df[['Purchases', 'Total_Value', 'Visits']]
y = df['churned']

print("=" * 70)
print("🚀 نظام التنبؤ بالعملاء - نماذج متقدمة (Random Forest + XGBoost)")
print("=" * 70)

print("\n📊 بيانات التدريب:")
print(f"  • عدد العملاء: {len(df)}")
print(f"  • عدد الذين تركوا: {y.sum()}")
print(f"  • نسبة الرحيل: {(y.sum() / len(df) * 100):.1f}%")

# ==================== تقسيم البيانات ====================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n🔀 تقسيم البيانات:")
print(f"  • بيانات التدريب: {len(X_train)} صف")
print(f"  • بيانات الاختبار: {len(X_test)} صف")

# ==================== نموذج 1: Random Forest ====================
print("\n" + "=" * 70)
print("🌳 نموذج 1: Random Forest Classifier")
print("=" * 70)

rf_model = RandomForestClassifier(
    n_estimators=150,
    max_depth=12,
    min_samples_split=4,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)
rf_pred_proba = rf_model.predict_proba(X_test)[:, 1]

rf_accuracy = accuracy_score(y_test, rf_pred)
rf_precision = precision_score(y_test, rf_pred, zero_division=0)
rf_recall = recall_score(y_test, rf_pred, zero_division=0)
rf_f1 = f1_score(y_test, rf_pred, zero_division=0)
rf_auc = auc(*roc_curve(y_test, rf_pred_proba)[:2])

print(f"\n📊 نتائج Random Forest:")
print(f"  ✅ الدقة (Accuracy): {rf_accuracy:.2%}")
print(f"  📌 Precision: {rf_precision:.2%}")
print(f"  🎯 Recall: {rf_recall:.2%}")
print(f"  ⚖️  F1-Score: {rf_f1:.2%}")
print(f"  📈 AUC: {rf_auc:.2%}")

# ==================== نموذج 2: XGBoost ====================
print("\n" + "=" * 70)
print("⚡ نموذج 2: XGBoost Classifier (متقدم)")
print("=" * 70)

xgb_model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=7,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric='logloss'
)

xgb_model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False
)

xgb_pred = xgb_model.predict(X_test)
xgb_pred_proba = xgb_model.predict_proba(X_test)[:, 1]

xgb_accuracy = accuracy_score(y_test, xgb_pred)
xgb_precision = precision_score(y_test, xgb_pred, zero_division=0)
xgb_recall = recall_score(y_test, xgb_pred, zero_division=0)
xgb_f1 = f1_score(y_test, xgb_pred, zero_division=0)
xgb_auc = auc(*roc_curve(y_test, xgb_pred_proba)[:2])

print(f"\n📊 نتائج XGBoost:")
print(f"  ✅ الدقة (Accuracy): {xgb_accuracy:.2%}")
print(f"  📌 Precision: {xgb_precision:.2%}")
print(f"  🎯 Recall: {xgb_recall:.2%}")
print(f"  ⚖️  F1-Score: {xgb_f1:.2%}")
print(f"  📈 AUC: {xgb_auc:.2%}")

# ==================== مقارنة النماذج ====================
print("\n" + "=" * 70)
print("🏆 مقارنة النماذج")
print("=" * 70)

comparison = pd.DataFrame({
    'Random Forest': [rf_accuracy, rf_precision, rf_recall, rf_f1, rf_auc],
    'XGBoost': [xgb_accuracy, xgb_precision, xgb_recall, xgb_f1, xgb_auc],
}, index=['Accuracy', 'Precision', 'Recall', 'F1-Score', 'AUC'])

print("\n" + comparison.to_string())

# اختيار النموذج الأفضل
best_model = xgb_model if xgb_accuracy > rf_accuracy else rf_model
best_name = "XGBoost" if xgb_accuracy > rf_accuracy else "Random Forest"
best_pred_proba = xgb_pred_proba if xgb_accuracy > rf_accuracy else rf_pred_proba
best_pred = xgb_pred if xgb_accuracy > rf_accuracy else rf_pred

print(f"\n🏆 النموذج الأفضل: {best_name}")

# ==================== رسوم بيانية ====================
print("\n📊 إنشاء الرسوم البيانية...")

# ROC Curve
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
fpr_rf, tpr_rf, _ = roc_curve(y_test, rf_pred_proba)
fpr_xgb, tpr_xgb, _ = roc_curve(y_test, xgb_pred_proba)

plt.plot(fpr_rf, tpr_rf, label=f'Random Forest (AUC={rf_auc:.2f})', linewidth=2)
plt.plot(fpr_xgb, tpr_xgb, label=f'XGBoost (AUC={xgb_auc:.2f})', linewidth=2)
plt.plot([0, 1], [0, 1], 'k--', label='Random', linewidth=1)
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve Comparison')
plt.legend()
plt.grid(True, alpha=0.3)

# مقارنة الدقة
plt.subplot(1, 2, 2)
models = ['Random Forest', 'XGBoost']
accuracies = [rf_accuracy, xgb_accuracy]
colors = ['#1f77b4', '#ff7f0e']
bars = plt.bar(models, accuracies, color=colors, alpha=0.7, edgecolor='black')
plt.ylabel('Accuracy')
plt.title('Model Accuracy Comparison')
plt.ylim([0, 1])
for bar, acc in zip(bars, accuracies):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
             f'{acc:.1%}', ha='center', va='bottom', fontsize=11, fontweight='bold')
plt.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('models_comparison.png', dpi=300, bbox_inches='tight')
print("✅ تم حفظ 'models_comparison.png'")
plt.close()

# Feature Importance - XGBoost
plt.figure(figsize=(10, 6))
feature_names = ['Purchases', 'Total_Value', 'Visits']
xgb_importance = xgb_model.feature_importances_
rf_importance = rf_model.feature_importances_

x = range(len(feature_names))
width = 0.35

plt.bar([i - width/2 for i in x], rf_importance, width, label='Random Forest', alpha=0.8)
plt.bar([i + width/2 for i in x], xgb_importance, width, label='XGBoost', alpha=0.8)
plt.xlabel('Features')
plt.ylabel('Importance')
plt.title('Feature Importance Comparison')
plt.xticks(x, feature_names)
plt.legend()
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('feature_importance_comparison.png', dpi=300, bbox_inches='tight')
print("✅ تم حفظ 'feature_importance_comparison.png'")
plt.close()

# Confusion Matrix - Best Model
plt.figure(figsize=(8, 6))
cm = confusion_matrix(y_test, best_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['No Churn', 'Churn'],
            yticklabels=['No Churn', 'Churn'],
            cbar_kws={'label': 'Count'})
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.title(f'Confusion Matrix - {best_name}')
plt.tight_layout()
plt.savefig('confusion_matrix_best.png', dpi=300, bbox_inches='tight')
print("✅ تم حفظ 'confusion_matrix_best.png'")
plt.close()

# ==================== حفظ النماذج ====================
joblib.dump(xgb_model, 'xgb_churn_model.pkl')
joblib.dump(rf_model, 'rf_churn_model.pkl')
joblib.dump(best_model, 'best_churn_model.pkl')

print("\n" + "=" * 70)
print("✅ تم حفظ النماذج:")
print("  • xgb_churn_model.pkl")
print("  • rf_churn_model.pkl")
print("  • best_churn_model.pkl")
print("=" * 70)

# ==================== Cross-Validation ====================
print("\n🔄 Cross-Validation (5-Fold):")
rf_cv = cross_val_score(rf_model, X, y, cv=5, scoring='accuracy')
xgb_cv = cross_val_score(xgb_model, X, y, cv=5, scoring='accuracy')

print(f"  Random Forest: {rf_cv.mean():.2%} ± {rf_cv.std():.2%}")
print(f"  XGBoost: {xgb_cv.mean():.2%} ± {xgb_cv.std():.2%}")

# ==================== ملخص نهائي ====================
print("\n" + "=" * 70)
print("📊 الملخص النهائي")
print("=" * 70)
print(f"""
النموذج الفائز: {best_name}
─────────────────────────────────
الدقة: {max(rf_accuracy, xgb_accuracy):.1%}
Precision: {max(rf_precision, xgb_precision):.1%}
Recall: {max(rf_recall, xgb_recall):.1%}
F1-Score: {max(rf_f1, xgb_f1):.1%}
AUC: {max(rf_auc, xgb_auc):.1%}

الرسوم المحفوظة:
✓ models_comparison.png
✓ feature_importance_comparison.png
✓ confusion_matrix_best.png

الملفات المحفوظة:
✓ best_churn_model.pkl (للاستخدام)
✓ xgb_churn_model.pkl
✓ rf_churn_model.pkl
""")
