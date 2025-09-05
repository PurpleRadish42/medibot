import pandas as pd
import re
from datetime import datetime

def find_problematic_rows():
    """Find the specific rows that likely caused insertion errors"""
    
    df = pd.read_csv('Web_Scraping/practo_scraper/data/bangalore_doctors_complete.csv')
    
    print(f'Analyzing {len(df)} rows from CSV...')
    
    problematic_rows = []
    
    for index, row in df.iterrows():
        issues = []
        
        # Check for name length
        name = str(row.get('name', ''))
        if len(name) > 200:
            issues.append(f'Name too long: {len(name)} chars')
        
        # Check for specialty length  
        specialty = str(row.get('specialty', ''))
        if len(specialty) > 100:
            issues.append(f'Specialty too long: {len(specialty)} chars')
        
        # Check for location length
        location = str(row.get('bangalore_location', ''))
        if len(location) > 150:
            issues.append(f'Location too long: {len(location)} chars')
        
        # Check for invalid entry_id
        try:
            entry_id = row.get('entry_id')
            if pd.notna(entry_id):
                int(entry_id)
        except:
            issues.append(f'Invalid entry_id: {entry_id}')
        
        # Check for invalid rating
        try:
            rating = row.get('rating')
            if pd.notna(rating):
                rating_val = float(rating)
                if rating_val < 0 or rating_val > 5:
                    issues.append(f'Invalid rating: {rating_val}')
        except:
            issues.append(f'Invalid rating format: {rating}')
        
        # Check for invalid location_index
        try:
            loc_index = row.get('location_index')
            if pd.notna(loc_index):
                int(loc_index)
        except:
            issues.append(f'Invalid location_index: {loc_index}')
        
        # Check for problematic characters in key fields
        for field in ['name', 'specialty', 'degree', 'bangalore_location']:
            value = row.get(field, '')
            if pd.notna(value):
                try:
                    str(value).encode('utf-8')
                except:
                    issues.append(f'Encoding issue in {field}')
        
        # Check timestamp
        try:
            scraped_at = row.get('scraped_at')
            if pd.notna(scraped_at):
                datetime.fromisoformat(str(scraped_at).replace('T', ' ').replace('Z', ''))
        except:
            issues.append(f'Invalid timestamp: {scraped_at}')
        
        # Check coordinates
        coords = row.get('coordinates')
        if pd.notna(coords):
            try:
                coord_parts = str(coords).split(',')
                if len(coord_parts) == 2:
                    lat = float(coord_parts[0].strip())
                    lng = float(coord_parts[1].strip())
                    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                        issues.append(f'Invalid coordinates range: {coords}')
                else:
                    issues.append(f'Invalid coordinates format: {coords}')
            except:
                issues.append(f'Invalid coordinates: {coords}')
        
        if issues:
            problematic_rows.append({
                'index': index,
                'entry_id': row.get('entry_id'),
                'name': name[:50] + '...' if len(name) > 50 else name,
                'issues': issues
            })
    
    print(f'Found {len(problematic_rows)} potentially problematic rows:')
    
    for i, prob_row in enumerate(problematic_rows[:15]):  # Show first 15
        print(f'\nRow {prob_row["index"]} (entry_id: {prob_row["entry_id"]}):')
        print(f'  Name: {prob_row["name"]}')
        for issue in prob_row["issues"]:
            print(f'  Issue: {issue}')
    
    if len(problematic_rows) > 15:
        print(f'\n... and {len(problematic_rows) - 15} more problematic rows')
    
    return problematic_rows

if __name__ == "__main__":
    find_problematic_rows()
