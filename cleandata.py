import pandas as pd
df = pd.read_csv('cleaned_ashoksalesdata.csv')
df['TM Invoice Date'] = pd.to_datetime(df['TM Invoice Date'])
df['Retail invoice Date'] = pd.to_datetime(df['Retail invoice Date'])
df['SAP Doc Date'] = pd.to_datetime(df['SAP Doc Date'])
df.to_csv('claim_data.csv')