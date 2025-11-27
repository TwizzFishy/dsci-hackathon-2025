import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from scipy import stats
from pandas.tseries.offsets import MonthEnd

# Load cleaned data
df = pd.read_csv("data/cleaned/business_licences_1997_2024.csv")

print(f"Loaded {len(df):,} business records")
print(f"Columns: {list(df.columns)}")

# Check folderyear distribution to understand data sources
print("\n" + "="*70)
print("FOLDERYEAR DISTRIBUTION (Data Source Indicator)")
print("="*70)
if 'folderyear' in df.columns:
    print(df['folderyear'].value_counts().sort_index())
    print(f"\nNote: folderyear likely indicates which source file the record came from")
    print("  - 97-12 range: from 1997_2012.csv")
    print("  - 13-24 range: from 2013_2024.csv") 
    print("  - 24: from current_2024_plus.csv")

# =============================================================================
# STEP 1: DATA PREPARATION (robust date parsing & synthesis)
# =============================================================================

# Try to find a candidate date column automatically
date_cols = [c for c in df.columns if 'issued' in c.lower() or ('date' in c.lower() and c.lower() != 'year')]
print(f"\nCandidate date columns: {date_cols}")

preferred = ['issueddate', 'issued_date', 'date_issued', 'date']
chosen_date_col = None
for col in preferred:
    if col in df.columns:
        chosen_date_col = col
        break
if chosen_date_col is None and date_cols:
    chosen_date_col = date_cols[0]

print("Using date column:", chosen_date_col)

# Parse chosen date column robustly
if chosen_date_col is not None:
    # coerce to datetime, allow mixed formats, handle timezone
    df['issued_date'] = pd.to_datetime(df[chosen_date_col], errors='coerce', utc=True)
    # remove timezone info if present
    try:
        df['issued_date'] = df['issued_date'].dt.tz_convert(None)
    except Exception:
        # if dt.tz_convert fails, try tz_localize (some values may be tz-naive)
        try:
            df['issued_date'] = df['issued_date'].dt.tz_localize(None)
        except Exception:
            pass
else:
    df['issued_date'] = pd.NaT

