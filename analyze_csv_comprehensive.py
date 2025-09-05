import pandas as pd
import numpy as np
import re
from datetime import datetime

def comprehensive_csv_analysis():
    """Comprehensive analysis of the bangalore_doctors_complete.csv file"""
    
    # Load the CSV file
    df = pd.read_csv('Web_Scraping/practo_scraper/data/bangalore_doctors_complete.csv')
    
    print('=' * 80)
    print('COMPREHENSIVE CSV ANALYSIS - BANGALORE DOCTORS')
    print('=' * 80)
    print(f'Total rows: {len(df)}')
    print(f'Total columns: {len(df.columns)}')
    print(f'Columns: {list(df.columns)}')
    print()
    
    # Set pandas display options for better visibility
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 100)
    
    print('=' * 80)
    print('SAMPLE DATA (First 3 rows)')
    print('=' * 80)
    print(df.head(3))
    print()
    
    print('=' * 80)
    print('DATA TYPES AND NULL ANALYSIS')
    print('=' * 80)
    for col in df.columns:
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        null_percent = (null_count / len(df)) * 100
        unique_count = df[col].nunique()
        
        print(f'{col}:')
        print(f'  Data Type: {dtype}')
        print(f'  Null Values: {null_count} ({null_percent:.1f}%)')
        print(f'  Unique Values: {unique_count}')
        
        # Show sample non-null values
        non_null_values = df[col].dropna()
        if len(non_null_values) > 0:
            sample_values = non_null_values.head(5).tolist()
            print(f'  Sample Values: {sample_values}')
            
            # Additional analysis based on column type
            if col == 'entry_id':
                print(f'  Range: {df[col].min()} to {df[col].max()}')
                duplicates = df[col].duplicated().sum()
                print(f'  Duplicates: {duplicates}')
                
            elif col == 'name':
                name_lengths = df[col].str.len()
                print(f'  Name Length: Min={name_lengths.min()}, Max={name_lengths.max()}, Avg={name_lengths.mean():.1f}')
                empty_names = df[(df[col].isna()) | (df[col] == '') | (df[col].str.strip() == '')].shape[0]
                print(f'  Empty/Blank Names: {empty_names}')
                
            elif col == 'specialty':
                specialty_lengths = df[col].str.len()
                print(f'  Specialty Length: Min={specialty_lengths.min()}, Max={specialty_lengths.max()}, Avg={specialty_lengths.mean():.1f}')
                print(f'  Top 5 Specialties: {df[col].value_counts().head().to_dict()}')
                
            elif col == 'experience':
                # Analyze experience patterns
                exp_patterns = []
                for exp in non_null_values.head(10):
                    exp_patterns.append(str(exp)[:50])
                print(f'  Experience Patterns: {exp_patterns}')
                
            elif col == 'degree':
                degree_lengths = df[col].str.len()
                print(f'  Degree Length: Min={degree_lengths.min()}, Max={degree_lengths.max()}, Avg={degree_lengths.mean():.1f}')
                
            elif col == 'consultation_fee':
                # Analyze consultation fee patterns
                fee_patterns = []
                for fee in non_null_values.head(10):
                    fee_patterns.append(str(fee))
                print(f'  Fee Patterns: {fee_patterns}')
                
            elif col == 'rating':
                if df[col].dtype in ['float64', 'int64']:
                    print(f'  Rating Range: {df[col].min()} to {df[col].max()}')
                    print(f'  Average Rating: {df[col].mean():.2f}')
                invalid_ratings = df[(df[col] < 0) | (df[col] > 5)].shape[0]
                print(f'  Invalid Ratings (not 0-5): {invalid_ratings}')
                
            elif col == 'bangalore_location':
                location_lengths = df[col].str.len()
                print(f'  Location Length: Min={location_lengths.min()}, Max={location_lengths.max()}, Avg={location_lengths.mean():.1f}')
                print(f'  Top 5 Locations: {df[col].value_counts().head().to_dict()}')
                
            elif col == 'coordinates':
                # Analyze coordinate patterns
                coord_patterns = []
                for coord in non_null_values.head(5):
                    coord_patterns.append(str(coord))
                print(f'  Coordinate Patterns: {coord_patterns}')
                
            elif col == 'location_index':
                print(f'  Location Index Range: {df[col].min()} to {df[col].max()}')
                
            elif col == 'scraped_at':
                # Analyze timestamp patterns
                timestamp_patterns = []
                for ts in non_null_values.head(5):
                    timestamp_patterns.append(str(ts))
                print(f'  Timestamp Patterns: {timestamp_patterns}')
        
        print('-' * 40)
    
    print('=' * 80)
    print('PROBLEMATIC DATA DETECTION')
    print('=' * 80)
    
    problems = {}
    
    # 1. Check for problematic names
    long_names = df[df['name'].str.len() > 200]
    empty_names = df[(df['name'].isna()) | (df['name'] == '') | (df['name'].str.strip() == '')]
    problems['long_names'] = len(long_names)
    problems['empty_names'] = len(empty_names)
    
    # 2. Check for problematic specialties
    long_specialties = df[df['specialty'].str.len() > 100]
    empty_specialties = df[(df['specialty'].isna()) | (df['specialty'] == '')]
    problems['long_specialties'] = len(long_specialties)
    problems['empty_specialties'] = len(empty_specialties)
    
    # 3. Check for invalid ratings
    invalid_ratings = df[(df['rating'] < 0) | (df['rating'] > 5) | (df['rating'].isna())]
    problems['invalid_ratings'] = len(invalid_ratings)
    
    # 4. Check for invalid entry_ids
    invalid_entry_ids = df[df['entry_id'].isna()]
    duplicate_entry_ids = df[df['entry_id'].duplicated()]
    problems['invalid_entry_ids'] = len(invalid_entry_ids)
    problems['duplicate_entry_ids'] = len(duplicate_entry_ids)
    
    # 5. Check for long locations
    long_locations = df[df['bangalore_location'].str.len() > 150]
    empty_locations = df[(df['bangalore_location'].isna()) | (df['bangalore_location'] == '')]
    problems['long_locations'] = len(long_locations)
    problems['empty_locations'] = len(empty_locations)
    
    # 6. Check for invalid coordinates
    def is_valid_coordinate(coord):
        if pd.isna(coord):
            return False
        try:
            coords = str(coord).split(',')
            if len(coords) == 2:
                lat = float(coords[0].strip())
                lng = float(coords[1].strip())
                return -90 <= lat <= 90 and -180 <= lng <= 180
        except:
            pass
        return False
    
    invalid_coordinates = df[~df['coordinates'].apply(is_valid_coordinate)]
    problems['invalid_coordinates'] = len(invalid_coordinates)
    
    # 7. Check for invalid timestamps
    def is_valid_timestamp(ts):
        if pd.isna(ts):
            return False
        try:
            datetime.fromisoformat(str(ts).replace('T', ' ').replace('Z', ''))
            return True
        except:
            return False
    
    invalid_timestamps = df[~df['scraped_at'].apply(is_valid_timestamp)]
    problems['invalid_timestamps'] = len(invalid_timestamps)
    
    print('PROBLEMS SUMMARY:')
    for problem, count in problems.items():
        if count > 0:
            print(f'  {problem}: {count} rows')
    
    total_problematic = sum(problems.values())
    print(f'\nTotal problematic entries: {total_problematic}')
    print(f'Percentage of data needing fixes: {(total_problematic / len(df)) * 100:.1f}%')
    
    print('=' * 80)
    print('RECOMMENDATIONS FOR PSEUDO VALUES')
    print('=' * 80)
    print('1. Empty names → Generate "Dr. Unknown_{entry_id}"')
    print('2. Long names → Truncate to 200 characters')
    print('3. Empty specialties → Set to "General Practitioner"')
    print('4. Long specialties → Truncate to 100 characters')
    print('5. Invalid ratings → Set to 3.0 (neutral rating)')
    print('6. Invalid entry_ids → Generate sequential IDs')
    print('7. Empty locations → Set to "Bangalore"')
    print('8. Long locations → Truncate to 150 characters')
    print('9. Invalid coordinates → Set to Bangalore center (12.9716,77.5946)')
    print('10. Invalid timestamps → Set to current timestamp')
    print('11. Empty degrees → Set to "MBBS"')
    print('12. Invalid consultation fees → Set to ₹500')
    
    return df, problems

if __name__ == "__main__":
    df, problems = comprehensive_csv_analysis()
