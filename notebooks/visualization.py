import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

# Load processed data
monthly = pd.read_csv("data/cleaned/monthly_business_counts.csv")
monthly['date'] = pd.to_datetime(monthly['date'])

# Sort by date and reset index to ensure proper rolling calculation
monthly = monthly.sort_values('date').reset_index(drop=True)

yearly = pd.read_csv("data/cleaned/yearly_business_counts.csv")

# Crisis periods for shading
CRISES = {
    "Dot-Com": (datetime(2000, 1, 1), datetime(2002, 12, 31)),
    "Great Recession": (datetime(2008, 1, 1), datetime(2009, 12, 31)),
    "Oil Crash": (datetime(2014, 7, 1), datetime(2016, 12, 31)),
    "COVID-19": (datetime(2020, 3, 1), datetime(2021, 12, 31)),
    "Rate Shock": (datetime(2022, 1, 1), datetime(2023, 12, 31))
}

CRISIS_COLORS = {
    "Dot-Com": "lightblue",
    "Great Recession": "lightcoral",
    "Oil Crash": "lightyellow",
    "COVID-19": "lightpink",
    "Rate Shock": "lightgreen"
}

# =============================================================================
# VISUALIZATION 1: MONTHLY TREND WITH CRISIS OVERLAYS
# =============================================================================

fig, ax = plt.subplots(figsize=(18, 8))

ax.plot(monthly['date'], monthly['count'], linewidth=1.5, color='navy', 
        label='Monthly Business Licences', alpha=0.6)

# Add 12-month rolling average - use min_periods to handle edges better
monthly['rolling_avg'] = monthly['count'].rolling(window=12, center=True, min_periods=1).mean()
ax.plot(monthly['date'], monthly['rolling_avg'], linewidth=3, color='red', 
        label='12-Month Rolling Average', linestyle='--', alpha=0.8)

# Shade crisis periods
for crisis_name, (start, end) in CRISES.items():
    ax.axvspan(start, end, alpha=0.3, color=CRISIS_COLORS[crisis_name], label=crisis_name)

ax.set_xlabel("Year", fontsize=14, fontweight='bold')
ax.set_ylabel("Number of Business Licences Issued", fontsize=14, fontweight='bold')
ax.set_title("Vancouver Business Licence Trends with Economic Crisis Periods (1997-2024)", 
             fontsize=16, fontweight='bold', pad=20)
ax.set_ylim(0, monthly['rolling_avg'].max() * 1.2)
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("results/crisis_timeline_monthly.png", dpi=300, bbox_inches='tight')
plt.show()

print("✓ Saved: crisis_timeline_monthly.png")

# =============================================================================
# VISUALIZATION 2: YEAR-OVER-YEAR GROWTH RATE
# =============================================================================

fig, ax = plt.subplots(figsize=(16, 8))

# Calculate YoY growth
yearly['yoy_growth'] = yearly['count'].pct_change() * 100

# Plot as bar chart
colors = ['red' if x < 0 else 'green' for x in yearly['yoy_growth']]
ax.bar(yearly['year'], yearly['yoy_growth'], color=colors, alpha=0.6, edgecolor='black')

# Add zero line
ax.axhline(0, color='black', linewidth=1, linestyle='-')

