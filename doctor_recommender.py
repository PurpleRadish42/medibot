"""
Doctor recommendation system - Database with CSV fallback
"""
import pandas as pd
import re
from pathlib import Path
from typing import List, Dict, Optional
import logging
from markupsafe import Markup
import mysql.connector
from mysql.connector import Error
import os
import math
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DoctorRecommender:
    def __init__(self, csv_path: str = r"C:\Users\kmgs4\Documents\Christ Uni\trimester 4\nndl\project\medibot\data\bangalore_doctors_final.csv"):
        self.csv_path = csv_path
        self.doctors_df = None
        self.data_source = None  # Will be 'database' or 'csv'
        
        # Database configuration
        self.db_config = {
            'host': os.getenv('MYSQL_HOST'),
            'port': int(os.getenv('MYSQL_PORT', '3306')),
            'user': os.getenv('MYSQL_USERNAME'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DATABASE'),
            'charset': 'utf8mb4',
            'autocommit': True
        }
        
        # EXACT MAPPING to your database specialties
        self.specialty_mapping = {
            # Map AI recommendations to your exact database specialties
            "ophthalmologist": "ophthalmologist",
            "eye specialist": "ophthalmologist", 
            "cardiologist": "cardiologist",
            "dermatologist": "dermatologist",
            "gastroenterologist": "gastroenterologist",
            "gynecologist": "gynecologist",
            "neurologist": "neurologist",
            "orthopedist": "orthopedist",
            "pediatrician": "pediatrician",
            "psychiatrist": "psychiatrist",
            "pulmonologist": "pulmonologist",
            "rheumatologist": "rheumatologist",
            "urologist": "urologist",
            "general practitioner": "general-physician",
            "gp": "general-physician",
            "ent specialist": "ent-specialist",
            "endocrinologist": "endocrinologist",
            "nephrologist": "nephrologist",
            "oncologist": "oncologist",
            
            # Additional mappings for database specialties
            "dentist": "dentist",
            "ayurveda": "ayurveda",
            "cardiac surgeon": "cardiac-surgeon",
            "anesthesiologist": "anesthesiologist",
            "neurosurgeon": "neurosurgeon",
            "plastic surgeon": "plastic-surgeon",
            "pathologist": "pathologist",
            "radiologist": "radiologist",
            "sexologist": "sexologist",
            "surgeon": "surgeon",
            "trichologist": "trichologist",
            "unani": "unani",
            "vascular surgeon": "vascular-surgeon"
        }
        
        self.load_doctors_data()
    
    def load_doctors_data(self):
        """Load doctors data from MySQL database with CSV fallback"""
        # First try to load from database
        if self.load_from_database():
            return True
        
        # Fallback to CSV if database fails
        print("⚠️ Database connection failed, falling back to CSV...")
        return self.load_from_csv()
    
    def load_from_database(self):
        """Load doctors data from MySQL database"""
        try:
            print("🔄 Attempting to connect to MySQL database...")
            
            # Check if database credentials are available
            if not all([self.db_config['host'], self.db_config['user'], self.db_config['database']]):
                print("❌ Missing database credentials in environment variables")
                return False
            
            # Connect to database
            connection = mysql.connector.connect(**self.db_config)
            
            if connection.is_connected():
                print(f"✅ Connected to MySQL database: {self.db_config['database']}")
                
                # Check if doctors table exists
                cursor = connection.cursor()
                cursor.execute("SHOW TABLES LIKE 'doctors'")
                result = cursor.fetchone()
                
                if not result:
                    print("❌ 'doctors' table not found in database")
                    return False
                
                # Load doctors data from database
                query = """
                SELECT name, specialty, degree, bangalore_location as city, 
                       bangalore_location as location, 
                       latitude, longitude, consultation_fee, experience_years as year_of_experience, 
                       rating as dp_score, source_url as profile_url, google_maps_link as google_map_link
                FROM doctors
                """
                
                self.doctors_df = pd.read_sql(query, connection)
                print(f"📊 Loaded {len(self.doctors_df)} doctors from MySQL database")
                
                # Preprocess data similar to CSV loading
                self.preprocess_doctors_data()
                self.data_source = 'database'
                
                cursor.close()
                connection.close()
                print("✅ Database connection closed")
                return True
                
        except Error as e:
            print(f"❌ MySQL Error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error connecting to database: {e}")
            return False
        finally:
            if 'connection' in locals() and connection.is_connected():
                connection.close()
        
        return False
    
    def load_from_csv(self):
        """Load doctors data from CSV file"""
        try:
            file_path = Path(self.csv_path)
            if not file_path.exists():
                print(f"❌ CSV file not found: {self.csv_path}")
                return False
            
            self.doctors_df = pd.read_csv(self.csv_path)
            print(f"📊 Loaded {len(self.doctors_df)} doctors from CSV file")
            
            # Preprocess data
            self.preprocess_doctors_data()
            self.data_source = 'csv'
            return True
            
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            return False
    
    def preprocess_doctors_data(self):
        """Preprocess doctors data regardless of source"""
        # Handle both 'specialty' and 'speciality' columns for compatibility
        if 'specialty' in self.doctors_df.columns and 'speciality' not in self.doctors_df.columns:
            self.doctors_df['speciality'] = self.doctors_df['specialty']
        elif 'speciality' in self.doctors_df.columns and 'specialty' not in self.doctors_df.columns:
            self.doctors_df['specialty'] = self.doctors_df['speciality']
        
        # Ensure we have the specialty column with correct name
        specialty_col = 'specialty' if 'specialty' in self.doctors_df.columns else 'speciality'
        if specialty_col in self.doctors_df.columns:
            self.doctors_df['speciality'] = self.doctors_df[specialty_col].fillna('')
        
        # Handle experience column mapping (CSV uses 'experience_years', code expects 'year_of_experience')
        if 'experience_years' in self.doctors_df.columns and 'year_of_experience' not in self.doctors_df.columns:
            self.doctors_df['year_of_experience'] = self.doctors_df['experience_years']
        
        # Handle rating column mapping (CSV uses 'rating', code expects 'dp_score')
        if 'rating' in self.doctors_df.columns and 'dp_score' not in self.doctors_df.columns:
            self.doctors_df['dp_score'] = self.doctors_df['rating']
        
        # Handle Google Maps link mapping (CSV uses 'google_maps_link', code expects 'google_map_link')
        if 'google_maps_link' in self.doctors_df.columns and 'google_map_link' not in self.doctors_df.columns:
            self.doctors_df['google_map_link'] = self.doctors_df['google_maps_link']
        
        # Handle profile URL mapping (CSV uses 'source_url', code expects 'profile_url')
        if 'source_url' in self.doctors_df.columns and 'profile_url' not in self.doctors_df.columns:
            self.doctors_df['profile_url'] = self.doctors_df['source_url']
            
        # Handle city column (database uses 'bangalore_location', CSV might use different names)
        if 'city' not in self.doctors_df.columns:
            if 'bangalore_location' in self.doctors_df.columns:
                self.doctors_df['city'] = self.doctors_df['bangalore_location']
            else:
                self.doctors_df['city'] = 'Bangalore'  # Default
        
        self.doctors_df['name'] = self.doctors_df['name'].fillna('Unknown')
        self.doctors_df['city'] = self.doctors_df['city'].fillna('Unknown')
        self.doctors_df['consultation_fee'] = pd.to_numeric(self.doctors_df['consultation_fee'], errors='coerce')
        self.doctors_df['year_of_experience'] = pd.to_numeric(self.doctors_df['year_of_experience'], errors='coerce')
        self.doctors_df['dp_score'] = pd.to_numeric(self.doctors_df['dp_score'], errors='coerce')
        
        print(f"✅ Loaded {len(self.doctors_df)} doctors from {self.data_source}")
        print(f"📊 Unique specialties: {self.doctors_df['speciality'].nunique()}")
        
        # Show available specialties for debugging
        print(f"🔍 Available specialties in {self.data_source}:")
        unique_specialties = sorted(self.doctors_df['speciality'].unique())
        for specialty in unique_specialties:
            count = len(self.doctors_df[self.doctors_df['speciality'] == specialty])
            print(f"  • {specialty} ({count} doctors)")
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula (in kilometers)"""
        try:
            # Convert latitude and longitude from degrees to radians
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            # Radius of earth in kilometers
            r = 6371
            return c * r
        except (TypeError, ValueError):
            return float('inf')  # Return infinite distance for invalid coordinates
    
    def get_data_source_info(self):
        """Get information about current data source"""
        return {
            'source': self.data_source,
            'total_records': len(self.doctors_df) if self.doctors_df is not None else 0,
            'csv_path': self.csv_path if self.data_source == 'csv' else None,
            'database_config': {
                'host': self.db_config['host'],
                'database': self.db_config['database']
            } if self.data_source == 'database' else None
        }
    
    def find_specialty_match(self, recommended_specialist: str) -> str:
        """Find exact matching specialty in CSV - SIMPLIFIED"""
        recommended_lower = recommended_specialist.lower().strip()
        
        print(f"🔍 Looking for: '{recommended_specialist}'")
        
        # Direct mapping to exact CSV specialty
        if recommended_lower in self.specialty_mapping:
            exact_specialty = self.specialty_mapping[recommended_lower]
            print(f"✅ Found mapping: '{recommended_specialist}' → '{exact_specialty}'")
            return exact_specialty
        
        # Fallback: try partial matching
        available_specialties = self.doctors_df['speciality'].unique()
        for specialty in available_specialties:
            if recommended_lower in specialty.lower():
                print(f"✅ Found partial match: '{specialty}'")
                return specialty
        
        print(f"❌ No match found for '{recommended_specialist}'")
        return None
    
    def recommend_doctors(self, specialist_type: str, city: str = None, limit: int = 5, sort_by: str = "rating", user_lat: float = None, user_lng: float = None) -> List[Dict]:
        """Recommend doctors based on specialist type with sorting options - ENHANCED WITH LOCATION"""
        if self.doctors_df is None:
            print("❌ No doctor data loaded")
            return []
        
        try:
            print(f"\n🏥 Searching for {specialist_type}" + (f" in {city}" if city else "") + f" (sorted by {sort_by})")
            
            # Find exact matching specialty
            exact_specialty = self.find_specialty_match(specialist_type)
            
            if not exact_specialty:
                print("❌ No matching specialty found")
                return []
            
            # Filter doctors by exact specialty match
            filtered_doctors = self.doctors_df[
                self.doctors_df['speciality'] == exact_specialty
            ].copy()
            
            print(f"🔍 Found {len(filtered_doctors)} {exact_specialty}s in database")
            
            # Filter by city if provided (for location-based sorting)
            if city and len(filtered_doctors) > 0:
                city_filtered = filtered_doctors[
                    filtered_doctors['city'].str.contains(city, case=False, na=False)
                ]
                
                if len(city_filtered) > 0:
                    filtered_doctors = city_filtered
                    print(f"🏙️ Filtered to {len(filtered_doctors)} doctors in {city}")
                else:
                    print(f"⚠️ No {exact_specialty}s found in {city}, showing all locations")
            
            if len(filtered_doctors) == 0:
                print("❌ No doctors found after filtering")
                return []
            
            # Fill NaN values for sorting
            filtered_doctors['dp_score'] = filtered_doctors['dp_score'].fillna(0)  # This is actually rating from DB
            filtered_doctors['year_of_experience'] = filtered_doctors['year_of_experience'].fillna(0)
            filtered_doctors['consultation_fee'] = filtered_doctors['consultation_fee'].fillna(999999)
            
            # Handle location-based sorting with coordinates
            if sort_by == "location" and user_lat is not None and user_lng is not None:
                # Calculate distance for each doctor using coordinates
                filtered_doctors['distance_km'] = filtered_doctors.apply(
                    lambda row: self.calculate_distance(
                        user_lat, user_lng, 
                        float(row['latitude']) if pd.notna(row['latitude']) else 0,
                        float(row['longitude']) if pd.notna(row['longitude']) else 0
                    ), axis=1
                )
                # Sort by distance first, then by rating
                filtered_doctors = filtered_doctors.sort_values([
                    'distance_km', 'dp_score', 'year_of_experience'
                ], ascending=[True, False, False])
                print(f"📍 Sorted by distance from user location ({user_lat:.4f}, {user_lng:.4f})")
            elif sort_by == "experience":
                # Sort by experience first, then rating, then fee
                filtered_doctors = filtered_doctors.sort_values([
                    'year_of_experience', 'dp_score', 'consultation_fee'
                ], ascending=[False, False, True])
                print(f"🎓 Sorted by experience and ratings")
            else:
                # Default rating-based sorting: Best rating first, most experience first, lowest fee first
                filtered_doctors = filtered_doctors.sort_values([
                    'dp_score', 'year_of_experience', 'consultation_fee'
                ], ascending=[False, False, True])
                print(f"⭐ Sorted by ratings and experience")
            
            # Get top recommendations
            top_doctors = filtered_doctors.head(limit)
            print(f"👨‍⚕️ Returning top {len(top_doctors)} {exact_specialty}s")
            
            # Format recommendations
            recommendations = []
            for _, doctor in top_doctors.iterrows():
                # Get experience, consultation fee, and rating from the database
                experience_years = doctor.get('year_of_experience', 0)
                consultation_fee = doctor.get('consultation_fee', 0)
                rating = doctor.get('dp_score', 0)  # This is actually 'rating' from database, mapped to dp_score
                
                # Get distance if available
                distance = doctor.get('distance_km', None)
                distance_str = f"{distance:.1f} km" if distance is not None and distance != float('inf') else 'Location not available'
                
                recommendations.append({
                    'name': str(doctor['name']),
                    'specialty': str(doctor['speciality']),
                    'degree': str(doctor.get('degree', 'Not specified')),
                    'city': str(doctor['city']),
                    'location': str(doctor.get('location', 'Location not specified')),
                    'experience_years': int(experience_years) if pd.notna(experience_years) and experience_years > 0 else 'Not specified',
                    'consultation_fee': f"₹{int(consultation_fee)}" if pd.notna(consultation_fee) and consultation_fee > 0 else 'Not specified',
                    'rating': f"{rating:.1f}★" if pd.notna(rating) and rating > 0 else 'Not rated',
                    'distance': distance_str,
                    'profile_url': str(doctor.get('profile_url', '')),
                    'google_map_link': str(doctor.get('google_map_link', ''))
                })
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error in doctor recommendation: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def format_doctor_recommendations(self, doctors: List[Dict], specialist_type: str) -> str:
        """Format doctor recommendations for chat response as HTML table"""
        if not doctors:
            return f"I recommend consulting a {specialist_type}. Unfortunately, I don't have specific doctor recommendations available in your area right now. Please consult your local healthcare directory or contact your nearest hospital."
        
        response = f"<p>Based on your symptoms, I recommend consulting a <strong>{specialist_type}</strong>. Here are {len(doctors)} qualified doctors I found:</p>\n\n"
        
        # Start the HTML table
        response += """
        <table style="border-collapse: collapse; width: 100%; margin: 20px 0; font-family: Arial, sans-serif; background: rgba(255, 255, 255, 0.9); border-radius: 8px; overflow: hidden;">
            <thead>
                <tr style="background: linear-gradient(45deg, #4facfe, #00f2fe); color: white; border-bottom: 2px solid #dee2e6;">
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">#</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Doctor Name</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Specialty</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Qualification</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Experience</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Consultation Fee</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Rating</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Distance</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Location</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Profile</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Maps</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for i, doctor in enumerate(doctors, 1):
            # Handle profile URL
            profile_link = ""
            if doctor['profile_url'] and doctor['profile_url'] != 'nan':
                profile_link = f'<a href="{doctor["profile_url"]}" target="_blank" style="color: #007bff; text-decoration: none; font-weight: bold;">View Profile</a>'
            else:
                profile_link = "Not available"
                
            # Handle Google Maps link
            maps_link = ""
            if doctor['google_map_link'] and doctor['google_map_link'] != 'nan':
                maps_link = f'<a href="{doctor["google_map_link"]}" target="_blank" style="color: #007bff; text-decoration: none; font-weight: bold;">View Map</a>'
            else:
                maps_link = "Not available"
                
            # Add table row
            row_style = "background-color: #ffffff;" if i % 2 == 1 else "background-color: #f8f9fa;"
            response += f"""
                <tr style="{row_style}">
                    <td style="border: 1px solid #dee2e6; padding: 10px; text-align: center; font-weight: bold; color: #4facfe;">{i}</td>
                    <td style="border: 1px solid #dee2e6; padding: 10px;"><strong>Dr. {doctor['name']}</strong></td>
                    <td style="border: 1px solid #dee2e6; padding: 10px;">{doctor['specialty']}</td>
                    <td style="border: 1px solid #dee2e6; padding: 10px; font-size: 0.9em;">{doctor['degree']}</td>
                    <td style="border: 1px solid #dee2e6; padding: 10px; text-align: center;"><strong style="color: #17a2b8;">{doctor['experience_years']}</strong></td>
                    <td style="border: 1px solid #dee2e6; padding: 10px; text-align: center;"><strong style="color: #28a745;">{doctor['consultation_fee']}</strong></td>
                    <td style="border: 1px solid #dee2e6; padding: 10px; text-align: center;"><strong style="color: #ffc107;">{doctor['rating']}</strong></td>
                    <td style="border: 1px solid #dee2e6; padding: 10px; text-align: center;"><strong style="color: #6f42c1;">{doctor['distance']}</strong></td>
                    <td style="border: 1px solid #dee2e6; padding: 10px;">{doctor['location']}</td>
                    <td style="border: 1px solid #dee2e6; padding: 10px; text-align: center;">{profile_link}</td>
                    <td style="border: 1px solid #dee2e6; padding: 10px; text-align: center;">{maps_link}</td>
                </tr>
            """
        
        # Close the table
        response += """
            </tbody>
        </table>
        """
        
        # Add important notes
        response += """
        <div style="margin-top: 20px; padding: 15px; background: linear-gradient(45deg, #e9ecef, #f8f9fa); border-radius: 8px; font-family: Arial, sans-serif; border-left: 4px solid #4facfe;">
            <h4 style="margin-top: 0; color: #495057; display: flex; align-items: center;"><i class="fas fa-clipboard-list" style="margin-right: 8px; color: #4facfe;"></i> Important Notes:</h4>
            <ul style="margin-bottom: 0; color: #6c757d; line-height: 1.6;">
                <li>Please verify doctor availability before visiting</li>
                <li>Consultation fees may have changed</li>
                <li>In case of emergency, visit the nearest hospital immediately</li>
                <li>This is for informational purposes only</li>
            </ul>
        </div>
        """
        
        return response


    def get_statistics(self) -> Dict:
        """Get statistics about the doctors database"""
        if self.doctors_df is None:
            return {}
        
        stats = {
            'total_doctors': len(self.doctors_df),
            'total_cities': self.doctors_df['city'].nunique(),
            'total_specialties': self.doctors_df['speciality'].nunique(),
            'avg_experience': float(self.doctors_df['year_of_experience'].mean()) if not self.doctors_df['year_of_experience'].isna().all() else 0,
            'avg_consultation_fee': float(self.doctors_df['consultation_fee'].mean()) if not self.doctors_df['consultation_fee'].isna().all() else 0,
            'top_cities': self.doctors_df['city'].value_counts().head(5).to_dict(),
            'top_specialties': self.doctors_df['speciality'].value_counts().head(10).to_dict(),
            'data_source': self.data_source
        }
        
        return stats

# Test the system
if __name__ == "__main__":
    print("🧪 TESTING OPHTHALMOLOGIST SEARCH")
    print("=" * 50)
    
    recommender = DoctorRecommender()
    
    if recommender.doctors_df is not None:
        # Test ophthalmologist search
        test_cases = [
            ("ophthalmologist", "Mumbai"),
            ("eye specialist", "Delhi"),
            ("cardiologist", "Bangalore"),
            ("general practitioner", None)
        ]
        
        for specialist, city in test_cases:
            print(f"\n🔍 Testing: {specialist}" + (f" in {city}" if city else ""))
            doctors = recommender.recommend_doctors(specialist, city, limit=3)
            
            if doctors:
                print(f"✅ Found {len(doctors)} doctors:")
                for i, doctor in enumerate(doctors, 1):
                    print(f"  {i}. Dr. {doctor['name']} - {doctor['specialty']} - {doctor['city']}")
            else:
                print(f"❌ No {specialist} found")
    else:
        print("❌ Failed to load doctors data")