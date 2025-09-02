#!/usr/bin/env python3
"""
CSV to Database Migration Script
Migrates doctor data from cleaned_doctors_full.csv to MySQL database
"""

import os
import pandas as pd
import pymysql
from dotenv import load_dotenv
from datetime import datetime
import sys

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get MySQL database connection"""
    mysql_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'user': os.getenv('MYSQL_USERNAME', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DATABASE', 'medibot2'),
        'charset': 'utf8mb4',
        'autocommit': False
    }
    
    return pymysql.connect(**mysql_config)

def migrate_csv_to_database(csv_path: str = "cleaned_doctors_full.csv"):
    """Migrate doctor data from CSV to database"""
    
    print(f"🔄 Starting CSV to Database Migration")
    print("=" * 50)
    
    # Check if CSV file exists
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return False
    
    try:
        # Load CSV data
        print(f"📂 Loading CSV data from {csv_path}...")
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded {len(df)} records from CSV")
        
        # Connect to database
        print("🔗 Connecting to MySQL database...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if doctors table exists
        cursor.execute("SHOW TABLES LIKE 'doctors'")
        if not cursor.fetchone():
            print("❌ Doctors table not found. Please run init_medibot2.py first.")
            return False
        
        # Check if table already has data
        cursor.execute("SELECT COUNT(*) FROM doctors")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"⚠️  Doctors table already contains {existing_count} records")
            response = input("Do you want to clear existing data and reimport? (y/N): ")
            if response.lower() == 'y':
                print("🗑️  Clearing existing data...")
                cursor.execute("DELETE FROM doctors")
                print("✅ Existing data cleared")
            else:
                print("❌ Migration cancelled")
                return False
        
        # Prepare insert query
        insert_query = """
            INSERT INTO doctors (
                city, speciality, profile_url, name, degree, 
                year_of_experience, location, dp_score, npv, 
                consultation_fee, google_map_link, scraped_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Migrate data in batches
        batch_size = 100
        total_rows = len(df)
        successful_inserts = 0
        
        print(f"📤 Migrating {total_rows} records in batches of {batch_size}...")
        
        for i in range(0, total_rows, batch_size):
            batch_end = min(i + batch_size, total_rows)
            batch_df = df.iloc[i:batch_end]
            
            batch_data = []
            for _, row in batch_df.iterrows():
                # Handle potential None/NaN values
                scraped_at = None
                if pd.notna(row['scraped_at']):
                    try:
                        # Parse the datetime string
                        scraped_at = datetime.fromisoformat(row['scraped_at'].replace('T', ' ').replace('Z', ''))
                    except:
                        scraped_at = None
                
                batch_data.append((
                    str(row['city']) if pd.notna(row['city']) else '',
                    str(row['speciality']) if pd.notna(row['speciality']) else '',
                    str(row['profile_url']) if pd.notna(row['profile_url']) else '',
                    str(row['name']) if pd.notna(row['name']) else '',
                    str(row['degree']) if pd.notna(row['degree']) else '',
                    int(row['year_of_experience']) if pd.notna(row['year_of_experience']) else 0,
                    str(row['location']) if pd.notna(row['location']) else '',
                    float(row['dp_score']) if pd.notna(row['dp_score']) else None,
                    int(row['npv']) if pd.notna(row['npv']) else 0,
                    int(row['consultation_fee']) if pd.notna(row['consultation_fee']) else 0,
                    str(row['google_map_link']) if pd.notna(row['google_map_link']) else '',
                    scraped_at
                ))
            
            # Insert batch
            cursor.executemany(insert_query, batch_data)
            successful_inserts += len(batch_data)
            
            print(f"  ✅ Processed batch {i//batch_size + 1}: {batch_end}/{total_rows} records")
        
        # Commit transaction
        conn.commit()
        
        # Verify migration
        cursor.execute("SELECT COUNT(*) FROM doctors")
        final_count = cursor.fetchone()[0]
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"   📊 Total records inserted: {successful_inserts}")
        print(f"   📊 Final database count: {final_count}")
        
        # Show some statistics
        print(f"\n📈 Database Statistics:")
        cursor.execute("SELECT COUNT(DISTINCT speciality) FROM doctors")
        specialty_count = cursor.fetchone()[0]
        print(f"   🏥 Unique specialties: {specialty_count}")
        
        cursor.execute("SELECT COUNT(DISTINCT city) FROM doctors")
        city_count = cursor.fetchone()[0]
        print(f"   🏙️  Unique cities: {city_count}")
        
        # Show top specialties
        print(f"\n🔝 Top 5 Specialties:")
        cursor.execute("""
            SELECT speciality, COUNT(*) as count 
            FROM doctors 
            GROUP BY speciality 
            ORDER BY count DESC 
            LIMIT 5
        """)
        for specialty, count in cursor.fetchall():
            print(f"   • {specialty}: {count} doctors")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def verify_migration():
    """Verify the migration was successful"""
    print(f"\n🔍 Verifying migration...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test some sample queries
        cursor.execute("SELECT COUNT(*) FROM doctors WHERE speciality = 'Cardiologist'")
        cardiologist_count = cursor.fetchone()[0]
        print(f"   ❤️  Cardiologists: {cardiologist_count}")
        
        cursor.execute("SELECT COUNT(*) FROM doctors WHERE city = 'Bangalore'")
        bangalore_count = cursor.fetchone()[0]
        print(f"   🏙️  Doctors in Bangalore: {bangalore_count}")
        
        # Test a sample doctor lookup
        cursor.execute("SELECT name, speciality, city FROM doctors LIMIT 3")
        sample_doctors = cursor.fetchall()
        print(f"   👨‍⚕️ Sample doctors:")
        for name, specialty, city in sample_doctors:
            print(f"     • Dr. {name} - {specialty} in {city}")
        
        conn.close()
        print("✅ Migration verification completed")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🏥 Doctor Database Migration Tool")
    print("=" * 50)
    
    # Check environment variables
    required_env_vars = ['MYSQL_HOST', 'MYSQL_USERNAME', 'MYSQL_PASSWORD', 'MYSQL_DATABASE']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        sys.exit(1)
    
    # Run migration
    if migrate_csv_to_database():
        verify_migration()
        print(f"\n🎉 Migration completed successfully!")
        print("You can now update your application to use the database instead of CSV.")
    else:
        print(f"\n❌ Migration failed. Please check the errors above.")
        sys.exit(1)