import pandas as pd

df = pd.read_csv("data/cleaned/business_licences_1997_2024.csv")

print("="*70)
print("DATE COLUMN DIAGNOSTIC")
print("="*70)

print(f"\nAll columns in dataset:")
for col in df.columns:
    print(f"  - {col}")

date_cols = [col for col in df.columns if 'date' in col.lower() or 'year' in col.lower()]
print(f"\nDate-related columns: {date_cols}")

# Check each date column
for col in date_cols:
    print(f"\n{col}:")
    print(f"  Data type: {df[col].dtype}")
    print(f"  Non-null count: {df[col].notna().sum():,} / {len(df):,}")
    print(f"  Sample values:")
    print(f"    {df[col].dropna().head(10).tolist()}")
    
    # Try to parse as datetime
    try:
        parsed = pd.to_datetime(df[col], errors='coerce')
        valid_dates = parsed.notna().sum()
        print(f"  Valid dates after parsing: {valid_dates:,}")
        if valid_dates > 0:
            print(f"  Date range: {parsed.min()} to {parsed.max()}")
            print(f"  Year distribution:")
            year_counts = parsed.dt.year.value_counts().sort_index()
            print(year_counts.tail(15))  # Show last 15 years
    except Exception as e:
        print(f"  Error parsing: {e}")

# Check the year column specifically
if 'year' in df.columns:
    print(f"\n\nYear column distribution:")
    print(df['year'].value_counts().sort_index().tail(20))
    print(f"\nYears with data: {df['year'].min()} to {df['year'].max()}")
    print(f"Missing years: {df['year'].isna().sum():,}")

# Check if there's data after 2012
print(f"\n\nRecords by year range:")
if 'year' in df.columns:
    print(f"  1997-2012: {len(df[df['year'] <= 2012]):,}")
    print(f"  2013-2024: {len(df[df['year'] >= 2013]):,}")
    print(f"  Missing year: {len(df[df['year'].isna()]):,}")

# Show sample of recent records
print(f"\n\nSample of records from 2020+:")
if 'year' in df.columns:
    recent = df[df['year'] >= 2020].head(10)
    print(recent[['year'] + [col for col in date_cols if col in df.columns]])

