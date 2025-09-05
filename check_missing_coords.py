#!/usr/bin/env python3
"""
Check for missing coordinates in cardiologists
"""

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'user': os.getenv('MYSQL_USERNAME'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'charset': 'utf8mb4'
}

connection = mysql.connector.connect(**DB_CONFIG)
cursor = connection.cursor()

# Check for NULL coordinates in cardiologists
cursor.execute("""
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN latitude IS NOT NULL THEN 1 ELSE 0 END) as has_lat,
    SUM(CASE WHEN longitude IS NOT NULL THEN 1 ELSE 0 END) as has_lng,
    SUM(CASE WHEN latitude IS NULL THEN 1 ELSE 0 END) as missing_lat,
    SUM(CASE WHEN longitude IS NULL THEN 1 ELSE 0 END) as missing_lng
FROM doctors 
WHERE specialty = 'cardiologist'
""")

result = cursor.fetchone()
total, has_lat, has_lng, missing_lat, missing_lng = result

print(f'🏥 Cardiologist coordinate analysis:')
print(f'Total cardiologists: {total}')
print(f'With latitude: {has_lat}')
print(f'With longitude: {has_lng}')
print(f'Missing latitude: {missing_lat}')
print(f'Missing longitude: {missing_lng}')

# Check some specific doctors that showed huge distances
print(f'\n🔍 Checking specific doctors from test:')
cursor.execute("""
SELECT name, latitude, longitude 
FROM doctors 
WHERE name IN ('M Sudhakar Rao', 'Anusha Buchade', 'Ameet Oswal')
LIMIT 10
""")

for row in cursor.fetchall():
    name, lat, lng = row
    lat_status = f"{lat}" if lat is not None else "NULL"
    lng_status = f"{lng}" if lng is not None else "NULL"
    print(f"👨‍⚕️ {name}: lat={lat_status}, lng={lng_status}")

cursor.close()
connection.close()