# If we have a 'year' column, coerce it and synthesize dates for missing issued_date
if 'year' in df.columns:
    df['year_numeric'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')
    missing_date_mask = df['issued_date'].isna() & df['year_numeric'].notna()
    if missing_date_mask.any():
        df.loc[missing_date_mask, 'issued_date'] = pd.to_datetime(
            df.loc[missing_date_mask, 'year_numeric'].astype(int).astype(str) + '-01-01'
        )

# Final coercion to datetime (ensures consistent dtype)
df['issued_date'] = pd.to_datetime(df['issued_date'], errors='coerce')

# Create tidy time columns
df['year'] = pd.to_numeric(df['issued_date'].dt.year, errors='coerce').astype('Int64')
df['month'] = df['issued_date'].dt.month
df['month_start'] = df['issued_date'].dt.to_period('M').dt.to_timestamp()

print(f"Records with valid issued_date: {df['issued_date'].notna().sum():,} / {len(df):,}")

# Keep only rows with any date info (you may decide to keep rows missing dates separately)
df_with_dates = df[df['issued_date'].notna()].copy()

if len(df_with_dates) == 0:
    print("No records with valid dates found. Check your CSV's date columns.")
else:
    print(f"Date range: {df_with_dates['issued_date'].min()} to {df_with_dates['issued_date'].max()}")
    # Year range - convert Int64 to python int for display
    yr_min = int(df_with_dates['year'].min())
    yr_max = int(df_with_dates['year'].max())
    print(f"Year range: {yr_min} to {yr_max}")

# Check for gaps in years (diagnostic)
if len(df_with_dates) > 0 and not pd.isna(df_with_dates['year'].min()):
    all_years = set(range(int(df_with_dates['year'].min()), int(df_with_dates['year'].max()) + 1))
    present_years = set(df_with_dates['year'].dropna().astype(int).unique())
    missing_years = sorted(all_years - present_years)
    print("\n" + "="*70)
    print("CHECKING FOR YEAR GAPS")
    print("="*70)
    if missing_years:
        print(f"WARNING: Missing years in data: {missing_years}")
        print("This could explain why some crisis periods show 0 records")
    else:
        print("No year gaps detected")

# =============================================================================
# STEP 2: DEFINE CRISIS PERIODS (use Timestamp ranges)
# =============================================================================

CRISES = {
    "Dot-Com Crash": ("2000-01", "2002-12"),
    "Great Recession": ("2008-01", "2009-12"),
    "Oil Price Crash": ("2014-07", "2016-12"),
    "COVID-19": ("2020-03", "2021-12"),
    "Interest Rate Shock": ("2022-01", "2023-12")
}

# Convert crisis ranges to Timestamp intervals
CRISES_TS = {
    name: (pd.to_datetime(start + "-01"), pd.to_datetime(end + "-01") + MonthEnd(0))
    for name, (start, end) in CRISES.items()
}

# Assign crisis_period by vectorized timestamp comparisons
df_with_dates['crisis_period'] = 'Normal'  # default
for name, (start_ts, end_ts) in CRISES_TS.items():
    mask = df_with_dates['issued_date'].notna() & (df_with_dates['issued_date'] >= start_ts) & (df_with_dates['issued_date'] <= end_ts)
    df_with_dates.loc[mask, 'crisis_period'] = name

print("\nApplying crisis identification... done")

# DIAGNOSTIC: sample dates and types for a few years
print("\n" + "="*70)
print("DATE FORMAT DIAGNOSTIC")
print("="*70)
for year in [2000, 2010, 2019, 2020, 2021, 2022, 2023, 2024]:
    sample = df_with_dates[df_with_dates['year'] == year]['issued_date'].head(3)
    if len(sample) > 0:
        print(f"\n{year}:")
        for dt in sample:
            print(f"  {dt} (type: {type(dt).__name__})")

# =============================================================================
# STEP 3: AGGREGATE DATA FOR TIME SERIES (monthly & yearly)
# =============================================================================

# Monthly business licence counts using month_start
if len(df_with_dates) > 0:
    monthly_counts = (
        df_with_dates
        .groupby('month_start')
        .size()
        .rename('count')
        .reset_index()
    )

    # Create a complete month series
    date_range = pd.date_range(monthly_counts['month_start'].min(), monthly_counts['month_start'].max(), freq='MS')
    complete_months = pd.DataFrame({'month_start': date_range})
    monthly_counts = complete_months.merge(monthly_counts, on='month_start', how='left').fillna({'count': 0})
    monthly_counts['count'] = monthly_counts['count'].astype(int)
    monthly_counts = monthly_counts.sort_values('month_start').reset_index(drop=True)
    monthly_counts['date'] = monthly_counts['month_start']  # alias for older code sections

    print(f"\nMonthly data points: {len(monthly_counts)}")
    print(f"Months with zero licences: {(monthly_counts['count'] == 0).sum()}")
else:
    monthly_counts = pd.DataFrame(columns=['month_start', 'count', 'date'])
    print("\nNo monthly counts produced (no dated records).")

# Yearly counts
if len(df_with_dates) > 0:
    yearly_counts = df_with_dates.groupby('year').size().reset_index(name='count')
else:
    yearly_counts = pd.DataFrame(columns=['year', 'count'])

# Status by year (active vs closed)
status_by_year = None
if 'status' in df_with_dates.columns and len(df_with_dates) > 0:
    status_by_year = df_with_dates.groupby(['year', 'status']).size().unstack(fill_value=0)

# Business type trends
type_by_year = None
if 'businesstype' in df_with_dates.columns and len(df_with_dates) > 0:
    top_business_types = df_with_dates['businesstype'].value_counts().head(10).index
    df_top_types = df_with_dates[df_with_dates['businesstype'].isin(top_business_types)]
    type_by_year = df_top_types.groupby(['year', 'businesstype']).size().unstack(fill_value=0)

# =============================================================================
# STEP 4: BOOTSTRAP CRISIS IMPACT ANALYSIS (simplified, correct)
# =============================================================================

def bootstrap_crisis_impact(data, crisis_name, baseline_year, n_bootstrap=1000, random_state=0):
    """
    Bootstrap confidence intervals for crisis impact metrics.
    Uses Poisson draws on counts (sensible for count data) to get distribution of changes.
    Returns dict with baseline_count, crisis_count, mean_change (pct), ci (2.5,97.5) or abs stats.
    """
    rng = np.random.default_rng(random_state)
    baseline_count = int(data[data['year'] == baseline_year].shape[0])
    crisis_count = int(data[data['crisis_period'] == crisis_name].shape[0])

    # No data at all
    if baseline_count == 0 and crisis_count == 0:
        return {'baseline_count': 0, 'crisis_count': 0, 'mean_change': np.nan, 'ci': (np.nan, np.nan)}

    # If baseline missing, return absolute bootstrap of crisis_count
    if baseline_count == 0:
        bs = rng.poisson(lam=crisis_count, size=n_bootstrap)
        return {
            'baseline_count': 0,
            'crisis_count': crisis_count,
            'mean_change': np.nan,
            'ci': (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))),
            'abs_mean': float(bs.mean())
        }

    # If crisis_count is 0, nothing to compute
    if crisis_count == 0:
        return {'baseline_count': baseline_count, 'crisis_count': 0, 'mean_change': np.nan, 'ci': (np.nan, np.nan)}

    # Bootstrap percentage changes
    changes = []
    for _ in range(n_bootstrap):
        b = rng.poisson(lam=baseline_count)
        c = rng.poisson(lam=crisis_count)
        if b > 0:
            changes.append(((c - b) / b) * 100.0)
    if len(changes) == 0:
        return {'baseline_count': baseline_count, 'crisis_count': crisis_count, 'mean_change': np.nan, 'ci': (np.nan, np.nan)}

    return {
        'baseline_count': baseline_count,
        'crisis_count': crisis_count,
        'mean_change': float(np.mean(changes)),
        'ci': (float(np.percentile(changes, 2.5)), float(np.percentile(changes, 97.5)))
    }

