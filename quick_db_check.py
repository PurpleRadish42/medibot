"""
Quick database status check
"""
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    connection = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        port=int(os.getenv('MYSQL_PORT', '3306')),
        user=os.getenv('MYSQL_USERNAME'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE'),
    )
    
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM doctors")
    count = cursor.fetchone()[0]
    print(f"Current records in database: {count}")
    
    if count > 0:
        cursor.execute("SELECT specialty, COUNT(*) FROM doctors GROUP BY specialty LIMIT 5")
        print("Sample specialties:")
        for spec, cnt in cursor.fetchall():
            print(f"  - {spec}: {cnt}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Database error: {e}")
    print("Will use CSV fallback")
