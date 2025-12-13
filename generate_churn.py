import pandas as pd
import random

df = pd.read_excel('customers.xlsx')
df['churned'] = df['Purchases'].apply(lambda x: 1 if random.random() < 0.2 else 0)
df.to_excel('customers_churn.xlsx', index=False)
print("تم حفظ customers_churn.xlsx")
