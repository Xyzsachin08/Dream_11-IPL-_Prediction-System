import pandas as pd

data = pd.read_csv("IPL.csv" , low_memory=False)

print(data.head())
print(data.columns)