"""
Weekend vs Weekday comparison visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("Loading and analyzing data...")
bakery_df = pd.read_csv('../data/raw/BreadBasket_DMS.csv')

if 'TransactionNo' in bakery_df.columns:
    bakery_df.rename(columns={'TransactionNo': 'Transaction'}, inplace=True)
if 'Items' in bakery_df.columns:
    bakery_df.rename(columns={'Items': 'Item'}, inplace=True)
if 'DateTime' in bakery_df.columns:
    bakery_df['DateTime'] = pd.to_datetime(bakery_df['DateTime'])

bakery_df['Date'] = bakery_df['DateTime'].dt.date
bakery_df['Hour'] = bakery_df['DateTime'].dt.hour
bakery_df['DayOfWeekNum'] = bakery_df['DateTime'].dt.dayofweek
bakery_df['IsWeekend'] = bakery_df['DayOfWeekNum'].isin([5, 6])
bakery_df = bakery_df[bakery_df['Item'] != 'NONE'].copy()

# Calculate per-day averages
weekend_days = bakery_df[bakery_df['IsWeekend']]['Date'].nunique()
weekday_days = bakery_df[~bakery_df['IsWeekend']]['Date'].nunique()

weekend_hourly = bakery_df[bakery_df['IsWeekend']].groupby('Hour')['Transaction'].nunique() / weekend_days
weekday_hourly = bakery_df[~bakery_df['IsWeekend']].groupby('Hour')['Transaction'].nunique() / weekday_days

basket_sizes = bakery_df.groupby(['Transaction', 'IsWeekend']).size().reset_index(name='BasketSize')
weekend_basket_avg = basket_sizes[basket_sizes['IsWeekend'] == True]['BasketSize'].mean()
weekday_basket_avg = basket_sizes[basket_sizes['IsWeekend'] == False]['BasketSize'].mean()

morning_mask = bakery_df['Hour'] < 12
weekend_morning_avg = bakery_df[(bakery_df['IsWeekend']) & (morning_mask)].groupby('Date')['Transaction'].nunique().mean()
weekday_morning_avg = bakery_df[(~bakery_df['IsWeekend']) & (morning_mask)].groupby('Date')['Transaction'].nunique().mean()

# Simple clean style
plt.style.use('seaborn-v0_8-whitegrid')

# ============================================================================
# Create SIMPLE 2-panel visualization
# ============================================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
fig.suptitle('Weekend vs Weekday Patterns', fontsize=24, fontweight='bold', y=0.98)

# ----------------------------------------------------------------------------
# Panel 1: Hourly Pattern - SIMPLE, NO CLUTTER
# ----------------------------------------------------------------------------

ax1.plot(weekday_hourly.index, weekday_hourly.values,
         marker='s', linewidth=4, markersize=11, label='Weekday',
         color='#3498db', alpha=0.9, markeredgecolor='white', markeredgewidth=2)

ax1.plot(weekend_hourly.index, weekend_hourly.values,
         marker='o', linewidth=4, markersize=11, label='Weekend',
         color='#e74c3c', alpha=0.9, markeredgecolor='white', markeredgewidth=2)

# Mark peaks - SIMPLE dots, no ugly arrows
peak_hour = 11
ax1.plot(peak_hour, weekday_hourly[peak_hour], 'o', markersize=20,
         color='#3498db', markeredgecolor='black', markeredgewidth=3, zorder=5)
ax1.plot(peak_hour, weekend_hourly[peak_hour], 'o', markersize=20,
         color='#e74c3c', markeredgecolor='black', markeredgewidth=3, zorder=5)

# Simple text labels - NO overlapping
ax1.text(peak_hour + 0.3, weekday_hourly[peak_hour],
         f'{weekday_hourly[peak_hour]:.1f}',
         fontsize=16, fontweight='bold', va='center')

ax1.text(peak_hour + 0.3, weekend_hourly[peak_hour],
         f'{weekend_hourly[peak_hour]:.1f}',
         fontsize=16, fontweight='bold', va='center')

# Title shows the key insight
peak_diff = ((weekend_hourly[peak_hour] - weekday_hourly[peak_hour]) / weekday_hourly[peak_hour]) * 100

ax1.set_xlabel('Hour of Day', fontsize=18, fontweight='bold')
ax1.set_ylabel('Transactions per Day (avg)', fontsize=18, fontweight='bold')
ax1.set_title(f'Both Peak at 11 AM - Weekend +{peak_diff:.0f}% Busier at Peak',
              fontsize=18, fontweight='bold', pad=15)
ax1.legend(fontsize=16, loc='upper right', frameon=True, shadow=True)
ax1.grid(True, alpha=0.4, linewidth=1)
ax1.set_xlim([7, 20])
ax1.set_xticks(range(8, 21, 2))
ax1.tick_params(labelsize=14)

# ----------------------------------------------------------------------------
# Panel 2: Morning Transaction Comparison - SIMPLE BAR
# ----------------------------------------------------------------------------

categories = ['Weekday\nMorning', 'Weekend\nMorning']
values = [weekday_morning_avg, weekend_morning_avg]
colors = ['#3498db', '#e74c3c']

bars = ax2.bar(categories, values, color=colors, alpha=0.85,
               edgecolor='black', linewidth=2, width=0.5)

# Value labels on bars
for bar, val in zip(bars, values):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{val:.1f}', ha='center', va='bottom',
             fontsize=18, fontweight='bold')

# Percentage difference
morning_diff = ((weekend_morning_avg - weekday_morning_avg) / weekday_morning_avg) * 100
ax2.text(0.5, max(values) * 0.85, f'+{morning_diff:.1f}%',
         fontsize=28, fontweight='bold', color='darkgreen',
         ha='center', bbox=dict(boxstyle='round,pad=0.8',
                                facecolor='lightgreen',
                                edgecolor='darkgreen', linewidth=2))

ax2.set_ylabel('Transactions per Day (6 AM - 12 PM)', fontsize=18, fontweight='bold')
ax2.set_title('Weekend Morning Boom', fontsize=18, fontweight='bold', pad=15)
ax2.set_ylim([0, max(values) * 1.15])
ax2.grid(axis='y', alpha=0.4, linewidth=1)
ax2.tick_params(labelsize=14)

plt.tight_layout()
plt.savefig('../visualizations/viz7_weekend_weekday_comprehensive.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Saved: viz7_weekend_weekday_comprehensive.png")
print("\nActual patterns shown:")
print(f"  - Both peak at {peak_hour}:00 AM (no time shift)")
print(f"  - Weekend peak +{peak_diff:.0f}% busier")
print(f"  - Weekend morning +{morning_diff:.1f}% more transactions")
print(f"  - Basket size: {weekday_basket_avg:.2f} → {weekend_basket_avg:.2f} (+{((weekend_basket_avg-weekday_basket_avg)/weekday_basket_avg*100):.1f}%)")
plt.close()
