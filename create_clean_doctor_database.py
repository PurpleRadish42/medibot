import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os
import re
from datetime import datetime

# Load environment variables
load_dotenv()

def clean_and_prepare_data():
    """Clean the CSV data and handle missing/invalid values with pseudo values"""
    
    print("Loading and analyzing CSV data...")
    df = pd.read_csv('Web_Scraping/practo_scraper/data/bangalore_doctors_complete.csv')
    
    print(f"Original dataset: {len(df)} rows, {len(df.columns)} columns")
    print("\nNull values per column:")
    null_counts = df.isnull().sum()
    for col, count in null_counts.items():
        if count > 0:
            print(f"  {col}: {count} null values")
    
    # Create a copy for cleaning
    df_clean = df.copy()
    
    print("\n" + "="*60)
    print("CLEANING AND FILLING MISSING VALUES")
    print("="*60)
    
    # 1. Handle missing degrees (558 missing)
    degree_defaults = [
        "MBBS", "MD", "MS", "BDS", "MDS", "BAMS", "BHMS", "BUMS", 
        "B.Sc", "M.Sc", "Diploma", "Certificate"
    ]
    missing_degree_mask = df_clean['degree'].isnull()
    # Assign default degrees based on specialty patterns
    for idx in df_clean[missing_degree_mask].index:
        specialty = str(df_clean.loc[idx, 'specialty']).lower()
        if 'dent' in specialty:
            df_clean.loc[idx, 'degree'] = "BDS"
        elif 'surg' in specialty:
            df_clean.loc[idx, 'degree'] = "MS"
        elif 'cardio' in specialty or 'neuro' in specialty or 'gastro' in specialty:
            df_clean.loc[idx, 'degree'] = "MD"
        elif 'ayurved' in specialty:
            df_clean.loc[idx, 'degree'] = "BAMS"
        elif 'homeo' in specialty:
            df_clean.loc[idx, 'degree'] = "BHMS"
        else:
            df_clean.loc[idx, 'degree'] = "MBBS"
    
    print(f"✓ Filled {missing_degree_mask.sum()} missing degrees with appropriate defaults")
    
    # 2. Handle missing ratings (382 missing)
    # Use median rating or assign reasonable default based on experience
    median_rating = df_clean['rating'].median()
    if pd.isna(median_rating):
        median_rating = 4.0  # Default fallback
    
    missing_rating_mask = df_clean['rating'].isnull()
    for idx in df_clean[missing_rating_mask].index:
        experience = df_clean.loc[idx, 'experience']
        try:
            exp_years = int(re.findall(r'\d+', str(experience))[0]) if re.findall(r'\d+', str(experience)) else 5
            if exp_years >= 15:
                df_clean.loc[idx, 'rating'] = 4.2
            elif exp_years >= 10:
                df_clean.loc[idx, 'rating'] = 4.0
            elif exp_years >= 5:
                df_clean.loc[idx, 'rating'] = 3.8
            else:
                df_clean.loc[idx, 'rating'] = 3.5
        except:
            df_clean.loc[idx, 'rating'] = median_rating
    
    print(f"✓ Filled {missing_rating_mask.sum()} missing ratings with experience-based defaults")
    
    # 3. Handle missing consultation fees (19 missing)
    # Use median fee or assign based on specialty and experience
    median_fee = df_clean['consultation_fee'].median()
    if pd.isna(median_fee):
        median_fee = 500  # Default fallback
    
    missing_fee_mask = df_clean['consultation_fee'].isnull()
    for idx in df_clean[missing_fee_mask].index:
        specialty = str(df_clean.loc[idx, 'specialty']).lower()
        experience = df_clean.loc[idx, 'experience']
        try:
            exp_years = int(re.findall(r'\d+', str(experience))[0]) if re.findall(r'\d+', str(experience)) else 5
            
            # Specialty-based fee ranges
            if any(term in specialty for term in ['cardio', 'neuro', 'oncol', 'surg']):
                base_fee = 800 + (exp_years * 20)
            elif any(term in specialty for term in ['dent', 'ortho', 'dermat']):
                base_fee = 600 + (exp_years * 15)
            elif any(term in specialty for term in ['pediatr', 'gynec', 'ophthal']):
                base_fee = 500 + (exp_years * 12)
            else:
                base_fee = 400 + (exp_years * 10)
                
            df_clean.loc[idx, 'consultation_fee'] = min(base_fee, 2000)  # Cap at 2000
        except:
            df_clean.loc[idx, 'consultation_fee'] = median_fee
    
    print(f"✓ Filled {missing_fee_mask.sum()} missing consultation fees with specialty/experience-based defaults")
    
    # 4. Handle missing Google Maps links and coordinates (2 missing each)
    missing_maps_mask = df_clean['google_maps_link'].isnull()
    missing_coords_mask = df_clean['coordinates'].isnull()
    
    for idx in df_clean[missing_maps_mask].index:
        location = df_clean.loc[idx, 'bangalore_location']
        df_clean.loc[idx, 'google_maps_link'] = f"https://maps.google.com/search/{location.replace(' ', '+')}"
    
    for idx in df_clean[missing_coords_mask].index:
        # Default Bangalore coordinates with slight variation
        df_clean.loc[idx, 'coordinates'] = "12.9716,77.5946"
    
    print(f"✓ Filled {missing_maps_mask.sum()} missing Google Maps links")
    print(f"✓ Filled {missing_coords_mask.sum()} missing coordinates")
    
    # 5. Data validation and cleaning
    print("\n" + "="*60)
    print("DATA VALIDATION AND CLEANING")
    print("="*60)
    
    # Clean experience field
    df_clean['experience_years'] = df_clean['experience'].apply(extract_experience_years)
    
    # Clean consultation fee (remove any non-numeric characters)
    df_clean['consultation_fee'] = df_clean['consultation_fee'].apply(clean_fee)
    
    # Clean rating (ensure it's between 0 and 5)
    df_clean['rating'] = df_clean['rating'].apply(lambda x: max(0, min(5, float(x))) if pd.notna(x) else 3.5)
    
    # Clean coordinates
    df_clean['latitude'] = df_clean['coordinates'].apply(lambda x: extract_latitude(x))
    df_clean['longitude'] = df_clean['coordinates'].apply(lambda x: extract_longitude(x))
    
    print("✓ Extracted experience years")
    print("✓ Cleaned consultation fees")
    print("✓ Validated ratings (0-5 range)")
    print("✓ Extracted latitude/longitude from coordinates")
    
    print(f"\nCleaned dataset: {len(df_clean)} rows")
    print("Missing values after cleaning:")
    final_nulls = df_clean.isnull().sum()
    for col, count in final_nulls.items():
        if count > 0:
            print(f"  {col}: {count} null values")
    
    return df_clean

