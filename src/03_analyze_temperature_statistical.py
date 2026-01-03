"""
Statistical analysis of temperature vs transactions
Find the actual sweet spot with proper statistical rigor
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')

print("Loading data...")
bakery_df = pd.read_csv('../data/raw/BreadBasket_DMS.csv')
if 'TransactionNo' in bakery_df.columns:
    bakery_df.rename(columns={'TransactionNo': 'Transaction'}, inplace=True)
if 'Items' in bakery_df.columns:
    bakery_df.rename(columns={'Items': 'Item'}, inplace=True)
if 'DateTime' in bakery_df.columns:
    bakery_df['DateTime'] = pd.to_datetime(bakery_df['DateTime'])

bakery_df['Date'] = bakery_df['DateTime'].dt.date
bakery_df['DayOfWeek'] = bakery_df['DateTime'].dt.dayofweek
bakery_df = bakery_df[bakery_df['Item'] != 'NONE'].copy()

# Load weather
weather_df = pd.read_csv('../data/raw/edinburgh_weather.csv')
weather_df['DateTime'] = pd.to_datetime(weather_df['timestamp'])
weather_df['Date'] = weather_df['DateTime'].dt.date

# Daily aggregates
bakery_daily = bakery_df.groupby('Date').agg({
    'Transaction': 'nunique',
    'Item': 'count',
    'DayOfWeek': 'first'
}).reset_index()
bakery_daily.columns = ['Date', 'Transactions', 'Items', 'DayOfWeek']

weather_daily = weather_df.groupby('Date')['temperature'].mean().reset_index()
weather_daily.columns = ['Date', 'AvgTemp']

# Merge
merged_df = bakery_daily.merge(weather_daily, on='Date', how='inner')
print(f"Merged data: {len(merged_df)} days")

print("\n" + "="*80)
print("STATISTICAL ANALYSIS: Temperature vs Transactions")
print("="*80)

# 1. Basic statistics
print("\nTemperature range:", merged_df['AvgTemp'].min(), "to", merged_df['AvgTemp'].max(), "°C")
print("Transaction range:", merged_df['Transactions'].min(), "to", merged_df['Transactions'].max())

# 2. Correlation
correlation = merged_df['AvgTemp'].corr(merged_df['Transactions'])
print(f"\nPearson correlation: {correlation:.3f}")

# 3. Fit quadratic curve to find optimal temperature
def quadratic(x, a, b, c):
    return a * x**2 + b * x + c

# Fit curve
params, _ = curve_fit(quadratic, merged_df['AvgTemp'], merged_df['Transactions'])
a, b, c = params

# Find optimal temperature (vertex of parabola)
optimal_temp = -b / (2 * a)
optimal_txns = quadratic(optimal_temp, a, b, c)

print(f"\nQUADRATIC FIT ANALYSIS:")
print(f"  Optimal temperature: {optimal_temp:.1f}°C")
print(f"  Expected transactions at optimal: {optimal_txns:.1f}")
print(f"  Equation: {a:.4f}x² + {b:.4f}x + {c:.4f}")

# 4. Bin analysis with proper sample sizes
temp_bins = [0, 5, 7, 9, 11, 13, 100]
bin_labels = ['0-5°C', '5-7°C', '7-9°C', '9-11°C', '11-13°C', '>13°C']
merged_df['TempBin'] = pd.cut(merged_df['AvgTemp'], bins=temp_bins, labels=bin_labels)

bin_stats = merged_df.groupby('TempBin', observed=True).agg({
    'Transactions': ['mean', 'std', 'count'],
    'AvgTemp': 'mean'
}).reset_index()
bin_stats.columns = ['TempBin', 'MeanTxns', 'StdTxns', 'Count', 'AvgTempInBin']

print("\nBINNED ANALYSIS (narrower bins):")
print("-" * 80)
for row in bin_stats.itertuples():
    if row.Count >= 3:  # Only show bins with sufficient data
        ci = 1.96 * row.StdTxns / np.sqrt(row.Count)  # 95% confidence interval
        print(f"{row.TempBin:10s} | Avg temp: {row.AvgTempInBin:5.1f}°C | "
              f"Txns: {row.MeanTxns:5.1f} ± {ci:4.1f} | N={row.Count:3d} days")

# 5. Find peak bin
valid_bins = bin_stats[bin_stats['Count'] >= 5]  # At least 5 days
if len(valid_bins) > 0:
    peak_bin = valid_bins.loc[valid_bins['MeanTxns'].idxmax()]
    print(f"\nPEAK BIN (with ≥5 days): {peak_bin['TempBin']}")
    print(f"  Average temperature in bin: {peak_bin['AvgTempInBin']:.1f}°C")
    print(f"  Average transactions: {peak_bin['MeanTxns']:.1f}")
    print(f"  Sample size: {peak_bin['Count']:.0f} days")

# 6. Check for confounding by day of week
print("\n" + "="*80)
print("CHECKING FOR CONFOUNDING VARIABLES")
print("="*80)

# Average transactions by day of week
dow_stats = merged_df.groupby('DayOfWeek')['Transactions'].agg(['mean', 'count'])
print("\nTransactions by Day of Week:")
days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
for i in range(7):
    if i in dow_stats.index:
        print(f"  {days[i]}: {dow_stats.loc[i, 'mean']:.1f} avg txns ({dow_stats.loc[i, 'count']:.0f} days)")

# 7. Create detailed visualization
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Statistical Analysis: Temperature Sweet Spot', fontsize=16, fontweight='bold')

# Plot 1: Scatter with quadratic fit
ax1 = axes[0, 0]
ax1.scatter(merged_df['AvgTemp'], merged_df['Transactions'], alpha=0.5, s=50)
temp_range = np.linspace(merged_df['AvgTemp'].min(), merged_df['AvgTemp'].max(), 100)
ax1.plot(temp_range, quadratic(temp_range, a, b, c), 'r-', linewidth=2, label='Quadratic fit')
ax1.axvline(optimal_temp, color='green', linestyle='--', linewidth=2, label=f'Optimal: {optimal_temp:.1f}°C')
ax1.set_xlabel('Average Temperature (°C)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Daily Transactions', fontsize=12, fontweight='bold')
ax1.set_title('Temperature vs Transactions (Quadratic Fit)', fontsize=13, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Binned averages with error bars
ax2 = axes[0, 1]
valid_for_plot = bin_stats[bin_stats['Count'] >= 3]
x_pos = range(len(valid_for_plot))
ax2.bar(x_pos, valid_for_plot['MeanTxns'],
        yerr=1.96 * valid_for_plot['StdTxns'] / np.sqrt(valid_for_plot['Count']),
        capsize=5, alpha=0.7, edgecolor='black')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(valid_for_plot['TempBin'], rotation=45)
ax2.set_ylabel('Average Daily Transactions', fontsize=12, fontweight='bold')
ax2.set_title('Average Transactions by Temperature Range\n(with 95% confidence intervals)',
              fontsize=13, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

# Add sample sizes
for i, (idx, row) in enumerate(valid_for_plot.iterrows()):
    ax2.text(i, 5, f'n={row["Count"]:.0f}', ha='center', fontsize=9)

# Plot 3: Rolling average
ax3 = axes[1, 0]
sorted_df = merged_df.sort_values('AvgTemp')
window = 15  # 15-day rolling window
sorted_df['Rolling'] = sorted_df['Transactions'].rolling(window=window, center=True).mean()
ax3.scatter(sorted_df['AvgTemp'], sorted_df['Transactions'], alpha=0.3, s=30, label='Daily data')
ax3.plot(sorted_df['AvgTemp'], sorted_df['Rolling'], 'r-', linewidth=2,
         label=f'{window}-day rolling average')
ax3.axvline(optimal_temp, color='green', linestyle='--', linewidth=2,
            label=f'Optimal: {optimal_temp:.1f}°C')
ax3.set_xlabel('Average Temperature (°C)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Daily Transactions', fontsize=12, fontweight='bold')
ax3.set_title('Rolling Average Analysis', fontsize=13, fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Plot 4: Distribution of temperatures
ax4 = axes[1, 1]
ax4.hist(merged_df['AvgTemp'], bins=20, alpha=0.7, edgecolor='black')
ax4.axvline(optimal_temp, color='green', linestyle='--', linewidth=2,
            label=f'Optimal: {optimal_temp:.1f}°C')
ax4.set_xlabel('Average Temperature (°C)', fontsize=12, fontweight='bold')
ax4.set_ylabel('Number of Days', fontsize=12, fontweight='bold')
ax4.set_title('Temperature Distribution in Dataset', fontsize=13, fontweight='bold')
ax4.legend()
ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('../visualizations/viz_temperature_statistical_analysis.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved: viz_temperature_statistical_analysis.png")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print(f"Based on quadratic regression analysis:")
print(f"  Optimal temperature: {optimal_temp:.1f}°C")
print(f"  Expected transactions: {optimal_txns:.1f} per day")
print(f"\nThis is based on {len(merged_df)} days of data.")
print(f"Correlation coefficient: {correlation:.3f}")
print("="*80)

plt.close()
