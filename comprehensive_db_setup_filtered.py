import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import re
from datetime import datetime

# Load environment variables
load_dotenv()

def clean_and_filter_data(df):
    """Clean the data and remove entries without Google Maps links or locations"""
    
    print("Original dataset shape:", df.shape)
    
    # Remove entries with missing Google Maps links or locations
    print("\nFiltering out entries without Google Maps links or locations...")
    
    # Check for missing google_maps_link
    missing_maps = df['google_maps_link'].isnull() | (df['google_maps_link'] == '') | (df['google_maps_link'] == 'N/A')
    print(f"Entries with missing Google Maps links: {missing_maps.sum()}")
    
    # Check for missing bangalore_location
    missing_location = df['bangalore_location'].isnull() | (df['bangalore_location'] == '') | (df['bangalore_location'] == 'N/A')
    print(f"Entries with missing bangalore_location: {missing_location.sum()}")
    
    # Remove entries that have either missing maps OR missing location
    entries_to_remove = missing_maps | missing_location
    print(f"Total entries to be removed: {entries_to_remove.sum()}")
    
    # Filter the dataframe
    df_filtered = df[~entries_to_remove].copy()
    print(f"Filtered dataset shape: {df_filtered.shape}")
    print(f"Removed {len(df) - len(df_filtered)} entries")
    
    return df_filtered

def assign_missing_degree(specialty):
    """Assign appropriate degree based on specialty"""
    specialty_lower = str(specialty).lower()
    
    if 'dentist' in specialty_lower or 'dental' in specialty_lower:
        return 'BDS'
    elif 'surgeon' in specialty_lower or 'surgery' in specialty_lower:
        return 'MS'
    elif any(word in specialty_lower for word in ['cardiologist', 'neurologist', 'dermatologist', 
                                                  'pediatrician', 'psychiatrist', 'gynecologist']):
        return 'MD'
    elif 'physiotherapist' in specialty_lower:
        return 'BPT'
    else:
        return 'MBBS'

def assign_missing_rating(experience_years):
    """Assign rating based on experience"""
    if experience_years >= 15:
        return 4.2
    elif experience_years >= 10:
        return 4.0
    elif experience_years >= 5:
        return 3.8
    else:
        return 3.5

def calculate_consultation_fee(specialty, experience_years, has_rating=True):
    """Calculate consultation fee based on specialty and experience"""
    base_fee = 300
    
    # Specialty multipliers
    specialty_lower = str(specialty).lower()
    if any(word in specialty_lower for word in ['cardiologist', 'neurologist', 'surgeon']):
        base_fee = 800
    elif any(word in specialty_lower for word in ['dermatologist', 'psychiatrist', 'gynecologist']):
        base_fee = 600
    elif 'dentist' in specialty_lower:
        base_fee = 500
    
    # Experience bonus
    experience_bonus = min(experience_years * 20, 200)
    
    # Rating bonus
    rating_bonus = 50 if has_rating else 0
    
    return base_fee + experience_bonus + rating_bonus

def extract_experience_years(experience_str):
    """Extract numeric years from experience string"""
    if pd.isna(experience_str):
        return 1
    
    # Look for patterns like "5 Years", "10+ Years", etc.
    match = re.search(r'(\d+)', str(experience_str))
    if match:
        return int(match.group(1))
    return 1

def extract_coordinates(coord_str):
    """Extract latitude and longitude from coordinates string"""
    if pd.isna(coord_str) or coord_str == '':
        # Default Bangalore coordinates
        return 12.9716, 77.5946
    
    try:
        # Look for patterns like "12.9716, 77.5946" or "(12.9716, 77.5946)"
        coord_str = str(coord_str).replace('(', '').replace(')', '')
        coords = coord_str.split(',')
        if len(coords) == 2:
            lat = float(coords[0].strip())
            lng = float(coords[1].strip())
            
            # Validate coordinates are in Bangalore area
            if 12.8 <= lat <= 13.2 and 77.3 <= lng <= 77.8:
                return lat, lng
    except:
        pass
    
    # Return default Bangalore coordinates if parsing fails
    return 12.9716, 77.5946

def create_database_and_table():
    """Create the doctors table with proper schema"""
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            database=os.getenv('MYSQL_DATABASE'),
            user=os.getenv('MYSQL_USERNAME'),
            password=os.getenv('MYSQL_PASSWORD'),
            port=int(os.getenv('MYSQL_PORT', 25060)),
            ssl_disabled=False
        )
        
        cursor = connection.cursor()
        
        # Drop existing table if it exists
        cursor.execute("DROP TABLE IF EXISTS doctors")
        print("Dropped existing doctors table")
        
        # Create new table with proper schema
        create_table_query = """
        CREATE TABLE doctors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            entry_id INT NOT NULL,
            name VARCHAR(255) NOT NULL,
            specialty VARCHAR(255) NOT NULL,
            experience VARCHAR(100) NOT NULL,
            experience_years INT DEFAULT 1,
            degree VARCHAR(100) NOT NULL,
            consultation_fee INT NOT NULL DEFAULT 300,
            rating DECIMAL(2,1) DEFAULT 3.5,
            bangalore_location TEXT NOT NULL,
            google_maps_link TEXT NOT NULL,
            latitude DECIMAL(10, 8) DEFAULT 12.9716,
            longitude DECIMAL(11, 8) DEFAULT 77.5946,
            location_index INT DEFAULT 0,
            source_url TEXT,
            scraped_at DATETIME,
            scraping_session VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_specialty (specialty),
            INDEX idx_location (bangalore_location(100)),
            INDEX idx_rating (rating),
            INDEX idx_fee (consultation_fee),
            INDEX idx_experience (experience_years)
        )
        """
        
        cursor.execute(create_table_query)
        print("Created doctors table with proper schema")
        
        return connection, cursor
        
    except Error as e:
        print(f"Error creating database table: {e}")
        return None, None

