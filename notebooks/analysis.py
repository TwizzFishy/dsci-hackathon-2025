import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Load cleaned data
df = pd.read_csv("data/cleaned/business_licences_1997_2024.csv")

print(f"Loaded {len(df):,} business records")
print(f"Columns: {list(df.columns)}")

# =============================================================================
# STEP 1: DATA PREPARATION
# =============================================================================

# Parse dates - check what date columns exist
date_columns = [col for col in df.columns if 'date' in col.lower()]
print(f"\nDate columns found: {date_columns}")

# Parse the issueddate column - it has mixed formats
# Old: '1998-02-25', New: '2023-03-01T05:57:01+00:00'
if 'issueddate' in df.columns:
    # First attempt: try to parse as-is with UTC
    df['issued_date'] = pd.to_datetime(df['issueddate'], errors='coerce', utc=True)
    
    # Convert UTC to naive datetime (remove timezone info)
    df['issued_date'] = df['issued_date'].dt.tz_localize(None)
    
elif 'issued_date' in df.columns:
    df['issued_date'] = pd.to_datetime(df['issued_date'], errors='coerce')

# Extract time components from issued_date
if df['issued_date'].notna().any():
    df['year_from_date'] = df['issued_date'].dt.year
    df['month'] = df['issued_date'].dt.month
    df['year_month'] = df['issued_date'].dt.to_period('M')
else:
    df['year_from_date'] = None
    df['month'] = None
    df['year_month'] = None

# The 'year' column already exists in your data and has more complete data
# Use it as the primary year field
if 'year' not in df.columns:
    df['year'] = df['year_from_date']

# Remove records without dates or years
df_with_dates = df[(df['issued_date'].notna()) | (df['year'].notna())].copy()

# For records with year but no issued_date, create a date from the year
mask = df_with_dates['issued_date'].isna() & df_with_dates['year'].notna()
if mask.any():
    # Create date as January 1st of that year for grouping purposes
    df_with_dates.loc[mask, 'issued_date'] = pd.to_datetime(df_with_dates.loc[mask, 'year'].astype(int).astype(str) + '-01-01')
    df_with_dates.loc[mask, 'year_month'] = df_with_dates.loc[mask, 'issued_date'].dt.to_period('M')

print(f"\nRecords with valid dates: {len(df_with_dates):,}")
print(f"Date range: {df_with_dates['issued_date'].min()} to {df_with_dates['issued_date'].max()}")
print(f"Year range: {df_with_dates['year'].min():.0f} to {df_with_dates['year'].max():.0f}")

# =============================================================================
# STEP 2: DEFINE CRISIS PERIODS
# =============================================================================

CRISES = {
    "Dot-Com Crash": ("2000-01", "2002-12"),
    "Great Recession": ("2008-01", "2009-12"),
    "Oil Price Crash": ("2014-07", "2016-12"),
    "COVID-19": ("2020-03", "2021-12"),
    "Interest Rate Shock": ("2022-01", "2023-12")
}

# Add crisis indicator column
def identify_crisis(date):
    if pd.isna(date):
        return "None"
    for crisis_name, (start, end) in CRISES.items():
        if start <= date.strftime('%Y-%m') <= end:
            return crisis_name
    return "Normal"

df_with_dates['crisis_period'] = df_with_dates['issued_date'].apply(identify_crisis)

# =============================================================================
# STEP 3: AGGREGATE DATA FOR TIME SERIES
# =============================================================================

# Monthly business licence counts
monthly_counts = df_with_dates.groupby('year_month').size().reset_index(name='count')
monthly_counts['year_month_str'] = monthly_counts['year_month'].astype(str)
monthly_counts['date'] = pd.to_datetime(monthly_counts['year_month_str'])

# Sort by date to ensure proper ordering
monthly_counts = monthly_counts.sort_values('date').reset_index(drop=True)

# Fill in missing months with 0 counts
# Create a complete date range
date_range = pd.date_range(start=monthly_counts['date'].min(), 
                           end=monthly_counts['date'].max(), 
                           freq='MS')  # Month Start frequency

# Create complete monthly dataframe
complete_months = pd.DataFrame({'date': date_range})
complete_months['year_month'] = complete_months['date'].dt.to_period('M')

# Merge with actual counts, filling missing with 0
monthly_counts = complete_months.merge(monthly_counts[['date', 'count']], 
                                       on='date', 
                                       how='left')