def extract_experience_years(experience_str):
    """Extract numeric years from experience string"""
    try:
        if pd.isna(experience_str):
            return 5  # Default
        
        # Extract first number found in the string
        numbers = re.findall(r'\d+', str(experience_str))
        if numbers:
            years = int(numbers[0])
            return min(years, 50)  # Cap at 50 years
        return 5  # Default if no number found
    except:
        return 5

def clean_fee(fee_value):
    """Clean and validate consultation fee"""
    try:
        if pd.isna(fee_value):
            return 500  # Default
        
        # Remove any non-numeric characters except decimal point
        fee_str = re.sub(r'[^\d.]', '', str(fee_value))
        if fee_str:
            fee = float(fee_str)
            return max(100, min(fee, 5000))  # Range 100-5000
        return 500
    except:
        return 500

def extract_latitude(coord_str):
    """Extract latitude from coordinates string"""
    try:
        if pd.isna(coord_str):
            return 12.9716  # Default Bangalore latitude
        
        coords = str(coord_str).split(',')
        if len(coords) >= 2:
            lat = float(coords[0].strip())
            return lat if 10 <= lat <= 15 else 12.9716  # Validate Bangalore range
        return 12.9716
    except:
        return 12.9716

def extract_longitude(coord_str):
    """Extract longitude from coordinates string"""
    try:
        if pd.isna(coord_str):
            return 77.5946  # Default Bangalore longitude
        
        coords = str(coord_str).split(',')
        if len(coords) >= 2:
            lng = float(coords[1].strip())
            return lng if 75 <= lng <= 80 else 77.5946  # Validate Bangalore range
        return 77.5946
    except:
        return 77.5946

def create_database_schema():
    """Create the doctors table with proper schema"""
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        
        cursor = connection.cursor()
        
        # Drop existing table if it exists
        cursor.execute("DROP TABLE IF EXISTS doctors")
        
        # Create new table with proper schema
        create_table_query = """
        CREATE TABLE doctors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            entry_id INT NOT NULL,
            name VARCHAR(255) NOT NULL,
            specialty VARCHAR(255) NOT NULL,
            experience VARCHAR(100) NOT NULL,
            experience_years INT DEFAULT 5,
            degree VARCHAR(100) NOT NULL DEFAULT 'MBBS',
            consultation_fee DECIMAL(10, 2) NOT NULL DEFAULT 500.00,
            rating DECIMAL(3, 2) NOT NULL DEFAULT 3.50,
            bangalore_location VARCHAR(255) NOT NULL,
            google_maps_link TEXT,
            coordinates VARCHAR(50),
            latitude DECIMAL(10, 6) DEFAULT 12.971600,
            longitude DECIMAL(10, 6) DEFAULT 77.594600,
            location_index INT,
            source_url TEXT,
            scraped_at DATETIME,
            scraping_session VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_entry (entry_id),
            INDEX idx_specialty (specialty),
            INDEX idx_location (bangalore_location),
            INDEX idx_rating (rating),
            INDEX idx_fee (consultation_fee)
        )
        """
        
        cursor.execute(create_table_query)
        connection.commit()
        
        print("✓ Database table 'doctors' created successfully with proper schema")
        
        cursor.close()
        connection.close()
        
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
        return False

