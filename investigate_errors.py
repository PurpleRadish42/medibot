import pandas as pd
import numpy as np
import re
from datetime import datetime

def investigate_problematic_rows():
    """Investigate rows that might cause insertion errors"""
    
    # Load the CSV file
    df = pd.read_csv('Web_Scraping/practo_scraper/data/bangalore_doctors_complete.csv')
    
    print('=' * 60)
    print('INVESTIGATING PROBLEMATIC ROWS')
    print('=' * 60)
    print(f'Total rows: {len(df)}')
    
    error_cases = []
    
    # Check for missing critical data
    print('\n1. MISSING CRITICAL DATA:')
    missing_name = df[df['name'].isna() | (df['name'] == '')]
    if not missing_name.empty:
        print(f'   Rows with missing names: {len(missing_name)}')
        error_cases.extend(missing_name.index.tolist())
        
    missing_specialty = df[df['specialty'].isna() | (df['specialty'] == '')]
    if not missing_specialty.empty:
        print(f'   Rows with missing specialty: {len(missing_specialty)}')
        error_cases.extend(missing_specialty.index.tolist())
    
    # Check for data type issues
    print('\n2. DATA TYPE ISSUES:')
    
    # Check entry_id
    non_numeric_entry_id = df[~df['entry_id'].apply(lambda x: str(x).isdigit() if pd.notna(x) else True)]
    if not non_numeric_entry_id.empty:
        print(f'   Non-numeric entry_id: {len(non_numeric_entry_id)}')
        print(f'   Sample values: {non_numeric_entry_id["entry_id"].head().tolist()}')
        error_cases.extend(non_numeric_entry_id.index.tolist())
    
    # Check rating
    def is_valid_rating(x):
        if pd.isna(x):
            return True
        try:
            rating = float(x)
            return 0 <= rating <= 5
        except:
            return False
    
    invalid_rating = df[~df['rating'].apply(is_valid_rating)]
    if not invalid_rating.empty:
        print(f'   Invalid ratings: {len(invalid_rating)}')
        print(f'   Sample values: {invalid_rating["rating"].head().tolist()}')
        error_cases.extend(invalid_rating.index.tolist())
    
    # Check location_index
    non_numeric_location_index = df[~df['location_index'].apply(lambda x: str(x).isdigit() if pd.notna(x) else True)]
    if not non_numeric_location_index.empty:
        print(f'   Non-numeric location_index: {len(non_numeric_location_index)}')
        print(f'   Sample values: {non_numeric_location_index["location_index"].head().tolist()}')
        error_cases.extend(non_numeric_location_index.index.tolist())
    
    # Check for overly long text fields
    print('\n3. TEXT LENGTH ISSUES:')
    
    long_names = df[df['name'].str.len() > 200]
    if not long_names.empty:
        print(f'   Names longer than 200 chars: {len(long_names)}')
        for idx, row in long_names.head().iterrows():
            print(f'      Row {idx}: "{row["name"][:100]}..." ({len(row["name"])} chars)')
        error_cases.extend(long_names.index.tolist())
    
    long_specialty = df[df['specialty'].str.len() > 100]
    if not long_specialty.empty:
        print(f'   Specialties longer than 100 chars: {len(long_specialty)}')
        for idx, row in long_specialty.head().iterrows():
            print(f'      Row {idx}: "{row["specialty"][:50]}..." ({len(row["specialty"])} chars)')
        error_cases.extend(long_specialty.index.tolist())
    
    long_location = df[df['bangalore_location'].str.len() > 150]
    if not long_location.empty:
        print(f'   Locations longer than 150 chars: {len(long_location)}')
        for idx, row in long_location.head().iterrows():
            print(f'      Row {idx}: "{row["bangalore_location"][:50]}..." ({len(row["bangalore_location"])} chars)')
        error_cases.extend(long_location.index.tolist())
    
    # Check for problematic characters
    print('\n4. CHARACTER ENCODING ISSUES:')
    
    def has_problematic_chars(text):
        if pd.isna(text):
            return False
        try:
            str(text).encode('utf-8')
            return False
        except:
            return True
    
    problematic_chars = df[df.apply(lambda row: any(has_problematic_chars(row[col]) for col in ['name', 'specialty', 'degree', 'bangalore_location']), axis=1)]
    if not problematic_chars.empty:
        print(f'   Rows with encoding issues: {len(problematic_chars)}')
        error_cases.extend(problematic_chars.index.tolist())
    
    # Check for malformed timestamps
    print('\n5. TIMESTAMP ISSUES:')
    
    def is_valid_timestamp(ts):
        if pd.isna(ts):
            return True
        try:
            datetime.fromisoformat(str(ts).replace('T', ' ').replace('Z', ''))
            return True
        except:
            return False
    
    invalid_timestamps = df[~df['scraped_at'].apply(is_valid_timestamp)]
    if not invalid_timestamps.empty:
        print(f'   Invalid timestamps: {len(invalid_timestamps)}')
        print(f'   Sample values: {invalid_timestamps["scraped_at"].head().tolist()}')
        error_cases.extend(invalid_timestamps.index.tolist())
    
    # Check for malformed coordinates
    print('\n6. COORDINATE ISSUES:')
    
    def is_valid_coordinates(coord):
        if pd.isna(coord):
            return True
        try:
            coords = str(coord).split(',')
            if len(coords) == 2:
                lat = float(coords[0].strip())
                lng = float(coords[1].strip())
                return -90 <= lat <= 90 and -180 <= lng <= 180
        except:
            pass
        return False
    
    invalid_coords = df[~df['coordinates'].apply(is_valid_coordinates)]
    if not invalid_coords.empty:
        print(f'   Invalid coordinates: {len(invalid_coords)}')
        print(f'   Sample values: {invalid_coords["coordinates"].head().tolist()}')
        error_cases.extend(invalid_coords.index.tolist())
    
    # Get unique error cases
    unique_error_cases = list(set(error_cases))
    
    print(f'\n7. SUMMARY:')
    print(f'   Total problematic rows: {len(unique_error_cases)}')
    
    if unique_error_cases:
        print(f'\n8. SAMPLE PROBLEMATIC ROWS:')
        sample_error_rows = df.loc[unique_error_cases[:5]]
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', 50)
        print(sample_error_rows)
    
    return unique_error_cases