# Annotate crisis years
crisis_years = {2000: "Dot-Com", 2008: "GFC", 2014: "Oil", 2020: "COVID", 2022: "Rates"}
for year, label in crisis_years.items():
    if year in yearly['year'].values:
        y_val = yearly[yearly['year'] == year]['yoy_growth'].values[0]
        ax.annotate(label, xy=(year, y_val), xytext=(year, y_val + 5),
                   fontsize=10, fontweight='bold', ha='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

ax.set_xlabel("Year", fontsize=14, fontweight='bold')
ax.set_ylabel("Year-over-Year Growth (%)", fontsize=14, fontweight='bold')
ax.set_title("Year-over-Year Business Licence Growth Rate", fontsize=16, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig("results/yoy_growth_rate.png", dpi=300, bbox_inches='tight')
plt.show()

print("✓ Saved: yoy_growth_rate.png")

# =============================================================================
# VISUALIZATION 3: CRISIS COMPARISON
# =============================================================================

# Calculate average monthly licences during each crisis vs baseline
crisis_stats = []

for crisis_name, (start, end) in CRISES.items():
    crisis_data = monthly[(monthly['date'] >= start) & (monthly['date'] <= end)]
    
    # Baseline: 2 years before crisis
    baseline_start = start - pd.DateOffset(years=2)
    baseline_end = start - pd.DateOffset(days=1)
    baseline_data = monthly[(monthly['date'] >= baseline_start) & (monthly['date'] <= baseline_end)]
    
    if len(crisis_data) > 0 and len(baseline_data) > 0:
        crisis_avg = crisis_data['count'].mean()
        baseline_avg = baseline_data['count'].mean()
        pct_change = ((crisis_avg - baseline_avg) / baseline_avg) * 100
        
        crisis_stats.append({
            'Crisis': crisis_name,
            'Baseline Avg': baseline_avg,
            'Crisis Avg': crisis_avg,
            'Change (%)': pct_change
        })

crisis_df = pd.DataFrame(crisis_stats)

fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(crisis_df))
width = 0.35

bars1 = ax.bar(x - width/2, crisis_df['Baseline Avg'], width, label='2-Year Baseline', 
               color='lightblue', edgecolor='black')
bars2 = ax.bar(x + width/2, crisis_df['Crisis Avg'], width, label='During Crisis', 
               color='coral', edgecolor='black')

# Add percentage labels
for i, (idx, row) in enumerate(crisis_df.iterrows()):
    change = row['Change (%)']
    color = 'red' if change < 0 else 'green'
    ax.text(i, max(row['Baseline Avg'], row['Crisis Avg']) + 50, 
            f"{change:+.1f}%", ha='center', fontweight='bold', color=color, fontsize=11)

ax.set_xlabel("Economic Crisis", fontsize=14, fontweight='bold')
ax.set_ylabel("Average Monthly Business Licences", fontsize=14, fontweight='bold')
ax.set_title("Business Licence Activity: Baseline vs Crisis Period", fontsize=16, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(crisis_df['Crisis'], rotation=15, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig("results/crisis_comparison.png", dpi=300, bbox_inches='tight')
plt.show()

print("✓ Saved: crisis_comparison.png")

# =============================================================================
# VISUALIZATION 4: RECOVERY TIME ANALYSIS
# =============================================================================

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

for idx, (crisis_name, (start, end)) in enumerate(CRISES.items()):
    if idx >= len(axes):
        break
        
    ax = axes[idx]
    
    # Get data 1 year before to 2 years after crisis
    plot_start = start - pd.DateOffset(years=1)
    plot_end = end + pd.DateOffset(years=2)
    
    crisis_window = monthly[(monthly['date'] >= plot_start) & (monthly['date'] <= plot_end)].copy()
    
    if len(crisis_window) == 0:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
        ax.set_title(crisis_name, fontsize=12, fontweight='bold')
        continue
    
    # Normalize to crisis start = 0
    crisis_window['months_from_start'] = ((crisis_window['date'].dt.year - start.year) * 12 + 
                                          (crisis_window['date'].dt.month - start.month))
    
    # Only plot if we have substantial data (more than 5 points)
    if len(crisis_window[crisis_window['count'] > 0]) > 5:
        ax.plot(crisis_window['months_from_start'], crisis_window['count'], 
                linewidth=2, color='navy')
    else:
        # For sparse data, use scatter plot
        ax.scatter(crisis_window['months_from_start'], crisis_window['count'], 
                  s=50, color='navy', alpha=0.6)
        ax.plot(crisis_window['months_from_start'], crisis_window['count'], 
                linewidth=1, color='navy', alpha=0.3, linestyle='--')
    
    ax.axvspan(-12, (end.year - start.year)*12 + (end.month - start.month), 
               alpha=0.3, color=CRISIS_COLORS[crisis_name])
    ax.axvline(0, color='red', linestyle='--', linewidth=2, label='Crisis Start')
    ax.set_title(f"{crisis_name}\n(n={len(crisis_window[crisis_window['count'] > 0])} months with data)", 
                 fontsize=11, fontweight='bold')
    ax.set_xlabel("Months from Crisis Start", fontsize=10)
    ax.set_ylabel("Licences Issued", fontsize=10)
    ax.grid(True, alpha=0.3)

# Remove extra subplot
if len(CRISES) < len(axes):
    fig.delaxes(axes[-1])

plt.suptitle("Recovery Patterns: Business Licences Before, During, and After Each Crisis", 
             fontsize=16, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig("results/recovery_patterns.png", dpi=300, bbox_inches='tight')
plt.show()

print("✓ Saved: recovery_patterns.png")

print("\n" + "="*70)
print("ALL VISUALIZATIONS COMPLETE!")
print("="*70)