print("\n" + "="*70)
print("BOOTSTRAPPED CRISIS IMPACT ANALYSIS")
print("="*70)

crisis_results = {}
for crisis_name, (start, end) in CRISES.items():
    baseline_year = int(start[:4]) - 1
    out = bootstrap_crisis_impact(df_with_dates, crisis_name, baseline_year, n_bootstrap=1000)
    crisis_results[crisis_name] = out

    print(f"\n{crisis_name} ({start} to {end}):")
    print(f"  Baseline year ({baseline_year}): {out['baseline_count']:,} licences")
    print(f"  Crisis period total: {out['crisis_count']:,} licences")
    if not pd.isna(out.get('mean_change')):
        ci_low, ci_high = out['ci']
        print(f"  Mean change: {out['mean_change']:+.1f}%")
        print(f"  95% CI: [{ci_low:+.1f}%, {ci_high:+.1f}%]")
    else:
        if 'abs_mean' in out:
            print(f"  No baseline available; crisis absolute mean (bootstrap): {out['abs_mean']:.1f}")
            print(f"  95% CI (abs): [{out['ci'][0]:.1f}, {out['ci'][1]:.1f}]")
        else:
            print("  Unable to calculate change (insufficient data)")

    # Show top affected business types during crisis
    if 'businesstype' in df_with_dates.columns and out['crisis_count'] > 0:
        crisis_data = df_with_dates[df_with_dates['crisis_period'] == crisis_name]
        crisis_types = crisis_data['businesstype'].value_counts().head(5)
        print(f"  Top business types during crisis:")
        for btype, count in crisis_types.items():
            print(f"    - {btype}: {count:,}")

# =============================================================================
# STEP 5: BOOTSTRAPPED FORECAST WITH CONFIDENCE INTERVALS
# =============================================================================

def bootstrap_forecast(X, y, future_years, n_bootstrap=1000, random_state=0):
    """
    Bootstrap confidence intervals for linear regression forecasts
    X: numpy array of years
    y: numpy array of counts
    future_years: numpy array of years to predict
    """
    rng = np.random.default_rng(random_state)
    predictions = []
    n = len(X)
    for _ in range(n_bootstrap):
        indices = rng.integers(0, n, size=n)
        X_boot = X[indices]
        y_boot = y[indices]
        model = LinearRegression()
        model.fit(X_boot.reshape(-1, 1), y_boot)
        pred = model.predict(future_years.reshape(-1, 1))
        predictions.append(pred)

    predictions = np.array(predictions)
    mean_pred = np.mean(predictions, axis=0)
    ci_lower = np.percentile(predictions, 2.5, axis=0)
    ci_upper = np.percentile(predictions, 97.5, axis=0)

    return mean_pred, ci_lower, ci_upper

print("\n" + "="*70)
print("BOOTSTRAPPED FORECAST ANALYSIS")
print("="*70)

forecast_list = []
all_types = df_with_dates['businesstype'].unique() if 'businesstype' in df_with_dates.columns else []

for btype in all_types:
    subset = df_with_dates[df_with_dates['businesstype'] == btype]
    yearly = subset.groupby('year').size().reset_index(name='count')

    if len(yearly) < 5:
        continue

    X = yearly['year'].astype(int).values
    y = yearly['count'].values
    future_years = np.arange(2025, 2030)

    mean_pred, ci_lower, ci_upper = bootstrap_forecast(X, y, future_years, n_bootstrap=500)

    for year, pred, lower, upper in zip(future_years, mean_pred, ci_lower, ci_upper):
        forecast_list.append({
            'businesstype': btype,
            'year': int(year),
            'predicted_count': max(0, float(pred)),
            'ci_lower': max(0, float(lower)),
            'ci_upper': max(0, float(upper))
        })

forecast_df = pd.DataFrame(forecast_list)