monthly_counts['count'] = monthly_counts['count'].fillna(0)

print(f"\nMonthly data points: {len(monthly_counts)}")
print(f"Months with zero licences: {(monthly_counts['count'] == 0).sum()}")

# Yearly counts
yearly_counts = df_with_dates.groupby('year').size().reset_index(name='count')

# Status by year (active vs closed)
if 'status' in df_with_dates.columns:
    status_by_year = df_with_dates.groupby(['year', 'status']).size().unstack(fill_value=0)
    
# Business type trends
if 'businesstype' in df_with_dates.columns:
    top_business_types = df_with_dates['businesstype'].value_counts().head(10).index
    df_top_types = df_with_dates[df_with_dates['businesstype'].isin(top_business_types)]
    type_by_year = df_top_types.groupby(['year', 'businesstype']).size().unstack(fill_value=0)

# =============================================================================
# STEP 4: CALCULATE CRISIS METRICS
# =============================================================================

print("\n" + "="*70)
print("CRISIS IMPACT ANALYSIS")
print("="*70)

for crisis_name, (start, end) in CRISES.items():
    # Get data for crisis period
    crisis_data = df_with_dates[df_with_dates['crisis_period'] == crisis_name]
    
    # Get baseline (year before crisis)
    start_year = int(start[:4]) - 1
    baseline_data = df_with_dates[df_with_dates['year'] == start_year]
    
    crisis_count = len(crisis_data)
    baseline_count = len(baseline_data)
    
    if baseline_count > 0:
        change_pct = ((crisis_count - baseline_count) / baseline_count) * 100
        print(f"\n{crisis_name} ({start} to {end}):")
        print(f"  Baseline year ({start_year}): {baseline_count:,} licences")
        print(f"  Crisis period total: {crisis_count:,} licences")
        print(f"  Change: {change_pct:+.1f}%")
        
        # Show top affected business types during crisis
        if 'businesstype' in df_with_dates.columns:
            crisis_types = crisis_data['businesstype'].value_counts().head(5)
            print(f"  Top business types during crisis:")
            for btype, count in crisis_types.items():
                print(f"    - {btype}: {count:,}")

# =============================================================================
# STEP 5: SAVE PROCESSED DATA
# =============================================================================

# Save aggregated datasets for visualization
monthly_counts.to_csv("data/cleaned/monthly_business_counts.csv", index=False)
yearly_counts.to_csv("data/cleaned/yearly_business_counts.csv", index=False)

if 'status' in df_with_dates.columns:
    status_by_year.to_csv("data/cleaned/status_by_year.csv")

if 'businesstype' in df_with_dates.columns:
    type_by_year.to_csv("data/cleaned/business_type_by_year.csv")

print("\n" + "="*70)
print("DATA WRANGLING COMPLETE!")
print("="*70)
print("\nFiles saved:")
print("  - data/cleaned/monthly_business_counts.csv")
print("  - data/cleaned/yearly_business_counts.csv")
print("  - data/cleaned/status_by_year.csv")
print("  - data/cleaned/business_type_by_year.csv")

print("\nDate range:", df_with_dates['issued_date'].min(), "to", df_with_dates['issued_date'].max())
print(f"\nCrisis period breakdown:")
print(df_with_dates['crisis_period'].value_counts())


######linear model to predict the forcasted no of business licenses in the top sector in
# the next 3-5 years based on how they survived previous crises
from sklearn.linear_model import LinearRegression
import numpy as np

forecast_list = []

all_types = df_with_dates['businesstype'].unique()

for btype in all_types:
    subset = df_with_dates[df_with_dates['businesstype'] == btype]
    
    yearly = subset.groupby('year').size().reset_index(name='count')

    if len(yearly) < 5:   # too little data, skip
        continue

    X = yearly['year'].values.reshape(-1, 1)
    y = yearly['count'].values

    model = LinearRegression()
    model.fit(X, y)

    future_years = np.arange(2025, 2030)
    predicted_counts = model.predict(future_years.reshape(-1, 1))

    for year, pred in zip(future_years, predicted_counts):
        forecast_list.append({
            'businesstype': btype,
            'year': year,
            'predicted_count': max(0, pred)   # no negatives
        })

forecast_df = pd.DataFrame(forecast_list)
print("\nGenerated forecast table:")
print(forecast_df.head(20))
print("\nTotal predictions:", len(forecast_df))