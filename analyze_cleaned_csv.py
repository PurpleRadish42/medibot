import pandas as pd
import numpy as np
import re
from datetime import datetime

def analyze_cleaned_csv():
    """Comprehensive analysis of the cleaned CSV file"""
    
    print("=" * 80)
    print("COMPREHENSIVE ANALYSIS OF CLEANED CSV DATA")
    print("=" * 80)
    
    # Load the cleaned CSV file
    try:
        df = pd.read_csv('bangalore_doctors_cleaned.csv')
        print(f"✅ Successfully loaded cleaned CSV")
        print(f"📊 Dataset shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return
    
    print("\n" + "=" * 80)
    print("1. NULL VALUES ANALYSIS")
    print("=" * 80)
    
    null_analysis = df.isnull().sum()
    total_nulls = null_analysis.sum()
    
    if total_nulls == 0:
        print("✅ NO NULL VALUES FOUND!")
    else:
        print("❌ Found null values:")
        for col, null_count in null_analysis.items():
            if null_count > 0:
                percentage = (null_count / len(df)) * 100
                print(f"  {col}: {null_count} ({percentage:.1f}%)")
    
    print(f"\nTotal null values: {total_nulls}")
    
    print("\n" + "=" * 80)
    print("2. DATA TYPE ANALYSIS")
    print("=" * 80)
    
    for col in df.columns:
        print(f"{col}:")
        print(f"  Data Type: {df[col].dtype}")
        print(f"  Unique Values: {df[col].nunique()}")
        
    print("\n" + "=" * 80)
    print("3. COLUMN-WISE DETAILED ANALYSIS")
    print("=" * 80)
    
    # Analyze each column individually
    analyze_entry_id(df)
    analyze_name(df)
    analyze_specialty(df)
    analyze_degree(df)
    analyze_experience(df)
    analyze_experience_years(df)
    analyze_consultation_fee(df)
    analyze_rating(df)
    analyze_location(df)
    analyze_coordinates(df)
    analyze_google_maps_link(df)
    analyze_timestamps(df)
    
    print("\n" + "=" * 80)
    print("4. STATISTICAL SUMMARY")
    print("=" * 80)
    
    # Numerical columns summary
    numerical_cols = ['experience_years', 'consultation_fee', 'rating', 'latitude', 'longitude']
    print("Numerical columns statistics:")
    print(df[numerical_cols].describe())
    
    print("\n" + "=" * 80)
    print("5. SAMPLE DATA PREVIEW")
    print("=" * 80)
    print("First 5 rows:")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(df.head())

def analyze_entry_id(df):
    """Analyze entry_id column"""
    print("\n🔍 ENTRY_ID Analysis:")
    
    # Check for duplicates
    duplicates = df['entry_id'].duplicated().sum()
    print(f"  Duplicate entry_ids: {duplicates}")
    
    # Check for missing or invalid values
    invalid_ids = df['entry_id'].isnull().sum()
    print(f"  Missing entry_ids: {invalid_ids}")
    
    # Check range
    print(f"  ID range: {df['entry_id'].min()} to {df['entry_id'].max()}")

def analyze_name(df):
    """Analyze name column"""
    print("\n🔍 NAME Analysis:")
    
    # Check for missing names
    missing_names = df['name'].isnull().sum()
    empty_names = (df['name'] == '').sum()
    print(f"  Missing names: {missing_names}")
    print(f"  Empty names: {empty_names}")
    
    # Check for suspicious patterns
    suspicious_names = df[df['name'].str.contains(r'[0-9@#$%^&*()]', na=False)]
    print(f"  Names with numbers/special chars: {len(suspicious_names)}")
    
    # Check name lengths
    name_lengths = df['name'].str.len()
    print(f"  Name length range: {name_lengths.min()} to {name_lengths.max()}")
    print(f"  Average name length: {name_lengths.mean():.1f}")

def analyze_specialty(df):
    """Analyze specialty column"""
    print("\n🔍 SPECIALTY Analysis:")
    
    # Check for missing specialties
    missing_specialties = df['specialty'].isnull().sum()
    print(f"  Missing specialties: {missing_specialties}")
    
    # Show specialty distribution
    specialty_counts = df['specialty'].value_counts().head(10)
    print(f"  Total unique specialties: {df['specialty'].nunique()}")
    print("  Top 10 specialties:")
    for specialty, count in specialty_counts.items():
        print(f"    {specialty}: {count}")

def analyze_degree(df):
    """Analyze degree column"""
    print("\n🔍 DEGREE Analysis:")
    
    # Check for missing degrees
    missing_degrees = df['degree'].isnull().sum()
    print(f"  Missing degrees: {missing_degrees}")
    
    # Show degree distribution
    degree_counts = df['degree'].value_counts()
    print(f"  Total unique degrees: {df['degree'].nunique()}")
    print("  Degree distribution:")
    for degree, count in degree_counts.items():
        print(f"    {degree}: {count}")

def analyze_experience(df):
    """Analyze experience column"""
    print("\n🔍 EXPERIENCE Analysis:")
    
    # Check for missing experience
    missing_exp = df['experience'].isnull().sum()
    print(f"  Missing experience: {missing_exp}")
    
    # Show sample values
    sample_exp = df['experience'].dropna().head(10).tolist()
    print(f"  Sample experience values: {sample_exp}")

def analyze_experience_years(df):
    """Analyze experience_years column"""
    print("\n🔍 EXPERIENCE_YEARS Analysis:")
    
    # Check for missing values
    missing_years = df['experience_years'].isnull().sum()
    print(f"  Missing experience_years: {missing_years}")
    
    # Check for invalid values
    negative_years = (df['experience_years'] < 0).sum()
    excessive_years = (df['experience_years'] > 50).sum()
    zero_years = (df['experience_years'] == 0).sum()
    
    print(f"  Negative years: {negative_years}")
    print(f"  Excessive years (>50): {excessive_years}")
    print(f"  Zero years: {zero_years}")
    print(f"  Years range: {df['experience_years'].min()} to {df['experience_years'].max()}")
    print(f"  Average years: {df['experience_years'].mean():.1f}")

def analyze_consultation_fee(df):
    """Analyze consultation_fee column"""
    print("\n🔍 CONSULTATION_FEE Analysis:")
    
    # Check for missing fees
    missing_fees = df['consultation_fee'].isnull().sum()
    print(f"  Missing consultation_fee: {missing_fees}")
    
    # Check for invalid values
    zero_fees = (df['consultation_fee'] == 0).sum()
    negative_fees = (df['consultation_fee'] < 0).sum()
    excessive_fees = (df['consultation_fee'] > 5000).sum()
    low_fees = (df['consultation_fee'] < 100).sum()
    
    print(f"  Zero fees: {zero_fees}")
    print(f"  Negative fees: {negative_fees}")
    print(f"  Excessive fees (>5000): {excessive_fees}")
    print(f"  Very low fees (<100): {low_fees}")
    print(f"  Fee range: ₹{df['consultation_fee'].min()} to ₹{df['consultation_fee'].max()}")
    print(f"  Average fee: ₹{df['consultation_fee'].mean():.0f}")

def analyze_rating(df):
    """Analyze rating column"""
    print("\n🔍 RATING Analysis:")
    
    # Check for missing ratings
    missing_ratings = df['rating'].isnull().sum()
    print(f"  Missing ratings: {missing_ratings}")
    
    # Check for invalid values
    invalid_low = (df['rating'] < 0).sum()
    invalid_high = (df['rating'] > 5).sum()
    zero_ratings = (df['rating'] == 0).sum()
    
    print(f"  Invalid ratings (<0): {invalid_low}")
    print(f"  Invalid ratings (>5): {invalid_high}")
    print(f"  Zero ratings: {zero_ratings}")
    print(f"  Rating range: {df['rating'].min()} to {df['rating'].max()}")
    print(f"  Average rating: {df['rating'].mean():.2f}")

def analyze_location(df):
    """Analyze bangalore_location column"""
    print("\n🔍 BANGALORE_LOCATION Analysis:")
    
    # Check for missing locations
    missing_locations = df['bangalore_location'].isnull().sum()
    empty_locations = (df['bangalore_location'] == '').sum()
    print(f"  Missing locations: {missing_locations}")
    print(f"  Empty locations: {empty_locations}")
    
    # Show location distribution
    location_counts = df['bangalore_location'].value_counts().head(10)
    print(f"  Total unique locations: {df['bangalore_location'].nunique()}")
    print("  Top 10 locations:")
    for location, count in location_counts.items():
        print(f"    {location}: {count}")

def analyze_coordinates(df):
    """Analyze latitude and longitude columns"""
    print("\n🔍 COORDINATES Analysis:")
    
    # Check for missing coordinates
    missing_lat = df['latitude'].isnull().sum()
    missing_lng = df['longitude'].isnull().sum()
    print(f"  Missing latitude: {missing_lat}")
    print(f"  Missing longitude: {missing_lng}")
    
    # Check for invalid coordinates (outside Bangalore range)
    invalid_lat = ((df['latitude'] < 12.5) | (df['latitude'] > 13.5)).sum()
    invalid_lng = ((df['longitude'] < 77.0) | (df['longitude'] > 78.0)).sum()
    
    print(f"  Invalid latitude (outside Bangalore): {invalid_lat}")
    print(f"  Invalid longitude (outside Bangalore): {invalid_lng}")
    print(f"  Latitude range: {df['latitude'].min():.4f} to {df['latitude'].max():.4f}")
    print(f"  Longitude range: {df['longitude'].min():.4f} to {df['longitude'].max():.4f}")

def analyze_google_maps_link(df):
    """Analyze google_maps_link column"""
    print("\n🔍 GOOGLE_MAPS_LINK Analysis:")
    
    # Check for missing links
    missing_links = df['google_maps_link'].isnull().sum()
    empty_links = (df['google_maps_link'] == '').sum()
    print(f"  Missing Google Maps links: {missing_links}")
    print(f"  Empty Google Maps links: {empty_links}")
    
    # Check for valid URLs
    valid_urls = df['google_maps_link'].str.contains('http', na=False).sum()
    google_urls = df['google_maps_link'].str.contains('google.com', na=False).sum()
    
    print(f"  Valid URLs (containing 'http'): {valid_urls}")
    print(f"  Google URLs: {google_urls}")

def analyze_timestamps(df):
    """Analyze timestamp columns"""
    print("\n🔍 TIMESTAMPS Analysis:")
    
    # Check for missing timestamps
    missing_created = df['created_at'].isnull().sum()
    missing_updated = df['updated_at'].isnull().sum()
    missing_scraped = df['scraped_at'].isnull().sum()
    
    print(f"  Missing created_at: {missing_created}")
    print(f"  Missing updated_at: {missing_updated}")
    print(f"  Missing scraped_at: {missing_scraped}")

if __name__ == "__main__":
    analyze_cleaned_csv()
