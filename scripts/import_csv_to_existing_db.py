"""
Import CSV data into existing MySQL database with correct schema mapping
"""
import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

def get_db_config():
    """Get database configuration from environment variables"""
    return {
        'host': os.getenv('MYSQL_HOST'),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'user': os.getenv('MYSQL_USERNAME'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DATABASE'),
        'charset': 'utf8mb4',
        'autocommit': True
    }

def import_csv_to_existing_table(connection, csv_path):
    """Import data from CSV to existing MySQL table with correct column mapping"""
    try:
        # Read CSV file
        if not Path(csv_path).exists():
            print(f"❌ CSV file not found: {csv_path}")
            return False
        
        df = pd.read_csv(csv_path)
        print(f"📊 Loaded {len(df)} records from CSV")
        
        cursor = connection.cursor()
        
        # Get current record count
        cursor.execute("SELECT COUNT(*) FROM doctors")
        current_count = cursor.fetchone()[0]
        print(f"📊 Current database records: {current_count}")
        
        if current_count > 0:
            user_input = input(f"⚠️ Database already has {current_count} records. Do you want to:\n1. Add new records (a)\n2. Clear and replace all (r)\n3. Cancel (c)\nChoice: ").lower()
            
            if user_input == 'r':
                cursor.execute("DELETE FROM doctors")
                print("🗑️ Cleared existing data from doctors table")
            elif user_input == 'c':
                print("❌ Operation cancelled")
                return False
            elif user_input == 'a':
                print("➕ Adding new records to existing data")
            else:
                print("❌ Invalid choice")
                return False
        
        # Get the next available entry_id
        cursor.execute("SELECT COALESCE(MAX(entry_id), 0) + 1 FROM doctors")
        next_entry_id = cursor.fetchone()[0]
        
        # Prepare insert statement with correct column mapping
        insert_sql = """
        INSERT INTO doctors (
            entry_id, name, specialty, degree, experience, experience_years, 
            consultation_fee, rating, bangalore_location, latitude, longitude, 
            google_maps_link, source_url, scraped_at, scraping_session
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), 'csv_import'
        )
        """
        
        # Prepare data for insertion
        records_inserted = 0
        records_failed = 0
        
        for index, row in df.iterrows():
            try:
                # Map CSV columns to database columns
                data = (
                    next_entry_id + index,  # entry_id
                    str(row.get('name', '')),  # name
                    str(row.get('speciality', '')),  # specialty (CSV has speciality -> DB has specialty)
                    str(row.get('degree', '')),  # degree
                    f"{row.get('year_of_experience', 0)} years" if pd.notna(row.get('year_of_experience')) else "Not specified",  # experience
                    int(row.get('year_of_experience')) if pd.notna(row.get('year_of_experience')) else None,  # experience_years
                    int(row.get('consultation_fee')) if pd.notna(row.get('consultation_fee')) else None,  # consultation_fee
                    float(row.get('dp_score')) if pd.notna(row.get('dp_score')) else None,  # rating (CSV has dp_score -> DB has rating)
                    str(row.get('city', '')) if row.get('city') != 'Unknown' else str(row.get('location', '')),  # bangalore_location
                    float(row.get('latitude')) if pd.notna(row.get('latitude')) else None,  # latitude
                    float(row.get('longitude')) if pd.notna(row.get('longitude')) else None,  # longitude
                    str(row.get('google_map_link', '')),  # google_maps_link
                    str(row.get('profile_url', ''))  # source_url
                )
                
                cursor.execute(insert_sql, data)
                records_inserted += 1
                
                if records_inserted % 100 == 0:
                    print(f"📝 Inserted {records_inserted} records...")
                    
            except Exception as e:
                records_failed += 1
                print(f"❌ Failed to insert record {index}: {e}")
        
        connection.commit()
        print(f"✅ Successfully inserted {records_inserted} records")
        if records_failed > 0:
            print(f"⚠️ Failed to insert {records_failed} records")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Error importing CSV data: {e}")
        return False

def verify_data(connection):
    """Verify imported data"""
    try:
        cursor = connection.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM doctors")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total doctors in database: {total_count}")
        
        # Get specialty count
        cursor.execute("SELECT COUNT(DISTINCT specialty) FROM doctors")
        specialty_count = cursor.fetchone()[0]
        print(f"📊 Total specialties: {specialty_count}")
        
        # Get location count
        cursor.execute("SELECT COUNT(DISTINCT bangalore_location) FROM doctors")
        location_count = cursor.fetchone()[0]
        print(f"📊 Total locations: {location_count}")
        
        # Get top specialties
        cursor.execute("""
            SELECT specialty, COUNT(*) as count 
            FROM doctors 
            GROUP BY specialty 
            ORDER BY count DESC 
            LIMIT 5
        """)
        
        print("\n🔝 Top 5 specialties:")
        for specialty, count in cursor.fetchall():
            print(f"  • {specialty}: {count} doctors")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Error verifying data: {e}")

def main():
    """Main function to import data"""
    print("🏥 MediBot CSV to MySQL Import (Existing Schema)")
    print("=" * 50)
    
    # Get database configuration
    db_config = get_db_config()
    
    # Check if all required environment variables are present
    if not all([db_config['host'], db_config['user'], db_config['database']]):
        print("❌ Missing database credentials in environment variables")
        return
    
    print(f"🔄 Connecting to MySQL at {db_config['host']}:{db_config['port']}")
    print(f"📂 Database: {db_config['database']}")
    
    try:
        # Connect to database
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            print("✅ Connected to MySQL database")
            
            # Import CSV data
            csv_path = r"C:\Users\kmgs4\Documents\Christ Uni\trimester 4\nndl\project\medibot\data\bangalore_doctors_final.csv"
            print(f"\n📥 Importing data from: {csv_path}")
            
            if import_csv_to_existing_table(connection, csv_path):
                print("\n✅ Data import completed successfully")
                
                # Verify imported data
                print("\n🔍 Verifying imported data...")
                verify_data(connection)
                
            else:
                print("\n❌ Data import failed")
            
            connection.close()
            print("\n✅ Database connection closed")
            
    except Error as e:
        print(f"❌ MySQL Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
