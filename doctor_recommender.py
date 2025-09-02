"""
Doctor recommendation system - Updated to use MySQL database instead of CSV
"""
import pandas as pd
import re
from pathlib import Path
from typing import List, Dict, Optional
import logging
from markupsafe import Markup
import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DoctorRecommender:
    def __init__(self, use_database: bool = True, csv_path: str = "cleaned_doctors_full.csv"):
        self.use_database = use_database
        self.csv_path = csv_path
        self.doctors_df = None
        self.db_connection = None
        
        # EXACT MAPPING to your CSV specialties
        self.specialty_mapping = {
            # Map AI recommendations to your exact CSV specialties
            "ophthalmologist": "Ophthalmologist",
            "eye specialist": "Ophthalmologist", 
            "cardiologist": "Cardiologist",
            "dermatologist": "Dermatologist",
            "gastroenterologist": "Gastroenterologist",
            "gynecologist": "Gynecologist",
            "neurologist": "Neurologist",
            "orthopedist": "Orthopedist",
            "pediatrician": "Pediatrician",
            "psychiatrist": "Psychiatrist",
            "pulmonologist": "Pulmonologist",
            "rheumatologist": "Rheumatologist",
            "urologist": "Urologist",
            "general practitioner": "General Physician",
            "gp": "General Physician",
            "ent specialist": "ENT Specialist",
            "endocrinologist": "Endocrinologist",
            "nephrologist": "Nephrologist",
            "oncologist": "Oncologist",
            
            # Additional mappings
            "dentist": "Dentist",
            "chiropractor": "Chiropractor",
            "dietitian": "Dietitian/Nutritionist",
            "nutritionist": "Dietitian/Nutritionist",
            "infertility specialist": "Infertility Specialist",
            "neurosurgeon": "Neurosurgeon",
            "physiotherapist": "Physiotherapist",
            "radiologist": "Radiologist",
            "pathologist": "Pathologist",
            "anesthesiologist": "Anesthesiologist",
            "emergency medicine physician": "Emergency Medicine Physician",
            "geriatrician": "Geriatrician",
            "plastic surgeon": "Plastic Surgeon",
            "vascular surgeon": "Vascular Surgeon",
            "thoracic surgeon": "Thoracic Surgeon",
            "bariatric surgeon": "bariatric surgeon",
            "homeopath": "Homeopath",
            "ayurveda": "Ayurveda",
            "unani": "Unani",
            "sexologist": "Sexologist",
            "cosmetologist": "Cosmetologist"
        }
        
        # Initialize data loading
        if self.use_database:
            self.load_doctors_from_database()
        else:
            self.load_doctors_data()
    
    def get_db_connection(self):
        """Get MySQL database connection"""
        if self.db_connection and self.db_connection.open:
            return self.db_connection
            
        try:
            mysql_config = {
                'host': os.getenv('MYSQL_HOST', 'localhost'),
                'port': int(os.getenv('MYSQL_PORT', '3306')),
                'user': os.getenv('MYSQL_USERNAME', 'root'),
                'password': os.getenv('MYSQL_PASSWORD', ''),
                'database': os.getenv('MYSQL_DATABASE', 'medibot2'),
                'charset': 'utf8mb4',
                'autocommit': True
            }
            
            self.db_connection = pymysql.connect(**mysql_config)
            return self.db_connection
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return None
    
    def load_doctors_from_database(self):
        """Load doctors data from MySQL database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                print("❌ Database connection failed, falling back to CSV")
                self.use_database = False
                return self.load_doctors_data()
            
            cursor = conn.cursor()
            
            # Check if doctors table exists and has data
            cursor.execute("SELECT COUNT(*) FROM doctors")
            count = cursor.fetchone()[0]
            
            if count == 0:
                print("⚠️  Doctors table is empty, falling back to CSV")
                self.use_database = False
                return self.load_doctors_data()
            
            # Load all doctors data
            query = """
                SELECT city, speciality, profile_url, name, degree, 
                       year_of_experience, location, dp_score, npv, 
                       consultation_fee, google_map_link
                FROM doctors
                ORDER BY name
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Convert to DataFrame for compatibility with existing code
            columns = ['city', 'speciality', 'profile_url', 'name', 'degree', 
                      'year_of_experience', 'location', 'dp_score', 'npv', 
                      'consultation_fee', 'google_map_link']
            
            self.doctors_df = pd.DataFrame(results, columns=columns)
            
            print(f"✅ Loaded {len(self.doctors_df)} doctors from database")
            print(f"📊 Unique specialties: {self.doctors_df['speciality'].nunique()}")
            
            # Show available specialties for debugging
            print("🔍 Available specialties in database:")
            unique_specialties = sorted(self.doctors_df['speciality'].unique())
            for specialty in unique_specialties:
                count = len(self.doctors_df[self.doctors_df['speciality'] == specialty])
                print(f"  • {specialty} ({count} doctors)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading from database: {e}")
            print("📂 Falling back to CSV...")
            self.use_database = False
            return self.load_doctors_data()
    
    def load_doctors_data(self):
        """Load and preprocess doctors data from CSV"""
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
            
            # Show available specialties for debugging
            print("🔍 Available specialties in CSV:")
            unique_specialties = sorted(self.doctors_df['speciality'].unique())
            for specialty in unique_specialties:
                count = len(self.doctors_df[self.doctors_df['speciality'] == specialty])
                print(f"  • {specialty} ({count} doctors)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            return False
    
    def find_specialty_match(self, recommended_specialist: str) -> str:
        """Find exact matching specialty - Works with both database and CSV"""
        recommended_lower = recommended_specialist.lower().strip()
        
        print(f"🔍 Looking for: '{recommended_specialist}'")
        
        # Direct mapping to exact specialty
        if recommended_lower in self.specialty_mapping:
            exact_specialty = self.specialty_mapping[recommended_lower]
            print(f"✅ Found mapping: '{recommended_specialist}' → '{exact_specialty}'")
            return exact_specialty
        
        # Fallback: try partial matching
        if self.use_database:
            return self.find_specialty_in_database(recommended_lower)
        else:
            return self.find_specialty_in_dataframe(recommended_lower)
    
    def find_specialty_in_database(self, recommended_lower: str) -> str:
        """Find specialty in database using SQL"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return None
                
            cursor = conn.cursor()
            
            # Try partial matching
            cursor.execute("SELECT DISTINCT speciality FROM doctors WHERE LOWER(speciality) LIKE %s LIMIT 1", 
                          [f'%{recommended_lower}%'])
            result = cursor.fetchone()
            
            if result:
                specialty = result[0]
                print(f"✅ Found partial match in database: '{specialty}'")
                return specialty
                
        except Exception as e:
            print(f"❌ Database specialty search failed: {e}")
        
        print(f"❌ No match found for '{recommended_lower}'")
        return None
    
    def find_specialty_in_dataframe(self, recommended_lower: str) -> str:
        """Find specialty in DataFrame"""
        if self.doctors_df is None:
            return None
            
        available_specialties = self.doctors_df['speciality'].unique()
        for specialty in available_specialties:
            if recommended_lower in specialty.lower():
                print(f"✅ Found partial match: '{specialty}'")
                return specialty
        
        print(f"❌ No match found for '{recommended_lower}'")
        return None
    
    def recommend_doctors(self, specialist_type: str, city: str = None, limit: int = 5, sort_by: str = "rating") -> List[Dict]:
        """Recommend doctors based on specialist type with sorting options - Database optimized"""
        if self.use_database:
            return self.recommend_doctors_from_database(specialist_type, city, limit, sort_by)
        else:
            return self.recommend_doctors_from_dataframe(specialist_type, city, limit, sort_by)
    
    def recommend_doctors_from_database(self, specialist_type: str, city: str = None, limit: int = 5, sort_by: str = "rating") -> List[Dict]:
        """Recommend doctors from database - Direct SQL query for better performance"""
        try:
            conn = self.get_db_connection()
            if not conn:
                print("❌ Database connection failed")
                return []
            
            cursor = conn.cursor()
            
            # Find matching specialty
            matched_specialty = self.find_specialty_match(specialist_type)
            if not matched_specialty:
                print(f"❌ No specialty match found for '{specialist_type}'")
                return []
            
            # Build query with optional city filter
            base_query = """
                SELECT city, speciality, profile_url, name, degree, 
                       year_of_experience, location, dp_score, npv, 
                       consultation_fee, google_map_link
                FROM doctors 
                WHERE speciality = %s
            """
            
            params = [matched_specialty]
            
            if city:
                base_query += " AND city LIKE %s"
                params.append(f"%{city}%")
            
            # Add sorting
            if sort_by == "rating":
                base_query += " ORDER BY dp_score DESC, year_of_experience DESC"
            elif sort_by == "experience":
                base_query += " ORDER BY year_of_experience DESC, dp_score DESC"
            elif sort_by == "fee":
                base_query += " ORDER BY consultation_fee ASC, dp_score DESC"
            else:
                base_query += " ORDER BY dp_score DESC"
            
            base_query += f" LIMIT %s"
            params.append(limit)
            
            cursor.execute(base_query, params)
            results = cursor.fetchall()
            
            # Convert to list of dictionaries
            doctors = []
            for row in results:
                doctor = {
                    'city': row[0],
                    'specialty': row[1],
                    'profile_url': row[2],
                    'name': row[3],
                    'degree': row[4],
                    'experience': row[5] if row[5] is not None else 0,
                    'location': row[6],
                    'rating': float(row[7]) if row[7] is not None else 0.0,
                    'npv': row[8] if row[8] is not None else 0,
                    'fee': row[9] if row[9] is not None else 0,
                    'map_link': row[10]
                }
                doctors.append(doctor)
            
            print(f"✅ Found {len(doctors)} {matched_specialty}s" + (f" in {city}" if city else ""))
            return doctors
            
        except Exception as e:
            print(f"❌ Database query failed: {e}")
            return []
    
    def recommend_doctors_from_dataframe(self, specialist_type: str, city: str = None, limit: int = 5, sort_by: str = "rating") -> List[Dict]:
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
        if self.use_database:
            return self.get_database_statistics()
        else:
            return self.get_dataframe_statistics()
    
    def get_database_statistics(self) -> Dict:
        """Get statistics from database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return {"error": "Database connection failed"}
            
            cursor = conn.cursor()
            
            # Total doctors
            cursor.execute("SELECT COUNT(*) FROM doctors")
            total_doctors = cursor.fetchone()[0]
            
            # Unique specialties
            cursor.execute("SELECT COUNT(DISTINCT speciality) FROM doctors")
            unique_specialties = cursor.fetchone()[0]
            
            # Unique cities
            cursor.execute("SELECT COUNT(DISTINCT city) FROM doctors")
            unique_cities = cursor.fetchone()[0]
            
            # Top specialties
            cursor.execute("""
                SELECT speciality, COUNT(*) as count 
                FROM doctors 
                GROUP BY speciality 
                ORDER BY count DESC 
                LIMIT 5
            """)
            top_specialties = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Average consultation fee
            cursor.execute("SELECT AVG(consultation_fee) FROM doctors WHERE consultation_fee > 0")
            avg_fee_result = cursor.fetchone()[0]
            avg_consultation_fee = float(avg_fee_result) if avg_fee_result else 0
            
            return {
                "total_doctors": total_doctors,
                "unique_specialties": unique_specialties,
                "unique_cities": unique_cities,
                "top_specialties": top_specialties,
                "average_consultation_fee": round(avg_consultation_fee, 2),
                "data_source": "database"
            }
            
        except Exception as e:
            return {"error": f"Database statistics failed: {e}"}
    
    def get_dataframe_statistics(self) -> Dict:
        """Get statistics from DataFrame (CSV fallback)"""
        if self.doctors_df is None:
            return {"error": "No doctor data loaded"}
        
        try:
            return {
                "total_doctors": len(self.doctors_df),
                "unique_specialties": self.doctors_df['speciality'].nunique(),
                "unique_cities": self.doctors_df['city'].nunique(), 
                "top_specialties": self.doctors_df['speciality'].value_counts().head(5).to_dict(),
                "average_consultation_fee": round(self.doctors_df['consultation_fee'].mean(), 2),
                "data_source": "csv"
            }
        except Exception as e:
            return {"error": f"Statistics calculation failed: {e}"}

# Test the system
if __name__ == "__main__":
    print("🧪 TESTING DOCTOR RECOMMENDER (Database vs CSV)")
    print("=" * 50)
    
    # Test with database first, then CSV fallback
    recommender = DoctorRecommender(use_database=True)
    
    if recommender.use_database:
        print("✅ Using database mode")
    else:
        print("📂 Using CSV fallback mode")
    
    if (recommender.use_database and recommender.get_db_connection()) or (not recommender.use_database and recommender.doctors_df is not None):
        # Test ophthalmologist search
        test_cases = [
            ("ophthalmologist", "Bangalore"),
            ("eye specialist", "Delhi"),
            ("cardiologist", "Mumbai"),
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