def check_database_insertion_issues():
    """Check what might have gone wrong during database insertion"""
    
    print('\n' + '=' * 60)
    print('DATABASE INSERTION ANALYSIS')
    print('=' * 60)
    
    # Load CSV and check for potential MySQL issues
    df = pd.read_csv('Web_Scraping/practo_scraper/data/bangalore_doctors_complete.csv')
    
    # Check for NULL values in required fields
    print('NULL value analysis:')
    for col in df.columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            print(f'  {col}: {null_count} NULL values ({null_count/len(df)*100:.1f}%)')
    
    # Check for duplicate entry_ids
    duplicate_entries = df[df.duplicated('entry_id')]
    if not duplicate_entries.empty:
        print(f'\nDuplicate entry_ids: {len(duplicate_entries)}')
        print(f'Sample duplicates: {duplicate_entries["entry_id"].head().tolist()}')
    
    # Check for very large numeric values that might overflow
    print('\nNumeric value ranges:')
    if 'entry_id' in df.columns:
        print(f'  entry_id range: {df["entry_id"].min()} to {df["entry_id"].max()}')
    if 'location_index' in df.columns:
        print(f'  location_index range: {df["location_index"].min()} to {df["location_index"].max()}')
    if 'rating' in df.columns:
        print(f'  rating range: {df["rating"].min()} to {df["rating"].max()}')

if __name__ == "__main__":
    problematic_rows = investigate_problematic_rows()
    check_database_insertion_issues()
    
    print(f'\n{"="*60}')
    print('RECOMMENDATION')
    print(f'{"="*60}')
    print('Run this script to identify specific issues that caused insertion failures.')
    print('Then fix the insertion script to handle these edge cases properly.')
