import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def connect_to_database():
    """Connect to MySQL database using environment variables"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=int(os.getenv('MYSQL_PORT').strip("'")),  # Remove quotes from port
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
    """Create doctors table if it doesn't exist"""
    cursor = connection.cursor()
    
    # First drop the table to ensure clean structure
    drop_table_query = "DROP TABLE IF EXISTS doctors"
    
    create_table_query = """
    CREATE TABLE doctors (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(500) NOT NULL,
        specialization VARCHAR(300),
        experience_years INT DEFAULT 0,
        location VARCHAR(300),
        consultation_fee DECIMAL(10, 2) DEFAULT 0,
        dp_score INT DEFAULT 0,
        npv INT DEFAULT 0,
        profile_url TEXT,
        degree VARCHAR(255),
        google_map_link TEXT,
        scraped_at TIMESTAMP NULL,
        city VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_specialization (specialization),
        INDEX idx_location (location),
        INDEX idx_city (city),
        INDEX idx_dp_score (dp_score)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        cursor.execute(drop_table_query)
        cursor.execute(create_table_query)
        print("✅ Doctors table recreated successfully")
    except Error as e:
        print(f"❌ Error creating table: {e}")
    finally:
        cursor.close()

def insert_doctors_data():
    """Read CSV and insert data into MySQL database"""
    
    # Read the CSV file
    try:
        df = pd.read_csv('Web_Scraping/practo_scraper/data/bangalore_doctors_complete.csv')
        print(f"📊 Loaded {len(df)} rows from bangalore_doctors_complete.csv")
        print(f"📋 Columns: {list(df.columns)}")
        print(f"📄 First few rows:")
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
    
    # Create table
    create_doctors_table(connection)
    
    cursor = connection.cursor()
    
    try:
        # Prepare INSERT query based on CSV columns
        insert_query = """
        INSERT INTO doctors (
            city, specialization, profile_url, name, degree, 
            experience_years, location, dp_score, npv, consultation_fee,
            google_map_link, scraped_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Insert data in batches
        inserted_count = 0
        batch_size = 100
        batch_data = []
        
        for index, row in df.iterrows():
            try:
                # Map CSV columns to database columns based on your CSV structure
                # Handle NaN values properly
                city = str(row.get('city', ''))[:255] if pd.notna(row.get('city')) else ''
                speciality = str(row.get('speciality', ''))[:300] if pd.notna(row.get('speciality')) else ''
                profile_url = str(row.get('profile_url', '')) if pd.notna(row.get('profile_url')) else ''
                name = str(row.get('name', ''))[:500] if pd.notna(row.get('name')) else ''
                degree = str(row.get('degree', ''))[:255] if pd.notna(row.get('degree')) else ''
                
                # Handle experience years
                exp_years = row.get('year_of_experience', 0)
                if pd.notna(exp_years):
                    try:
                        exp_years = int(float(exp_years))
                        # Handle unrealistic values
                        if exp_years > 2024:  # Likely a year instead of experience
                            exp_years = 2024 - exp_years if exp_years > 1950 else 0
                        exp_years = max(0, min(exp_years, 70))  # Cap at reasonable values
                    except:
                        exp_years = 0
                else:
                    exp_years = 0
                
                location = str(row.get('location', ''))[:300] if pd.notna(row.get('location')) else ''
                
                # Handle dp_score
                dp_score = row.get('dp_score', 0)
                if pd.notna(dp_score):
                    try:
                        dp_score = int(float(dp_score))
                    except:
                        dp_score = 0
                else:
                    dp_score = 0
                
                # Handle npv
                npv = row.get('npv', 0)
                if pd.notna(npv):
                    try:
                        npv = int(float(npv))
                    except:
                        npv = 0
                else:
                    npv = 0
                
                # Handle consultation_fee
                consultation_fee = row.get('consultation_fee', 0)
                if pd.notna(consultation_fee):
                    try:
                        consultation_fee = float(consultation_fee)
                    except:
                        consultation_fee = 0
                else:
                    consultation_fee = 0
                
                google_map_link = str(row.get('google_map_link', '')) if pd.notna(row.get('google_map_link')) else ''
                scraped_at = str(row.get('scraped_at', '')) if pd.notna(row.get('scraped_at')) else None
                
                data = (
                    city, speciality, profile_url, name, degree,
                    exp_years, location, dp_score, npv, consultation_fee,
                    google_map_link, scraped_at
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
                print(f"⚠️ Error processing row {index}: {e}")
                print(f"Row data: {row.to_dict()}")
                continue
        
        # Insert remaining data
        if batch_data:
            cursor.executemany(insert_query, batch_data)
            connection.commit()
            inserted_count += len(batch_data)
        
        print(f"🎉 Successfully inserted {inserted_count} doctors into the database")
        
    except Error as e:
        print(f"❌ Error during database operation: {e}")
        connection.rollback()
    
    finally:
        cursor.close()
        connection.close()

def verify_insertion():
    """Verify that data was inserted correctly"""
    connection = connect_to_database()
    if not connection:
        return
    
    cursor = connection.cursor()
    
    try:
        # Count total records
        cursor.execute("SELECT COUNT(*) FROM doctors")
        count = cursor.fetchone()[0]
        print(f"\n📊 Total doctors in database: {count}")
        
        # Show statistics by specialization
        cursor.execute("SELECT specialization, COUNT(*) as count FROM doctors GROUP BY specialization ORDER BY count DESC LIMIT 10")
        specializations = cursor.fetchall()
        print("\n🏥 Top 10 Specializations:")
        for spec, count in specializations:
            print(f"  {spec}: {count} doctors")
        
        # Show statistics by city
        cursor.execute("SELECT city, COUNT(*) as count FROM doctors GROUP BY city ORDER BY count DESC LIMIT 5")
        cities = cursor.fetchall()
        print("\n🌆 Top 5 Cities:")
        for city, count in cities:
            print(f"  {city}: {count} doctors")
        
        # Show sample records with highest DP scores
        cursor.execute("SELECT name, specialization, dp_score, location, city FROM doctors WHERE dp_score > 0 ORDER BY dp_score DESC LIMIT 5")
        records = cursor.fetchall()
        print("\n⭐ Top 5 doctors by DP Score:")
        for record in records:
            print(f"  {record[0]} | {record[1]} | Score: {record[2]} | {record[3]}, {record[4]}")
            
    except Error as e:
        print(f"❌ Error verifying data: {e}")
    
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    print("🚀 Starting doctors data insertion to MySQL...")
    print("=" * 60)
    insert_doctors_data()
    print("\n🔍 Verifying insertion...")
    print("=" * 60)
    verify_insertion()
    print("\n✅ Process completed!")
