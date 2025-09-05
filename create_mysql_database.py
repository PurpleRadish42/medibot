import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from datetime import datetime
import re

# Load environment variables
load_dotenv()

def create_mysql_database():
    """Create MySQL database and insert cleaned doctor data"""
    
    print("=" * 80)
    print("CREATING MYSQL DATABASE FROM CLEANED CSV DATA")
    print("=" * 80)
    
    # Database connection configuration
    db_config = {
        'host': os.getenv('MYSQL_HOST'),
        'port': int(os.getenv('MYSQL_PORT', 25060)),
        'user': os.getenv('MYSQL_USERNAME'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DATABASE'),
        'ssl_disabled': False,
        'charset': 'utf8mb4',
        'autocommit': False
    }
    
    print(f"📡 Connecting to MySQL server: {db_config['host']}:{db_config['port']}")
    print(f"🗄️ Database: {db_config['database']}")
    
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        print("✅ Connected to MySQL database successfully!")
        
        # Load the cleaned CSV data
        print("\n📊 Loading cleaned CSV data...")
        df = pd.read_csv('data/bangalore_doctors_final.csv')
        
        print(f"✅ Loaded CSV data: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Create the doctors table with proper schema
        print("\n🏗️ Creating doctors table...")
        
        # Drop existing table if it exists
        cursor.execute("DROP TABLE IF EXISTS doctors")
        print("🗑️ Dropped existing doctors table")
        
        # Create new table with optimized schema
        create_table_query = """
        CREATE TABLE doctors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            entry_id INT NOT NULL,
            name VARCHAR(255) NOT NULL,
            specialty VARCHAR(100) NOT NULL,
            degree TEXT NOT NULL,
            experience TEXT,
            experience_years INT DEFAULT 0,
            consultation_fee INT DEFAULT 0,
            rating DECIMAL(3,2) DEFAULT 0.0,
            bangalore_location VARCHAR(100) NOT NULL,
            latitude DECIMAL(10,8),
            longitude DECIMAL(11,8),
            google_maps_link TEXT,
            coordinates TEXT,
            location_index INT,
            source_url TEXT,
            scraped_at DATETIME,
            scraping_session VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            
            INDEX idx_specialty (specialty),
            INDEX idx_location (bangalore_location),
            INDEX idx_rating (rating),
            INDEX idx_experience (experience_years),
            INDEX idx_fee (consultation_fee),
            INDEX idx_name (name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_query)
        print("✅ Created doctors table with indexes")
        
        # Prepare data for insertion
        print("\n🔄 Preparing data for insertion...")
        
        def clean_data_for_mysql(df):
            """Clean data specifically for MySQL insertion"""
            df_clean = df.copy()
            
            # Handle datetime columns
            for col in ['scraped_at']:
                if col in df_clean.columns:
                    df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
            
            # Ensure numeric columns are proper types
            df_clean['experience_years'] = pd.to_numeric(df_clean['experience_years'], errors='coerce').fillna(0).astype(int)
            df_clean['consultation_fee'] = pd.to_numeric(df_clean['consultation_fee'], errors='coerce').fillna(0).astype(int)
            df_clean['rating'] = pd.to_numeric(df_clean['rating'], errors='coerce').fillna(0.0)
            df_clean['latitude'] = pd.to_numeric(df_clean['latitude'], errors='coerce')
            df_clean['longitude'] = pd.to_numeric(df_clean['longitude'], errors='coerce')
            df_clean['entry_id'] = pd.to_numeric(df_clean['entry_id'], errors='coerce').fillna(0).astype(int)
            df_clean['location_index'] = pd.to_numeric(df_clean['location_index'], errors='coerce').fillna(0).astype(int)
            
            # Handle string columns - ensure they're not too long and clean
            string_columns = ['name', 'specialty', 'degree', 'experience', 'bangalore_location', 
                            'google_maps_link', 'coordinates', 'source_url', 'scraping_session']
            
            for col in string_columns:
                if col in df_clean.columns:
                    df_clean[col] = df_clean[col].astype(str)
                    # Truncate if too long
                    if col == 'name':
                        df_clean[col] = df_clean[col].str[:255]
                    elif col == 'specialty' or col == 'bangalore_location':
                        df_clean[col] = df_clean[col].str[:100]
                    elif col == 'scraping_session':
                        df_clean[col] = df_clean[col].str[:50]
            
            return df_clean
        
        df_clean = clean_data_for_mysql(df)
        
        # Insert data in batches
        print("📥 Inserting data into MySQL database...")
        
        insert_query = """
        INSERT INTO doctors (
            entry_id, name, specialty, degree, experience, experience_years,
            consultation_fee, rating, bangalore_location, latitude, longitude,
            google_maps_link, coordinates, location_index, source_url,
            scraped_at, scraping_session
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        batch_size = 100
        total_rows = len(df_clean)
        successful_inserts = 0
        failed_inserts = 0
        
        for i in range(0, total_rows, batch_size):
            batch = df_clean.iloc[i:i+batch_size]
            batch_data = []
            
            for _, row in batch.iterrows():
                try:
                    data_tuple = (
                        int(row['entry_id']),
                        str(row['name']),
                        str(row['specialty']),
                        str(row['degree']),
                        str(row['experience']),
                        int(row['experience_years']),
                        int(row['consultation_fee']),
                        float(row['rating']),
                        str(row['bangalore_location']),
                        float(row['latitude']) if pd.notna(row['latitude']) else None,
                        float(row['longitude']) if pd.notna(row['longitude']) else None,
                        str(row['google_maps_link']),
                        str(row['coordinates']),
                        int(row['location_index']),
                        str(row['source_url']),
                        row['scraped_at'] if pd.notna(row['scraped_at']) else None,
                        str(row['scraping_session'])
                    )
                    batch_data.append(data_tuple)
                except Exception as e:
                    print(f"⚠️ Error preparing row {i}: {e}")
                    failed_inserts += 1
            
            if batch_data:
                try:
                    cursor.executemany(insert_query, batch_data)
                    connection.commit()
                    successful_inserts += len(batch_data)
                    print(f"✅ Inserted batch {i//batch_size + 1}: {len(batch_data)} records (Total: {successful_inserts})")
                except Error as e:
                    print(f"❌ Error inserting batch {i//batch_size + 1}: {e}")
                    failed_inserts += len(batch_data)
                    connection.rollback()
        
        # Verify insertion
        print(f"\n📊 INSERTION SUMMARY:")
        print(f"✅ Successful inserts: {successful_inserts}")
        print(f"❌ Failed inserts: {failed_inserts}")
        print(f"📝 Total records processed: {total_rows}")
        
        # Get final count from database
        cursor.execute("SELECT COUNT(*) FROM doctors")
        db_count = cursor.fetchone()[0]
        print(f"🗄️ Records in database: {db_count}")
        
        # Create some sample queries to verify data
        print(f"\n🔍 DATA VERIFICATION:")
        
        # Top specialties
        cursor.execute("""
            SELECT specialty, COUNT(*) as count 
            FROM doctors 
            GROUP BY specialty 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_specialties = cursor.fetchall()
        print(f"Top 5 specialties:")
        for specialty, count in top_specialties:
            print(f"  {specialty}: {count}")
        
        # Average rating and fee
        cursor.execute("""
            SELECT 
                AVG(rating) as avg_rating,
                AVG(consultation_fee) as avg_fee,
                MIN(consultation_fee) as min_fee,
                MAX(consultation_fee) as max_fee
            FROM doctors
        """)
        stats = cursor.fetchone()
        print(f"Database statistics:")
        print(f"  Average rating: {stats[0]:.2f}")
        print(f"  Average fee: ₹{stats[1]:.0f}")
        print(f"  Fee range: ₹{stats[2]} - ₹{stats[3]}")
        
        # Sample records
        cursor.execute("SELECT name, specialty, rating, consultation_fee FROM doctors LIMIT 3")
        samples = cursor.fetchall()
        print(f"Sample records:")
        for name, specialty, rating, fee in samples:
            print(f"  {name} ({specialty}) - ⭐{rating} - ₹{fee}")
        
        print(f"\n🎉 DATABASE CREATION COMPLETED SUCCESSFULLY!")
        print(f"✅ Database: {db_config['database']}")
        print(f"✅ Table: doctors")
        print(f"✅ Records: {db_count}")
        print(f"✅ Status: Ready for use")
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Database connection closed")
    
    return True

if __name__ == "__main__":
    success = create_mysql_database()
    if success:
        print("\n🚀 Your MySQL database is ready to use!")
    else:
        print("\n💥 Database creation failed. Please check the errors above.")
