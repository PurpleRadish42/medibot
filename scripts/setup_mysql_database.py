"""
Setup MySQL database and import doctors data from CSV
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

def create_doctors_table(cursor):
    """Create the doctors table"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS doctors (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        speciality VARCHAR(255) NOT NULL,
        degree VARCHAR(500),
        city VARCHAR(100) NOT NULL,
        location VARCHAR(500),
        latitude DECIMAL(10, 8),
        longitude DECIMAL(11, 8),
        consultation_fee DECIMAL(10, 2),
        year_of_experience INT,
        dp_score DECIMAL(3, 2),
        profile_url TEXT,
        google_map_link TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_speciality (speciality),
        INDEX idx_city (city),
        INDEX idx_dp_score (dp_score)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    cursor.execute(create_table_sql)
    print("✅ Doctors table created successfully")

def import_csv_data(connection, csv_path):
    """Import data from CSV to MySQL database"""
    try:
        # Read CSV file
        if not Path(csv_path).exists():
            print(f"❌ CSV file not found: {csv_path}")
            return False
        
        df = pd.read_csv(csv_path)
        print(f"📊 Loaded {len(df)} records from CSV")
        
        cursor = connection.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM doctors")
        print("🗑️ Cleared existing data from doctors table")
        
        # Prepare insert statement
        insert_sql = """
        INSERT INTO doctors (
            name, speciality, degree, city, location, latitude, longitude,
            consultation_fee, year_of_experience, dp_score, profile_url, google_map_link
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        # Prepare data for insertion
        records_inserted = 0
        records_failed = 0
        
        for index, row in df.iterrows():
            try:
                data = (
                    str(row.get('name', '')),
                    str(row.get('speciality', '')),
                    str(row.get('degree', '')),
                    str(row.get('city', '')),
                    str(row.get('location', '')),
                    float(row.get('latitude')) if pd.notna(row.get('latitude')) else None,
                    float(row.get('longitude')) if pd.notna(row.get('longitude')) else None,
                    float(row.get('consultation_fee')) if pd.notna(row.get('consultation_fee')) else None,
                    int(row.get('year_of_experience')) if pd.notna(row.get('year_of_experience')) else None,
                    float(row.get('dp_score')) if pd.notna(row.get('dp_score')) else None,
                    str(row.get('profile_url', '')),
                    str(row.get('google_map_link', ''))
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
        cursor.execute("SELECT COUNT(DISTINCT speciality) FROM doctors")
        specialty_count = cursor.fetchone()[0]
        print(f"📊 Total specialties: {specialty_count}")
        
        # Get city count
        cursor.execute("SELECT COUNT(DISTINCT city) FROM doctors")
        city_count = cursor.fetchone()[0]
        print(f"📊 Total cities: {city_count}")
        
        # Get top specialties
        cursor.execute("""
            SELECT speciality, COUNT(*) as count 
            FROM doctors 
            GROUP BY speciality 
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
    """Main function to setup database"""
    print("🏥 MediBot MySQL Database Setup")
    print("=" * 40)
    
    # Get database configuration
    db_config = get_db_config()
    
    # Check if all required environment variables are present
    if not all([db_config['host'], db_config['user'], db_config['database']]):
        print("❌ Missing database credentials in environment variables")
        print("Please ensure your .env file contains:")
        print("  MYSQL_HOST=your_host")
        print("  MYSQL_USERNAME=your_username") 
        print("  MYSQL_PASSWORD=your_password")
        print("  MYSQL_DATABASE=your_database")
        return
    
    print(f"🔄 Connecting to MySQL at {db_config['host']}:{db_config['port']}")
    print(f"📂 Database: {db_config['database']}")
    
    try:
        # Connect to database
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            print("✅ Connected to MySQL database")
            
            cursor = connection.cursor()
            
            # Create doctors table
            print("\n📋 Creating doctors table...")
            create_doctors_table(cursor)
            
            # Import CSV data
            csv_path = r"C:\Users\kmgs4\Documents\Christ Uni\trimester 4\nndl\project\medibot\data\bangalore_doctors_final.csv"
            print(f"\n📥 Importing data from: {csv_path}")
            
            if import_csv_data(connection, csv_path):
                print("\n✅ Data import completed successfully")
                
                # Verify imported data
                print("\n🔍 Verifying imported data...")
                verify_data(connection)
                
            else:
                print("\n❌ Data import failed")
            
            cursor.close()
            connection.close()
            print("\n✅ Database connection closed")
            
    except Error as e:
        print(f"❌ MySQL Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
