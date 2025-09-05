import pandas as pd
import numpy as np

# Load the CSV file
print("Loading CSV file...")
df = pd.read_csv('Web_Scraping/practo_scraper/data/bangalore_doctors_complete.csv')

print(f'Total rows: {len(df)}')
print(f'Total columns: {len(df.columns)}')
print(f'Columns: {list(df.columns)}')
print()

print("First 3 rows:")
print(df.head(3))
print()

print("Data types and null values:")
print(df.dtypes)
print()
print("Null values per column:")
print(df.isnull().sum())
print()

print("Analysis completed!")
