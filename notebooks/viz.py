import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

raw = pd.read_csv("data/cleaned/business_licences_1997_2024.csv")
raw['issueddate'] = pd.to_datetime(raw['issueddate'], errors='coerce')
raw['date'] = raw['issueddate']

# rename it to 'date' so the rest of the script works:
raw = raw.rename(columns={'issueddate': 'date'})

os.makedirs("results", exist_ok=True)

raw = pd.read_csv("data/cleaned/business_licences_1997_2024.csv")

    # FIX: use issueddate instead of 'date'
raw['issueddate'] = pd.to_datetime(raw['issueddate'], errors='coerce')
raw = raw.rename(columns={'issueddate': 'date'})

sector_impact = []

CRISES = {
        "Dot-Com": (datetime(2000, 1, 1), datetime(2002, 12, 31)),
        "Great Recession": (datetime(2008, 1, 1), datetime(2009, 12, 31)),
        "Oil Crash": (datetime(2014, 7, 1), datetime(2016, 12, 31)),
        "COVID-19": (datetime(2020, 3, 1), datetime(2021, 12, 31)),
        "Rate Shock": (datetime(2022, 1, 1), datetime(2023, 12, 31))
    }

for crisis_name, (start, end) in CRISES.items():
        crisis_df = raw[(raw['date'] >= start) & (raw['date'] <= end)]
        baseline_df = raw[(raw['date'] >= (start - pd.DateOffset(years=2))) & (raw['date'] < start)]

        if len(crisis_df) == 0 or len(baseline_df) == 0:
            print(f"Skipping {crisis_name} (no usable data)")
            continue

        crisis_counts = crisis_df['businesstype'].value_counts(normalize=True)
        baseline_counts = baseline_df['businesstype'].value_counts(normalize=True)

        sectors = pd.DataFrame({
            'businesstype': baseline_counts.index,
            'baseline_pct': baseline_counts.values,
            'crisis_pct': crisis_counts.reindex(baseline_counts.index, fill_value=0).values
        })

        sectors['pct_change'] = (sectors['crisis_pct'] - sectors['baseline_pct']) * 100
        sectors['crisis'] = crisis_name
        sector_impact.append(sectors)

sector_df = pd.concat(sector_impact)

heat = sector_df.pivot_table(index='businesstype', columns='crisis', values='pct_change')

plt.figure(figsize=(10,12))
sns.heatmap(heat, cmap='coolwarm', center=0)
plt.title("Sector-Level Impact Heatmap")
plt.tight_layout()
plt.savefig("results/sector_level_crisis_impact.png", dpi=300, bbox_inches='tight')
plt.show()


print("✓ Saved: sector_level_crisis_impact.png")




##########
#plot 2 - how the top 10 sectors did during the crises
##########
top_sectors = sector_df.groupby('businesstype')['baseline_pct'].mean().nlargest(10).index
sector_top_df = sector_df[sector_df['businesstype'].isin(top_sectors)]

# Create "period" column
def categorize_period(row):
    if row['crisis'] in CRISES:
        start, end = CRISES[row['crisis']]
        if row['date'] < start:
            return 'baseline'
        elif start <= row['date'] <= end:
            return 'during'
        else:
            return 'post'
    return 'other'

# For this approach, you might need to calculate pre/during/post averages
# Example: pivot table with baseline, during, post
plot_data = []

for crisis_name, (start, end) in CRISES.items():
    baseline_df = raw[(raw['date'] >= (start - pd.DateOffset(years=2))) & (raw['date'] < start)]
    crisis_df = raw[(raw['date'] >= start) & (raw['date'] <= end)]
    post_df = raw[(raw['date'] > end) & (raw['date'] <= (end + pd.DateOffset(years=2)))]

    for sector in top_sectors:
        baseline_avg = baseline_df[baseline_df['businesstype']==sector].shape[0]
        crisis_avg = crisis_df[crisis_df['businesstype']==sector].shape[0]
        post_avg = post_df[post_df['businesstype']==sector].shape[0]
        
        plot_data.append({'sector': sector, 'crisis': crisis_name, 'period': 'baseline', 'count': baseline_avg})
        plot_data.append({'sector': sector, 'crisis': crisis_name, 'period': 'during', 'count': crisis_avg})
        plot_data.append({'sector': sector, 'crisis': crisis_name, 'period': 'post', 'count': post_avg})

plot_df = pd.DataFrame(plot_data)

# Compute % change relative to baseline
plot_df['pct_change'] = plot_df.groupby(['crisis','sector'])['count'].transform(lambda x: (x - x.iloc[0])/x.iloc[0]*100)

# Plot
plt.figure(figsize=(12,6))
sns.barplot(
    data=plot_df[plot_df['period']!='baseline'], 
    x='sector', y='pct_change', hue='period'
)
plt.xticks(rotation=45, ha='right')
plt.xlabel("Sector")
plt.ylabel("Change vs Baseline (%)")
plt.title("Top 10 Sectors: Crisis Impact")
plt.tight_layout()
plt.savefig("results/affect_of_crises_on_top10_sectors.png", dpi=300, bbox_inches='tight')
plt.show()