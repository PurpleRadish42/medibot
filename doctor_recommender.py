"""
Doctor recommendation system - UPDATED to load from MySQL database
"""
import pandas as pd
import re
from pathlib import Path
from typing import List, Dict, Optional
import logging
from markupsafe import Markup
import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DoctorRecommender:
    def __init__(self, csv_path: str = None):
        self.csv_path = csv_path
        self.doctors_df = None
        self.db_connection = None
        
        # EXACT MAPPING to database specialties (lowercase with hyphens)
        self.specialty_mapping = {
            # Map AI recommendations to exact database specialties
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
            
            # Additional mappings
            "dentist": "dentist",
            "chiropractor": "chiropractor",
            "dietitian": "dietitian",
            "nutritionist": "dietitian",
            "infertility specialist": "infertility-specialist",
            "neurosurgeon": "neurosurgeon",
            "physiotherapist": "physiotherapist",
            "radiologist": "radiologist",
            "pathologist": "pathologist",
            "anesthesiologist": "anesthesiologist",
            "emergency medicine physician": "emergency-medicine-physician",
            "geriatrician": "geriatrician",
            "plastic surgeon": "plastic-surgeon",
            "vascular surgeon": "vascular-surgeon",
            "thoracic surgeon": "thoracic-surgeon",
            "bariatric surgeon": "bariatric-surgeon",
            "homeopath": "homeopath",
            "ayurveda": "ayurveda",
            "unani": "unani",
            "sexologist": "sexologist",
            "cosmetologist": "cosmetologist"
        }
        
        self.load_doctors_data()
    
    def load_doctors_data(self):
        """Load and preprocess doctors data from MySQL database"""
        try:
            # Try to load from database first
            if self.load_from_database():
                return True
            
            # Fallback to CSV if database fails
            if self.csv_path and Path(self.csv_path).exists():
                print("🔄 Database failed, falling back to CSV...")
                return self.load_from_csv()
            
            print("❌ No data source available (database failed and CSV not found)")
            return False
            
        except Exception as e:
            print(f"❌ Error loading doctors data: {e}")
            return False
    
    def load_from_database(self):
        """Load doctors data from MySQL database"""
        try:
            # Database configuration
            mysql_config = {
                'host': os.getenv('MYSQL_HOST', 'localhost'),
                'port': int(os.getenv('MYSQL_PORT', '3306')),
                'user': os.getenv('MYSQL_USERNAME', 'root'),
                'password': os.getenv('MYSQL_PASSWORD', ''),
                'database': os.getenv('MYSQL_DATABASE', 'medibot2'),
                'charset': 'utf8mb4',
                'autocommit': True
            }
            
            # Connect to database
            self.db_connection = pymysql.connect(**mysql_config)
            cursor = self.db_connection.cursor()
            
            # Load doctors data
            query = """
            SELECT 
                id, name, specialty, degree, experience, experience_years,
                consultation_fee, rating, bangalore_location, latitude, longitude,
                google_maps_link, coordinates, source_url, created_at
            FROM doctors 
            WHERE specialty IS NOT NULL AND specialty != ''
            ORDER BY rating DESC, experience_years DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            if not results:
                print("❌ No doctors found in database")
                return False
            
            # Convert to DataFrame
            columns = [
                'id', 'name', 'specialty', 'degree', 'experience', 'experience_years',
                'consultation_fee', 'rating', 'bangalore_location', 'latitude', 'longitude',
                'google_maps_link', 'coordinates', 'source_url', 'created_at'
            ]
            
            self.doctors_df = pd.DataFrame(results, columns=columns)
            
            # Map database columns to expected format
            self.doctors_df['speciality'] = self.doctors_df['specialty']  # Map specialty to speciality
            self.doctors_df['city'] = self.doctors_df['bangalore_location']  # Map location to city
            self.doctors_df['year_of_experience'] = self.doctors_df['experience_years']  # Map experience
            self.doctors_df['dp_score'] = self.doctors_df['rating']  # Map rating to dp_score
            
            # Fill missing values
            self.doctors_df['speciality'] = self.doctors_df['speciality'].fillna('')
            self.doctors_df['name'] = self.doctors_df['name'].fillna('Unknown')
            self.doctors_df['city'] = self.doctors_df['city'].fillna('Unknown')
            self.doctors_df['consultation_fee'] = pd.to_numeric(self.doctors_df['consultation_fee'], errors='coerce')
            self.doctors_df['year_of_experience'] = pd.to_numeric(self.doctors_df['year_of_experience'], errors='coerce')
            self.doctors_df['dp_score'] = pd.to_numeric(self.doctors_df['dp_score'], errors='coerce')
            
            print(f"📊 Loaded {len(self.doctors_df)} doctors from database")
            print(f"📊 Unique specialties: {self.doctors_df['speciality'].nunique()}")
            
            # Show available specialties for debugging
            print("🔍 Available specialties in database:")
            unique_specialties = sorted(self.doctors_df['speciality'].unique())
            for specialty in unique_specialties:
                count = len(self.doctors_df[self.doctors_df['speciality'] == specialty])
                print(f"  • {specialty} ({count} doctors)")
            
            return True
            
        except Exception as e:
            print(f"❌ Database loading failed: {e}")
            return False
    
    def load_from_csv(self):
        """Fallback: Load doctors data from CSV file"""
        try:
            file_path = Path(self.csv_path)
            if not file_path.exists():
                print(f"❌ CSV file not found: {self.csv_path}")
                return False
            
            self.doctors_df = pd.read_csv(self.csv_path)
            print(f"📊 Loaded CSV with {len(self.doctors_df)} rows")
            
            # DON'T convert specialty to lowercase - keep original case
            self.doctors_df['speciality'] = self.doctors_df['speciality'].fillna('')
            self.doctors_df['name'] = self.doctors_df['name'].fillna('Unknown')
            self.doctors_df['city'] = self.doctors_df['city'].fillna('Unknown')
            self.doctors_df['consultation_fee'] = pd.to_numeric(self.doctors_df['consultation_fee'], errors='coerce')
            self.doctors_df['year_of_experience'] = pd.to_numeric(self.doctors_df['year_of_experience'], errors='coerce')
            self.doctors_df['dp_score'] = pd.to_numeric(self.doctors_df['dp_score'], errors='coerce')
            
            print(f"✅ Loaded {len(self.doctors_df)} doctors from CSV")
            print(f"📊 Unique specialties: {self.doctors_df['speciality'].nunique()}")
            
            return True
            
        except Exception as e:
            print(f"❌ CSV loading failed: {e}")
            return False
    
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
    
    def recommend_doctors(self, specialist_type: str, city: str = None, limit: int = 5, sort_by: str = "rating") -> List[Dict]:
        """Recommend doctors based on specialist type with sorting options - SIMPLIFIED"""
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
            filtered_doctors['dp_score'] = filtered_doctors['dp_score'].fillna(0)
            filtered_doctors['year_of_experience'] = filtered_doctors['year_of_experience'].fillna(0)
            filtered_doctors['consultation_fee'] = filtered_doctors['consultation_fee'].fillna(999999)
            
            # Sort based on preference
            if sort_by == "location" and city:
                # For location-based sorting, we already filtered by city
                # Sort by score within the city
                filtered_doctors = filtered_doctors.sort_values([
                    'dp_score', 'year_of_experience', 'consultation_fee'
                ], ascending=[False, False, True])
                print(f"📍 Sorted by location (within {city}) and then by rating")
            else:
                # Default rating-based sorting: Best score first, most experience first, lowest fee first
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
                # Only use dp_score as rating, skip problematic experience/fee data
                dp_score = doctor.get('dp_score', 0)
                
                recommendations.append({
                    'name': str(doctor['name']),
                    'specialty': str(doctor['speciality']),
                    'degree': str(doctor.get('degree', 'Not specified')),
                    'city': str(doctor['city']),
                    'location': str(doctor.get('location', 'Location not specified')),
                    'dp_score': f"{dp_score:.0f}" if pd.notna(dp_score) and dp_score > 0 else 'Not rated',
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
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">Location</th>
                    <th style="border: 1px solid #dee2e6; padding: 12px; text-align: left; font-weight: bold;">DP Score</th>
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
                    <td style="border: 1px solid #dee2e6; padding: 10px;">{doctor['degree']}</td>
                    <td style="border: 1px solid #dee2e6; padding: 10px;">{doctor['location']}, {doctor['city']}</td>
                    <td style="border: 1px solid #dee2e6; padding: 10px; text-align: center;"><strong style="color: #28a745;">{doctor['dp_score']}</strong></td>
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
        
        return {
            'total_doctors': len(self.doctors_df),
            'total_cities': self.doctors_df['city'].nunique(),
            'total_specialties': self.doctors_df['speciality'].nunique(),
            'avg_experience': float(self.doctors_df['year_of_experience'].mean()) if not self.doctors_df['year_of_experience'].isna().all() else 0,
            'avg_consultation_fee': float(self.doctors_df['consultation_fee'].mean()) if not self.doctors_df['consultation_fee'].isna().all() else 0,
            'top_cities': self.doctors_df['city'].value_counts().head(5).to_dict(),
            'top_specialties': self.doctors_df['speciality'].value_counts().head(10).to_dict()
        }

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