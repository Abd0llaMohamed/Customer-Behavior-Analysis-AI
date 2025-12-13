import pandas as pd
import random

data = []
for i in range(1, 101):
    data.append({
        'ID': i,
        'Name': f'عميل {i}',
        'Purchases': random.randint(1, 25),
        'Total_Value': random.randint(100, 3000),
        'Visits': random.randint(1, 60)
    })

df = pd.DataFrame(data)
df.to_excel('customers.xlsx', index=False)
print("✅ تم إنشاء الملف: customers.xlsx")
