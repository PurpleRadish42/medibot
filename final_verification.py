import pandas as pd
import re

# Load the perfect cleaned dataset
df = pd.read_csv('bangalore_doctors_perfect_cleaned.csv')

print("=" * 80)
print("FINAL VERIFICATION - PERFECT CLEANED DATASET")
print("=" * 80)
print(f"Dataset shape: {df.shape}")

# Check for any remaining sentence patterns
sentence_patterns = [
    r'has the following qualifications',
    r'completed his',
    r'completed her',
    r'Dr\.\s+\w+',
    r'You can book',
    r'more\.{2,}',
    r'hospital',
    r'department',
    r'consultant'
]

problematic_count = 0
for degree in df['degree']:
    degree_str = str(degree)
    for pattern in sentence_patterns:
        if re.search(pattern, degree_str, re.IGNORECASE):
            problematic_count += 1
            break

print(f"Remaining sentence-format degrees: {problematic_count}")

# Show top 15 degrees
print(f"\nTop 15 most common degrees:")
top_degrees = df['degree'].value_counts().head(15)
for degree, count in top_degrees.items():
    print(f"  {degree}: {count}")

# Check data quality
null_degrees = df['degree'].isnull().sum()
print(f"\nData quality metrics:")
print(f"  Null degrees: {null_degrees}")
print(f"  Total unique degrees: {df['degree'].nunique()}")
print(f"  Data completeness: {((len(df) - null_degrees) / len(df)) * 100:.1f}%")

# Sample degrees
print(f"\nSample degrees (first 10):")
for i, degree in enumerate(df['degree'].head(10), 1):
    print(f"  {i:2d}. {degree}")

# Final summary
print(f"\n" + "=" * 80)
print("CLEANING SUMMARY")
print("=" * 80)
print(f"✅ Total records: {len(df)}")
print(f"✅ Total columns: {len(df.columns)}")
print(f"✅ Unique degrees: {df['degree'].nunique()}")
print(f"✅ Problematic degrees: {problematic_count}")
print(f"✅ Data quality: {'100%' if problematic_count == 0 and null_degrees == 0 else 'Needs review'}")
print(f"✅ Ready for MySQL database: {'YES' if problematic_count == 0 and null_degrees == 0 else 'NO'}")

if problematic_count == 0 and null_degrees == 0:
    print(f"\n🎉 PERFECT! Dataset is completely clean and ready for database insertion!")
    print(f"📁 Use file: bangalore_doctors_perfect_cleaned.csv")
else:
    print(f"\n⚠️ Still needs attention: {problematic_count} entries")
