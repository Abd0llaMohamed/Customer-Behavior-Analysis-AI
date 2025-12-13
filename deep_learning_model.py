import tensorflow as tf
from tensorflow import keras
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# تحميل البيانات
df = pd.read_excel('customers_churn.xlsx')
X = df[['Purchases', 'Total_Value', 'Visits']]
y = df['churned']

# تقسيم البيانات
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# تطبيع البيانات
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("🧠 بناء شبكة عصبية عميقة...")

# بناء الشبكة العصبية
model = keras.Sequential([
    keras.layers.Dense(128, activation='relu', input_shape=(3,)),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(16, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy', keras.metrics.AUC()]
)

# تدريب النموذج
print("⏳ جاري التدريب...")
history = model.fit(
    X_train_scaled, y_train,
    epochs=100,
    batch_size=4,
    validation_split=0.2,
    verbose=1
)

# التقييم
loss, accuracy, auc = model.evaluate(X_test_scaled, y_test)
print(f"\n📊 النتائج:")
print(f"  Loss: {loss:.4f}")
print(f"  Accuracy: {accuracy:.2%}")
print(f"  AUC: {auc:.2%}")

# حفظ النموذج
model.save('deep_learning_model.h5')
joblib.dump(scaler, 'scaler.pkl')
print("\n✅ تم حفظ النموذج: deep_learning_model.h5")
print(df.shape)
print(df['churned'].value_counts(normalize=True))

