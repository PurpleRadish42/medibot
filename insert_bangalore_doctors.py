import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
import re
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def connect_to_database():
    """Connect to MySQL database using environment variables"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=int(os.getenv('MYSQL_PORT').strip("'")),
            user=os.getenv('MYSQL_USERNAME'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE'),
            ssl_disabled=False,
            autocommit=True
        )
        print("✅ Successfully connected to MySQL database")
        return connection
    except Error as e:
        print(f"❌ Error connecting to MySQL database: {e}")
        return None

def create_doctors_table(connection):
    """Create doctors table with proper schema based on CSV analysis"""
    cursor = connection.cursor()
    
    # Drop existing table to ensure clean structure
    drop_table_query = "DROP TABLE IF EXISTS bangalore_doctors"
    
    create_table_query = """
    CREATE TABLE bangalore_doctors (
        id INT AUTO_INCREMENT PRIMARY KEY,
        entry_id INT,
        name VARCHAR(200) NOT NULL,
        specialty VARCHAR(100),
        experience_text VARCHAR(200),
        experience_years INT DEFAULT 0,
        degree TEXT,
        consultation_fee_text VARCHAR(50),
        consultation_fee_amount DECIMAL(10, 2) DEFAULT 0,
        rating DECIMAL(3, 2) DEFAULT 0,
        bangalore_location VARCHAR(150),
        google_maps_link TEXT,
        coordinates VARCHAR(100),
        latitude DECIMAL(10, 8) DEFAULT NULL,
        longitude DECIMAL(11, 8) DEFAULT NULL,
        location_index INT DEFAULT 0,
        source_url TEXT,
        scraped_at TIMESTAMP NULL,
        scraping_session VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        -- Indexes for better performance
        INDEX idx_name (name),
        INDEX idx_specialty (specialty),
        INDEX idx_location (bangalore_location),
        INDEX idx_rating (rating),
        INDEX idx_consultation_fee (consultation_fee_amount),
        INDEX idx_experience_years (experience_years),
        INDEX idx_entry_id (entry_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(drop_table_query)
        print("🗑️ Dropped existing bangalore_doctors table")
        cursor.execute(create_table_query)
        print("✅ Created new bangalore_doctors table with proper schema")
    except Error as e:
        print(f"❌ Error creating table: {e}")
    finally:
        cursor.close()

def extract_experience_years(experience_text):
    """Extract years of experience from text like '32 Years Experience Overall'"""
    if pd.isna(experience_text) or not experience_text:
        return 0
    
    # Look for patterns like "32 Years", "45 Years Experience"
    match = re.search(r'(\d+)\s*[Yy]ears?', str(experience_text))
    if match:
        try:
            return int(match.group(1))
        except:
            return 0
    return 0

def extract_consultation_fee(fee_text):
    """Extract numeric fee from text like '₹1000'"""
    if pd.isna(fee_text) or not fee_text:
        return 0
    
    # Remove currency symbols and extract numbers
    fee_str = str(fee_text).replace('₹', '').replace(',', '').strip()
    match = re.search(r'(\d+)', fee_str)
    if match:
        try:
            return float(match.group(1))
        except:
            return 0
    return 0

def extract_coordinates(coord_text):
    """Extract latitude and longitude from coordinates text"""
    if pd.isna(coord_text) or not coord_text:
        return None, None
    
    try:
        # Split by comma and extract lat, lng
        coords = str(coord_text).split(',')
        if len(coords) == 2:
            lat = float(coords[0].strip())
            lng = float(coords[1].strip())
            return lat, lng
    except:
        pass
    return None, None

def parse_scraped_at(scraped_text):
    """Parse scraped_at timestamp"""
    if pd.isna(scraped_text) or not scraped_text:
        return None
    
    try:
        # Try to parse the ISO format timestamp
        return datetime.fromisoformat(str(scraped_text).replace('T', ' ').replace('Z', ''))
    except:
        return None

def insert_bangalore_doctors_data():
    """Read CSV and insert data into MySQL database with proper data processing"""
    
    # Read the CSV file
    try:
        df = pd.read_csv('Web_Scraping/practo_scraper/data/bangalore_doctors_complete.csv')
        print(f"📊 Loaded {len(df)} rows from bangalore_doctors_complete.csv")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Show sample data for verification
        print(f"📄 Sample data:")
        pd.set_option('display.max_columns', None)
        print(df.head(2))
        
    except FileNotFoundError:
        print("❌ Error: bangalore_doctors_complete.csv file not found in Web_Scraping/practo_scraper/data/")
        return
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return
    
    # Connect to database
    connection = connect_to_database()
    if not connection:
        print("❌ Failed to connect to database")
        return
    
    # Create table with proper schema
    create_doctors_table(connection)
    
    cursor = connection.cursor()
    
    try:
        # Prepare INSERT query with all columns
        insert_query = """
        INSERT INTO bangalore_doctors (
            entry_id, name, specialty, experience_text, experience_years,
            degree, consultation_fee_text, consultation_fee_amount, rating,
            bangalore_location, google_maps_link, coordinates, latitude, longitude,
            location_index, source_url, scraped_at, scraping_session
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Process data in batches
        inserted_count = 0
        error_count = 0
        batch_size = 100
        batch_data = []
        
        print(f"🚀 Starting data processing and insertion...")
        
        for index, row in df.iterrows():
            try:
                # Extract and process each field properly
                entry_id = int(row.get('entry_id', 0)) if pd.notna(row.get('entry_id')) else 0
                name = str(row.get('name', ''))[:200] if pd.notna(row.get('name')) else ''
                specialty = str(row.get('specialty', ''))[:100] if pd.notna(row.get('specialty')) else ''
                
                experience_text = str(row.get('experience', ''))[:200] if pd.notna(row.get('experience')) else ''
                experience_years = extract_experience_years(experience_text)
                
                degree = str(row.get('degree', '')) if pd.notna(row.get('degree')) else ''
                
                consultation_fee_text = str(row.get('consultation_fee', ''))[:50] if pd.notna(row.get('consultation_fee')) else ''
                consultation_fee_amount = extract_consultation_fee(consultation_fee_text)
                
                rating = float(row.get('rating', 0)) if pd.notna(row.get('rating')) else 0.0
                
                bangalore_location = str(row.get('bangalore_location', ''))[:150] if pd.notna(row.get('bangalore_location')) else ''
                google_maps_link = str(row.get('google_maps_link', '')) if pd.notna(row.get('google_maps_link')) else ''
                
                coordinates = str(row.get('coordinates', '')) if pd.notna(row.get('coordinates')) else ''
                latitude, longitude = extract_coordinates(coordinates)
                
                location_index = int(row.get('location_index', 0)) if pd.notna(row.get('location_index')) else 0
                source_url = str(row.get('source_url', '')) if pd.notna(row.get('source_url')) else ''
                scraped_at = parse_scraped_at(row.get('scraped_at'))
                scraping_session = str(row.get('scraping_session', ''))[:50] if pd.notna(row.get('scraping_session')) else ''
                
                # Prepare data tuple
                data = (
                    entry_id, name, specialty, experience_text, experience_years,
                    degree, consultation_fee_text, consultation_fee_amount, rating,
                    bangalore_location, google_maps_link, coordinates, latitude, longitude,
                    location_index, source_url, scraped_at, scraping_session
                )
                
                batch_data.append(data)
                
                # Insert in batches
                if len(batch_data) >= batch_size:
                    cursor.executemany(insert_query, batch_data)
                    connection.commit()
                    inserted_count += len(batch_data)
                    print(f"✅ Inserted {inserted_count} records...")
                    batch_data = []
                    
            except Exception as e:
                error_count += 1
                print(f"⚠️ Error processing row {index}: {e}")
                print(f"   Row data: {dict(row)}")
                if error_count < 5:  # Show first few errors for debugging
                    print(f"   Full error details: {type(e).__name__}: {str(e)}")
                continue
        
        # Insert remaining data
        if batch_data:
            cursor.executemany(insert_query, batch_data)
            connection.commit()
            inserted_count += len(batch_data)
        
        print(f"🎉 Successfully inserted {inserted_count} doctors into the database")
        if error_count > 0:
            print(f"⚠️ {error_count} rows had errors and were skipped")
        
    except Error as e:
        print(f"❌ Error during database operation: {e}")
        connection.rollback()
    
    finally:
        cursor.close()
        connection.close()

def verify_insertion():
    """Verify that data was inserted correctly with proper analysis"""
    connection = connect_to_database()
    if not connection:
        return
    
    cursor = connection.cursor()
    
    try:
        print(f"\n{'='*60}")
        print("DATABASE VERIFICATION")
        print(f"{'='*60}")
        
        # Count total records
        cursor.execute("SELECT COUNT(*) FROM bangalore_doctors")
        count = cursor.fetchone()[0]
        print(f"📊 Total doctors in database: {count}")
        
        # Show data quality statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_doctors,
                COUNT(DISTINCT name) as unique_names,
                COUNT(DISTINCT specialty) as unique_specialties,
                AVG(experience_years) as avg_experience,
                AVG(consultation_fee_amount) as avg_fee,
                AVG(rating) as avg_rating
            FROM bangalore_doctors
        """)
        stats = cursor.fetchone()
        print(f"📈 Unique doctor names: {stats[1]}")
        print(f"🏥 Unique specialties: {stats[2]}")
        print(f"⏰ Average experience: {stats[3]:.1f} years")
        print(f"💰 Average consultation fee: ₹{stats[4]:.0f}")
        print(f"⭐ Average rating: {stats[5]:.2f}")
        
        # Show top specialties
        cursor.execute("""
            SELECT specialty, COUNT(*) as count 
            FROM bangalore_doctors 
            GROUP BY specialty 
            ORDER BY count DESC 
            LIMIT 10
        """)
        specialties = cursor.fetchall()
        print(f"\n🏥 Top 10 Specialties:")
        for spec, count in specialties:
            print(f"  {spec}: {count} doctors")
        
        # Show top locations
        cursor.execute("""
            SELECT bangalore_location, COUNT(*) as count 
            FROM bangalore_doctors 
            GROUP BY bangalore_location 
            ORDER BY count DESC 
            LIMIT 10
        """)
        locations = cursor.fetchall()
        print(f"\n📍 Top 10 Locations:")
        for loc, count in locations:
            print(f"  {loc}: {count} doctors")
        
        # Show sample of top-rated doctors
        cursor.execute("""
            SELECT name, specialty, experience_years, consultation_fee_amount, rating, bangalore_location
            FROM bangalore_doctors 
            WHERE rating > 0
            ORDER BY rating DESC, experience_years DESC
            LIMIT 5
        """)
        top_doctors = cursor.fetchall()
        print(f"\n⭐ Top 5 Rated Doctors:")
        for doctor in top_doctors:
            name, spec, exp, fee, rating, loc = doctor
            print(f"  {name} | {spec} | {exp}Y exp | ₹{fee:.0f} | {rating}⭐ | {loc}")
            
    except Error as e:
        print(f"❌ Error verifying data: {e}")
    
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    print("🚀 Starting Bangalore doctors data insertion to MySQL...")
    print("=" * 60)
    insert_bangalore_doctors_data()
    print("\n🔍 Verifying insertion...")
    verify_insertion()
    print("\n✅ Process completed!")