def insert_cleaned_data(df_clean):
    """Insert the cleaned data into MySQL database with error handling"""
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        
        cursor = connection.cursor()
        
        insert_query = """
        INSERT INTO doctors (
            entry_id, name, specialty, experience, experience_years, degree, 
            consultation_fee, rating, bangalore_location, google_maps_link, 
            coordinates, latitude, longitude, location_index, source_url, 
            scraped_at, scraping_session
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        successful_inserts = 0
        failed_inserts = 0
        error_log = []
        
        print(f"\nInserting {len(df_clean)} records into database...")
        
        for index, row in df_clean.iterrows():
            try:
                # Prepare data tuple
                data = (
                    int(row['entry_id']),
                    str(row['name'])[:255],  # Truncate if too long
                    str(row['specialty'])[:255],
                    str(row['experience'])[:100],
                    int(row['experience_years']),
                    str(row['degree'])[:100],
                    float(row['consultation_fee']),
                    float(row['rating']),
                    str(row['bangalore_location'])[:255],
                    str(row['google_maps_link']) if pd.notna(row['google_maps_link']) else None,
                    str(row['coordinates']) if pd.notna(row['coordinates']) else None,
                    float(row['latitude']),
                    float(row['longitude']),
                    int(row['location_index']) if pd.notna(row['location_index']) else None,
                    str(row['source_url']) if pd.notna(row['source_url']) else None,
                    row['scraped_at'] if pd.notna(row['scraped_at']) else None,
                    str(row['scraping_session']) if pd.notna(row['scraping_session']) else None
                )
                
                cursor.execute(insert_query, data)
                successful_inserts += 1
                
                # Commit every 100 records
                if successful_inserts % 100 == 0:
                    connection.commit()
                    print(f"  Processed {successful_inserts} records...")
                    
            except Exception as e:
                failed_inserts += 1
                error_msg = f"Row {index}: {str(e)}"
                error_log.append(error_msg)
                
                # Print only first 5 errors to avoid spam
                if failed_inserts <= 5:
                    print(f"  ⚠️  Error inserting row {index}: {e}")
        
        # Final commit
        connection.commit()
        
        print(f"\n" + "="*60)
        print("INSERTION RESULTS")
        print("="*60)
        print(f"✅ Successfully inserted: {successful_inserts} records")
        print(f"❌ Failed insertions: {failed_inserts} records")
        
        if error_log:
            print(f"\nFirst few errors:")
            for error in error_log[:5]:
                print(f"  {error}")
            
            if len(error_log) > 5:
                print(f"  ... and {len(error_log) - 5} more errors")
        
        cursor.close()
        connection.close()
        
        return successful_inserts, failed_inserts
        
    except mysql.connector.Error as err:
        print(f"❌ Database connection error: {err}")
        return 0, len(df_clean)

def main():
    """Main execution function"""
    print("🏥 MEDIBOT DOCTOR DATABASE SETUP WITH DATA CLEANING")
    print("="*70)
    
    # Step 1: Clean and prepare data
    df_clean = clean_and_prepare_data()
    
    # Step 2: Create database schema
    print(f"\n📊 Creating database schema...")
    if not create_database_schema():
        print("❌ Failed to create database schema. Aborting.")
        return
    
    # Step 3: Insert cleaned data
    print(f"\n💾 Inserting cleaned data into database...")
    successful, failed = insert_cleaned_data(df_clean)
    
    # Step 4: Final summary
    print(f"\n🎯 FINAL SUMMARY")
    print("="*70)
    print(f"📈 Total records processed: {len(df_clean)}")
    print(f"✅ Successfully inserted: {successful}")
    print(f"❌ Failed insertions: {failed}")
    print(f"📊 Success rate: {(successful/(successful+failed)*100):.1f}%")
    
    if successful > 0:
        print(f"\n🎉 Database setup completed! Your doctor database is ready to use.")
    else:
        print(f"\n⚠️  Database setup encountered issues. Please check the errors above.")

if __name__ == "__main__":
    main()
