import pandas as pd
import re

def verify_final_cleaning():
    """Verify that the degree cleaning was successful"""
    
    print("=" * 80)
    print("VERIFICATION OF FINAL CLEANED DATASET")
    print("=" * 80)
    
    # Load both files for comparison
    df_original = pd.read_csv('bangalore_doctors_cleaned.csv')
    df_final = pd.read_csv('bangalore_doctors_final_cleaned.csv')
    
    print(f"Original dataset shape: {df_original.shape}")
    print(f"Final dataset shape: {df_final.shape}")
    
    # Check for sentence patterns in degrees
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
    
    def count_sentence_degrees(df):
        """Count degrees that contain sentence patterns"""
        count = 0
        for degree in df['degree']:
            degree_str = str(degree)
            for pattern in sentence_patterns:
                if re.search(pattern, degree_str, re.IGNORECASE):
                    count += 1
                    break
        return count
    
    original_sentences = count_sentence_degrees(df_original)
    final_sentences = count_sentence_degrees(df_final)
    
    print(f"\n🔍 SENTENCE-FORMAT DEGREES:")
    print(f"  Before cleaning: {original_sentences}")
    print(f"  After cleaning: {final_sentences}")
    print(f"  Cleaned: {original_sentences - final_sentences}")
    
    if final_sentences == 0:
        print("  ✅ All sentence-format degrees successfully cleaned!")
    else:
        print(f"  ⚠️ {final_sentences} sentence-format degrees still remain")
    
    # Compare top degrees before and after
    print(f"\n📊 TOP 10 DEGREES COMPARISON:")
    print(f"\nBEFORE CLEANING:")
    original_top = df_original['degree'].value_counts().head(10)
    for degree, count in original_top.items():
        print(f"  {degree}: {count}")
    
    print(f"\nAFTER CLEANING:")
    final_top = df_final['degree'].value_counts().head(10)
    for degree, count in final_top.items():
        print(f"  {degree}: {count}")
    
    # Show sample of cleaned degrees
    print(f"\n📋 SAMPLE CLEANED DEGREES:")
    sample_degrees = df_final['degree'].unique()[:15]
    for i, degree in enumerate(sample_degrees, 1):
        print(f"  {i:2d}. {degree}")
    
    # Check for null values
    null_degrees = df_final['degree'].isnull().sum()
    print(f"\n🔍 DATA QUALITY CHECK:")
    print(f"  Null degrees: {null_degrees}")
    print(f"  Total unique degrees: {df_final['degree'].nunique()}")
    print(f"  Data completeness: {((len(df_final) - null_degrees) / len(df_final)) * 100:.1f}%")
    
    # Final summary
    print(f"\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"✅ Dataset size: {len(df_final)} records")
    print(f"✅ Columns: {len(df_final.columns)}")
    print(f"✅ Sentence-format degrees cleaned: {original_sentences - final_sentences}")
    print(f"✅ Data quality: {'100%' if final_sentences == 0 and null_degrees == 0 else 'Needs review'}")
    print(f"✅ Ready for database: {'Yes' if final_sentences == 0 and null_degrees == 0 else 'No'}")
    
    return df_final

if __name__ == "__main__":
    final_df = verify_final_cleaning()