def clean_and_insert_data():
    """Main function to clean data and insert into MySQL"""
    
    print("Starting comprehensive database setup with data filtering...")
    
    # Load CSV data
    print("Loading CSV data...")
    df = pd.read_csv('Web_Scraping/practo_scraper/data/bangalore_doctors_complete.csv')
    
    # First filter out entries without Google Maps or location
    df_filtered = clean_and_filter_data(df)
    
    # Create database connection
    connection, cursor = create_database_and_table()
    if not connection:
        return
    
    print("\nStarting data cleaning and insertion...")
    
    inserted_count = 0
    error_count = 0
    batch_size = 100
    
    try:
        for index, row in df_filtered.iterrows():
            try:
                # Extract and clean data
                entry_id = int(row['entry_id']) if pd.notna(row['entry_id']) else index
                name = str(row['name']).strip()
                specialty = str(row['specialty']).strip()
                experience = str(row['experience']).strip()
                experience_years = extract_experience_years(experience)
                
                # Handle missing degree
                degree = row['degree'] if pd.notna(row['degree']) and row['degree'] != '' else assign_missing_degree(specialty)
                degree = str(degree).strip()
                
                # Handle missing consultation fee
                if pd.notna(row['consultation_fee']) and row['consultation_fee'] != '':
                    try:
                        consultation_fee = int(float(row['consultation_fee']))
                        consultation_fee = max(100, min(consultation_fee, 5000))  # Clamp between 100-5000
                    except:
                        consultation_fee = calculate_consultation_fee(specialty, experience_years)
                else:
                    consultation_fee = calculate_consultation_fee(specialty, experience_years)
                
                # Handle missing rating
                if pd.notna(row['rating']) and row['rating'] != '':
                    try:
                        rating = float(row['rating'])
                        rating = max(0.0, min(rating, 5.0))  # Clamp between 0-5
                    except:
                        rating = assign_missing_rating(experience_years)
                else:
                    rating = assign_missing_rating(experience_years)
                
                # These should not be missing after filtering, but double-check
                bangalore_location = str(row['bangalore_location']).strip()
                google_maps_link = str(row['google_maps_link']).strip()
                
                # Extract coordinates
                latitude, longitude = extract_coordinates(row['coordinates'] if pd.notna(row['coordinates']) else '')
                
                location_index = int(row['location_index']) if pd.notna(row['location_index']) else 0
                source_url = str(row['source_url']) if pd.notna(row['source_url']) else ''
                
                # Handle datetime
                scraped_at = None
                if pd.notna(row['scraped_at']):
                    try:
                        scraped_at = pd.to_datetime(row['scraped_at'])
                    except:
                        scraped_at = datetime.now()
                else:
                    scraped_at = datetime.now()
                
                scraping_session = str(row['scraping_session']) if pd.notna(row['scraping_session']) else 'default'
                
                # Insert into database
                insert_query = """
                INSERT INTO doctors (
                    entry_id, name, specialty, experience, experience_years, degree, 
                    consultation_fee, rating, bangalore_location, google_maps_link, 
                    latitude, longitude, location_index, source_url, scraped_at, scraping_session
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    entry_id, name, specialty, experience, experience_years, degree,
                    consultation_fee, rating, bangalore_location, google_maps_link,
                    latitude, longitude, location_index, source_url, scraped_at, scraping_session
                )
                
                cursor.execute(insert_query, values)
                inserted_count += 1
                
                # Commit every batch_size records
                if inserted_count % batch_size == 0:
                    connection.commit()
                    print(f"Inserted {inserted_count} records...")
                
            except Exception as e:
                error_count += 1
                print(f"Error inserting row {index}: {e}")
                continue
        
        # Final commit
        connection.commit()
        
        print(f"\n✅ Database setup completed!")
        print(f"📊 Successfully inserted: {inserted_count} records")
        print(f"❌ Failed insertions: {error_count}")
        print(f"🗂️  Total records processed: {len(df_filtered)}")
        print(f"🧹 Records removed (no maps/location): {len(df) - len(df_filtered)}")
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM doctors")
        total_in_db = cursor.fetchone()[0]
        print(f"📈 Total records in database: {total_in_db}")
        
    except Exception as e:
        print(f"Error during data insertion: {e}")
        connection.rollback()
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    clean_and_insert_data()
