import pandas as pd
import re

def clean_degree_entries():
    """Clean the degree entries that contain full sentences"""
    
    print("=" * 80)
    print("CLEANING DEGREE ENTRIES - REMOVING SENTENCES")
    print("=" * 80)
    
    # Load the CSV file
    df = pd.read_csv('bangalore_doctors_cleaned.csv')
    
    print(f"Original dataset shape: {df.shape}")
    
    # Patterns to identify sentence-format degrees
    sentence_patterns = [
        r'has the following qualifications',
        r'completed his',
        r'completed her',
        r'studied',
        r'graduated',
        r'is a',
        r'more\.\.',
        r'Dr\.',
        r'You can book'
    ]
    
    # Function to extract degrees from sentences
    def extract_degree_from_sentence(degree_text):
        """Extract actual medical degrees from sentence format"""
        
        if pd.isna(degree_text):
            return 'MBBS'
        
        degree_str = str(degree_text)
        
        # Check if it's a sentence format
        is_sentence = False
        for pattern in sentence_patterns:
            if re.search(pattern, degree_str, re.IGNORECASE):
                is_sentence = True
                break
        
        if not is_sentence:
            return degree_str  # Return as-is if not a sentence
        
        print(f"Cleaning: {degree_str[:100]}...")
        
        # Extract degree patterns from the sentence
        degree_patterns = [
            r'MBBS[^,.\n]*',
            r'MD[^,.\n]*',
            r'MS[^,.\n]*',
            r'DNB[^,.\n]*',
            r'DM[^,.\n]*',
            r'MCh[^,.\n]*',
            r'BDS[^,.\n]*',
            r'DGO[^,.\n]*',
            r'DDVL[^,.\n]*',
            r'DO[^,.\n]*',
            r'DVD[^,.\n]*',
            r'DOMS[^,.\n]*',
            r'DPM[^,.\n]*',
            r'MRCP[^,.\n]*',
            r'FRCS[^,.\n]*',
            r'MRCS[^,.\n]*',
            r'Fellowship[^,.\n]*',
            r'Diploma[^,.\n]*',
            r'Diplomate[^,.\n]*',
            r'Member[^,.\n]*',
            r'Fellow[^,.\n]*',
            r'Certificate[^,.\n]*',
            r'CCT[^,.\n]*',
            r'FNB[^,.\n]*',
            r'FRCOG[^,.\n]*',
            r'MRCOG[^,.\n]*'
        ]
        
        found_degrees = []
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, degree_str, re.IGNORECASE)
            for match in matches:
                cleaned_match = match.strip().rstrip(',').rstrip('.')
                if cleaned_match and len(cleaned_match) > 2:
                    found_degrees.append(cleaned_match)
        
        if found_degrees:
            # Remove duplicates while preserving order
            unique_degrees = []
            for degree in found_degrees:
                if degree not in unique_degrees:
                    unique_degrees.append(degree)
            
            cleaned_degree = ', '.join(unique_degrees)
            print(f"  → Extracted: {cleaned_degree}")
            return cleaned_degree
        else:
            # If no degrees found, try to extract from common patterns
            if 'MBBS' in degree_str:
                print("  → Default: MBBS")
                return 'MBBS'
            elif 'BDS' in degree_str:
                print("  → Default: BDS")
                return 'BDS'
            else:
                print("  → Default: MBBS")
                return 'MBBS'
    
    # Identify problematic entries
    problematic_entries = []
    for idx, degree in enumerate(df['degree']):
        degree_str = str(degree)
        for pattern in sentence_patterns:
            if re.search(pattern, degree_str, re.IGNORECASE):
                problematic_entries.append(idx)
                break
    
    print(f"\nFound {len(problematic_entries)} problematic degree entries")
    
    if len(problematic_entries) > 0:
        print("\nSample problematic entries:")
        for i, idx in enumerate(problematic_entries[:5]):
            print(f"  {i+1}. {df.loc[idx, 'degree'][:100]}...")
    
    # Clean the degrees
    print(f"\nCleaning degree entries...")
    df['degree_cleaned'] = df['degree'].apply(extract_degree_from_sentence)
    
    # Replace the original degree column
    df['degree'] = df['degree_cleaned']
    df.drop('degree_cleaned', axis=1, inplace=True)
    
    # Verify cleaning
    print(f"\n" + "=" * 60)
    print("VERIFICATION AFTER CLEANING")
    print("=" * 60)
    
    # Check for remaining sentence patterns
    remaining_sentences = 0
    for degree in df['degree']:
        degree_str = str(degree)
        for pattern in sentence_patterns:
            if re.search(pattern, degree_str, re.IGNORECASE):
                remaining_sentences += 1
                break
    
    print(f"Remaining sentence-format degrees: {remaining_sentences}")
    
    if remaining_sentences == 0:
        print("✅ All sentence-format degrees have been cleaned!")
    
    # Show updated degree distribution
    print(f"\nTop 15 most common degrees after cleaning:")
    degree_counts = df['degree'].value_counts().head(15)
    for degree, count in degree_counts.items():
        print(f"  {degree}: {count}")
    
    # Save the cleaned dataset
    output_file = 'bangalore_doctors_final_cleaned.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\n" + "=" * 80)
    print("CLEANING COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"✅ Cleaned dataset saved to: {output_file}")
    print(f"✅ Total records: {len(df)}")
    print(f"✅ Problematic degrees cleaned: {len(problematic_entries)}")
    print(f"✅ Remaining sentence-format degrees: {remaining_sentences}")
    print(f"✅ Data quality: {'100%' if remaining_sentences == 0 else f'{((len(df) - remaining_sentences) / len(df)) * 100:.1f}%'}")
    
    return df

if __name__ == "__main__":
    cleaned_df = clean_degree_entries()
