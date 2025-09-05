import pandas as pd
import re

def analyze_degrees_and_ratings():
    """Detailed analysis of degrees and ratings columns"""
    
    print("=" * 80)
    print("DETAILED ANALYSIS: DEGREES AND RATINGS COLUMNS")
    print("=" * 80)
    
    # Load the cleaned CSV file
    df = pd.read_csv('bangalore_doctors_cleaned.csv')
    
    print(f"Dataset shape: {df.shape}")
    print()
    
    # DEGREES ANALYSIS
    print("=" * 60)
    print("DEGREES COLUMN ANALYSIS")
    print("=" * 60)
    
    degrees = df['degree'].tolist()
    
    # Check for full sentences vs proper degrees
    print("Sample degrees (first 20):")
    for i, degree in enumerate(degrees[:20]):
        print(f"  {i+1:2d}. {degree}")
    
    print(f"\nTotal unique degrees: {df['degree'].nunique()}")
    
    # Analyze degree patterns
    print("\n🔍 DEGREE PATTERN ANALYSIS:")
    
    # Check for sentences (contain words like "has", "the", "following", etc.)
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
    
    sentence_degrees = []
    valid_degrees = []
    
    for degree in degrees:
        is_sentence = False
        degree_lower = degree.lower()
        
        for pattern in sentence_patterns:
            if re.search(pattern, degree_lower):
                is_sentence = True
                break
        
        if is_sentence:
            sentence_degrees.append(degree)
        else:
            valid_degrees.append(degree)
    
    print(f"✅ Valid degree formats: {len(valid_degrees)}")
    print(f"❌ Full sentences (invalid): {len(sentence_degrees)}")
    
    if sentence_degrees:
        print(f"\n❌ INVALID DEGREES (Full sentences):")
        for i, sentence in enumerate(sentence_degrees[:10]):  # Show first 10
            print(f"  {i+1}. {sentence}")
        if len(sentence_degrees) > 10:
            print(f"  ... and {len(sentence_degrees) - 10} more")
    
    # Check for common valid degree patterns
    print(f"\n🎓 COMMON VALID DEGREE PATTERNS:")
    degree_counts = df['degree'].value_counts().head(15)
    for degree, count in degree_counts.items():
        if degree not in sentence_degrees:
            print(f"  {degree}: {count}")
    
    # RATINGS ANALYSIS
    print("\n" + "=" * 60)
    print("RATINGS COLUMN ANALYSIS")
    print("=" * 60)
    
    ratings = df['rating']
    
    print(f"Rating data type: {ratings.dtype}")
    print(f"Unique ratings: {sorted(ratings.unique())}")
    print(f"Rating range: {ratings.min()} to {ratings.max()}")
    
    # Check for valid rating range (0-5)
    valid_ratings = ratings[(ratings >= 0) & (ratings <= 5)]
    invalid_ratings = ratings[(ratings < 0) | (ratings > 5)]
    
    print(f"\n🔍 RATING VALIDITY:")
    print(f"✅ Valid ratings (0-5): {len(valid_ratings)}")
    print(f"❌ Invalid ratings: {len(invalid_ratings)}")
    
    if len(invalid_ratings) > 0:
        print(f"Invalid rating values: {invalid_ratings.tolist()}")
    
    # Rating distribution
    print(f"\n📊 RATING DISTRIBUTION:")
    rating_counts = ratings.value_counts().sort_index()
    for rating, count in rating_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {rating}: {count} ({percentage:.1f}%)")
    
    # Check for decimal precision
    decimal_ratings = ratings[ratings % 1 != 0]
    whole_ratings = ratings[ratings % 1 == 0]
    
    print(f"\n🔢 RATING PRECISION:")
    print(f"  Whole number ratings: {len(whole_ratings)}")
    print(f"  Decimal ratings: {len(decimal_ratings)}")
    
    if len(decimal_ratings) > 0:
        print(f"  Sample decimal ratings: {sorted(decimal_ratings.unique())}")
    
    # SUMMARY
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    print(f"DEGREES:")
    print(f"  ✅ Valid degrees: {len(valid_degrees)} ({(len(valid_degrees)/len(degrees))*100:.1f}%)")
    print(f"  ❌ Invalid degrees: {len(sentence_degrees)} ({(len(sentence_degrees)/len(degrees))*100:.1f}%)")
    
    print(f"\nRATINGS:")
    print(f"  ✅ Valid ratings: {len(valid_ratings)} ({(len(valid_ratings)/len(ratings))*100:.1f}%)")
    print(f"  ❌ Invalid ratings: {len(invalid_ratings)} ({(len(invalid_ratings)/len(ratings))*100:.1f}%)")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if len(sentence_degrees) > 0:
        print(f"  🔧 Need to clean {len(sentence_degrees)} degree entries that contain full sentences")
    if len(invalid_ratings) > 0:
        print(f"  🔧 Need to fix {len(invalid_ratings)} rating entries outside 0-5 range")
    if len(sentence_degrees) == 0 and len(invalid_ratings) == 0:
        print(f"  🎉 Both degrees and ratings columns are clean and ready for database!")
    
    return {
        'valid_degrees': len(valid_degrees),
        'invalid_degrees': len(sentence_degrees),
        'valid_ratings': len(valid_ratings),
        'invalid_ratings': len(invalid_ratings),
        'sentence_degrees': sentence_degrees
    }

if __name__ == "__main__":
    results = analyze_degrees_and_ratings()