# Show top 5 business types by 2029 predicted count
if not forecast_df.empty:
    top_forecasts = forecast_df[forecast_df['year'] == 2029].nlargest(5, 'predicted_count')
    print("\nTop 5 business types forecasted for 2029 (with 95% CI):")
    for idx, row in top_forecasts.iterrows():
        print(f"  {row['businesstype']}: {row['predicted_count']:.0f} "
              f"[{row['ci_lower']:.0f}, {row['ci_upper']:.0f}]")
else:
    print("\nNo forecasts generated (insufficient business-type time series).")

# =============================================================================
# STEP 6: BOOTSTRAPPED CRISIS MODEL COEFFICIENTS (monthly)
# =============================================================================

def bootstrap_ols_coefficients(X, y, n_bootstrap=1000, random_state=0):
    coef_samples = []
    rng = np.random.default_rng(random_state)
    n = len(X)
    # X should be a DataFrame (with const column)
    for _ in range(n_bootstrap):
        indices = rng.integers(0, n, size=n)
        X_boot = X.iloc[indices]
        y_boot = y.iloc[indices]
        model = sm.OLS(y_boot, X_boot).fit()
        coef_samples.append(model.params.values)
    coef_samples = np.array(coef_samples)
    mean_coef = np.mean(coef_samples, axis=0)
    ci_lower = np.percentile(coef_samples, 2.5, axis=0)
    ci_upper = np.percentile(coef_samples, 97.5, axis=0)
    return mean_coef, ci_lower, ci_upper

print("\n" + "="*70)
print("BOOTSTRAPPED MONTHLY CRISIS MODEL")
print("="*70)

# Prepare monthly data and crisis indicator
if not monthly_counts.empty:
    def is_crisis_ts(date):
        for start_ts, end_ts in CRISES_TS.values():
            if start_ts <= date <= end_ts:
                return 1
        return 0

    monthly_counts['is_crisis'] = monthly_counts['date'].apply(is_crisis_ts)

    X = sm.add_constant(monthly_counts['is_crisis'])
    y = monthly_counts['count']

    # Original model
    model = sm.OLS(y, X).fit()
    print("\nOriginal OLS Model:")
    print(model.summary())

    # Bootstrapped coefficients
    mean_coef, ci_lower, ci_upper = bootstrap_ols_coefficients(X, y, n_bootstrap=1000)

    print("\n" + "="*70)
    print("BOOTSTRAPPED COEFFICIENT ESTIMATES (n=1000)")
    print("="*70)
    print(f"\nIntercept (Non-crisis baseline):")
    print(f"  Mean: {mean_coef[0]:.2f}")
    print(f"  95% CI: [{ci_lower[0]:.2f}, {ci_upper[0]:.2f}]")
    print(f"\nCrisis Effect:")
    print(f"  Mean: {mean_coef[1]:.2f}")
    print(f"  95% CI: [{ci_lower[1]:.2f}, {ci_upper[1]:.2f}]")

    if ci_lower[1] < 0 < ci_upper[1]:
        print(f"  Interpretation: Crisis effect is NOT statistically significant at 95% level")
    else:
        print(f"  Interpretation: Crisis effect IS statistically significant at 95% level")
else:
    print("Skipping monthly crisis model (no monthly data).")

# =============================================================================
# STEP 7: SAVE PROCESSED DATA
# =============================================================================

# Ensure output folder exists
import os
os.makedirs("data/cleaned", exist_ok=True)

monthly_counts.to_csv("data/cleaned/monthly_business_counts.csv", index=False)
yearly_counts.to_csv("data/cleaned/yearly_business_counts.csv", index=False)
forecast_df.to_csv("data/cleaned/business_forecast_with_ci.csv", index=False)

if status_by_year is not None:
    status_by_year.to_csv("data/cleaned/status_by_year.csv")

if type_by_year is not None:
    type_by_year.to_csv("data/cleaned/business_type_by_year.csv")

# Save bootstrap results
crisis_results_df = pd.DataFrame(crisis_results).T
crisis_results_df.to_csv("data/cleaned/crisis_bootstrap_results.csv")

print("\n" + "="*70)
print("DATA WRANGLING COMPLETE!")
print("="*70)
print("\nFiles saved:")
print("  - data/cleaned/monthly_business_counts.csv")
print("  - data/cleaned/yearly_business_counts.csv")
print("  - data/cleaned/business_forecast_with_ci.csv (NEW)")
print("  - data/cleaned/crisis_bootstrap_results.csv (NEW)")
if status_by_year is not None:
    print("  - data/cleaned/status_by_year.csv")
if type_by_year is not None:
    print("  - data/cleaned/business_type_by_year.csv")
