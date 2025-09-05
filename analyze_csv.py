import pandas as pd
import numpy as np

def analyze_bangalore_doctors_csv():
    """Analyze the bangalore_doctors_complete.csv file thoroughly"""
    
    # Load the CSV file
    df = pd.read_csv('Web_Scraping/practo_scraper/data/bangalore_doctors_complete.csv')
    
    print('=' * 60)
    print('BANGALORE DOCTORS CSV ANALYSIS')
    print('=' * 60)
    print(f'Total rows: {len(df)}')
    print(f'Total columns: {len(df.columns)}')
    print(f'Columns: {list(df.columns)}')
    print()
    
    print('=' * 60)
    print('DATA TYPES')
    print('=' * 60)
    print(df.dtypes)
    print()
    
    print('=' * 60)
    print('FIRST 3 ROWS')
    print('=' * 60)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)
    print(df.head(3))
    print()
    
    print('=' * 60)
    print('DETAILED COLUMN ANALYSIS')
    print('=' * 60)
    
    for col in df.columns:
        print(f'COLUMN: {col}')
        print(f'  Data type: {df[col].dtype}')
        
        # Get non-null values for analysis
        non_null_values = df[col].dropna()
        
        if len(non_null_values) > 0:
            sample_values = non_null_values.head(10).tolist()
            print(f'  Sample values: {sample_values}')
            
            # If it's numeric-like, show stats
            if df[col].dtype in ['int64', 'float64']:
                print(f'  Min: {df[col].min()}')
                print(f'  Max: {df[col].max()}')
                print(f'  Mean: {df[col].mean():.2f}')
            
            # Show unique count and null info
            print(f'  Unique values: {df[col].nunique()}')
            print(f'  Null count: {df[col].isnull().sum()} ({df[col].isnull().sum()/len(df)*100:.1f}%)')
            
            # If text column, show max length
            if df[col].dtype == 'object':
                max_length = df[col].astype(str).str.len().max()
                print(f'  Max text length: {max_length}')
        else:
            print(f'  All values are null')
        
        print('-' * 40)
        print()

if __name__ == "__main__":
    analyze_bangalore_doctors_csv()
