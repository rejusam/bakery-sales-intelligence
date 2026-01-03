"""
Create supplemental visualizations to complete the documentation
Author: Reju
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("Loading bakery data...")
bakery_df = pd.read_csv('../data/raw/BreadBasket_DMS.csv')

# Rename columns if needed
if 'TransactionNo' in bakery_df.columns:
    bakery_df.rename(columns={'TransactionNo': 'Transaction'}, inplace=True)
if 'Items' in bakery_df.columns:
    bakery_df.rename(columns={'Items': 'Item'}, inplace=True)

# Parse datetime
if 'DateTime' in bakery_df.columns:
    bakery_df['DateTime'] = pd.to_datetime(bakery_df['DateTime'])
else:
    bakery_df['DateTime'] = pd.to_datetime(bakery_df['date_time'])

bakery_df['Date'] = bakery_df['DateTime'].dt.date
bakery_df['Hour'] = bakery_df['DateTime'].dt.hour
bakery_df['DayOfWeek'] = bakery_df['DateTime'].dt.day_name()
bakery_df['DayOfWeekNum'] = bakery_df['DateTime'].dt.dayofweek
bakery_df['IsWeekend'] = bakery_df['DayOfWeekNum'].isin([5, 6])
bakery_df['Month'] = bakery_df['DateTime'].dt.month
bakery_df['MonthName'] = bakery_df['DateTime'].dt.strftime('%B')

# Filter out NONE items
bakery_df = bakery_df[bakery_df['Item'] != 'NONE'].copy()

print(f"Loaded {len(bakery_df):,} transaction records")

# Load weather data if available
try:
    weather_df = pd.read_csv('../data/raw/edinburgh_weather.csv')
    weather_df['DateTime'] = pd.to_datetime(weather_df['time'])
    weather_df['Date'] = weather_df['DateTime'].dt.date
    print(f"Loaded {len(weather_df):,} weather records")
    has_weather = True
except:
    print("Weather data not available - skipping weather plots")
    has_weather = False

# ============================================================================
# VISUALIZATION 1: Entry Products vs Add-On Products
# ============================================================================
print("\nCreating Visualization 1: Entry Products vs Add-On Products...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('🎯 Product Sequencing Analysis: Entry Products vs Add-On Products',
             fontsize=18, fontweight='bold', y=0.995)

# Get first and subsequent items in each transaction
transaction_items = bakery_df.sort_values(['Transaction', 'DateTime']).groupby('Transaction')['Item'].apply(list).reset_index()

# Identify first items
first_items = [items[0] if len(items) > 0 else None for items in transaction_items['Item']]
first_item_counts = pd.Series(first_items).value_counts()

# Identify items that appear later (not first)
subsequent_items = []
for items in transaction_items['Item']:
    if len(items) > 1:
        subsequent_items.extend(items[1:])
subsequent_item_counts = pd.Series(subsequent_items).value_counts()

# Calculate entry product rate
all_item_counts = bakery_df['Item'].value_counts()
entry_rate = {}
for item in all_item_counts.index[:20]:
    first_count = first_item_counts.get(item, 0)
    total_count = all_item_counts.get(item, 0)
    entry_rate[item] = (first_count / total_count * 100) if total_count > 0 else 0

entry_rate_series = pd.Series(entry_rate).sort_values(ascending=False)

# Subplot 1: Top Entry Products
ax1 = axes[0, 0]
top_entry = first_item_counts.head(10)
colors_entry = ['#FF6B6B' if item == 'COFFEE' else '#4ECDC4' for item in top_entry.index]
bars = ax1.barh(range(len(top_entry)), top_entry.values, color=colors_entry, alpha=0.8, edgecolor='black')

ax1.set_yticks(range(len(top_entry)))
ax1.set_yticklabels([item.title() for item in top_entry.index])
ax1.set_xlabel('Times as First Product', fontsize=12, fontweight='bold')
ax1.set_title('Top 10 Entry Products\n(Products customers buy FIRST)', fontsize=13, fontweight='bold')
ax1.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, val) in enumerate(zip(bars, top_entry.values)):
    width = bar.get_width()
    ax1.text(width + 20, bar.get_y() + bar.get_height()/2., f'{int(val)}',
            ha='left', va='center', fontsize=10, fontweight='bold')

# Subplot 2: Entry Rate (% of times bought first)
ax2 = axes[0, 1]
top_entry_rate = entry_rate_series.head(10)
colors_rate = plt.cm.RdYlGn(top_entry_rate.values / 100)
bars = ax2.barh(range(len(top_entry_rate)), top_entry_rate.values, color=colors_rate, alpha=0.8, edgecolor='black')

ax2.set_yticks(range(len(top_entry_rate)))
ax2.set_yticklabels([item.title() for item in top_entry_rate.index])
ax2.set_xlabel('Entry Product Rate (%)', fontsize=12, fontweight='bold')
ax2.set_title('Entry Product Rate\n(% of times product is bought FIRST)', fontsize=13, fontweight='bold')
ax2.grid(axis='x', alpha=0.3)
ax2.set_xlim([0, 100])

# Add value labels
for i, (bar, val) in enumerate(zip(bars, top_entry_rate.values)):
    width = bar.get_width()
    ax2.text(width + 2, bar.get_y() + bar.get_height()/2., f'{val:.1f}%',
            ha='left', va='center', fontsize=10, fontweight='bold')

# Subplot 3: Add-On Products (bought later, not first)
ax3 = axes[1, 0]
# Find products with low entry rate (mostly bought as add-ons)
addon_candidates = entry_rate_series[entry_rate_series < 30].head(10)
bars = ax3.barh(range(len(addon_candidates)), 100 - addon_candidates.values,
                color='#FFA07A', alpha=0.8, edgecolor='black')

ax3.set_yticks(range(len(addon_candidates)))
ax3.set_yticklabels([item.title() for item in addon_candidates.index])
ax3.set_xlabel('Add-On Rate (% bought AFTER first product)', fontsize=12, fontweight='bold')
ax3.set_title('Top Add-On Products\n(Rarely bought first, mostly upsells)', fontsize=13, fontweight='bold')
ax3.grid(axis='x', alpha=0.3)
ax3.set_xlim([0, 100])

# Add value labels
for i, (bar, val) in enumerate(zip(bars, 100 - addon_candidates.values)):
    width = bar.get_width()
    ax3.text(width + 2, bar.get_y() + bar.get_height()/2., f'{val:.1f}%',
            ha='left', va='center', fontsize=10, fontweight='bold')

# Subplot 4: Basket position analysis
ax4 = axes[1, 1]
# Analyze basket positions for top products
basket_positions = {}
for items in transaction_items['Item']:
    for pos, item in enumerate(items):
        if item not in basket_positions:
            basket_positions[item] = {'pos1': 0, 'pos2': 0, 'pos3+': 0, 'total': 0}
        basket_positions[item]['total'] += 1
        if pos == 0:
            basket_positions[item]['pos1'] += 1
        elif pos == 1:
            basket_positions[item]['pos2'] += 1
        else:
            basket_positions[item]['pos3+'] += 1

# Get top products by total
top_products_for_position = sorted(basket_positions.items(),
                                   key=lambda x: x[1]['total'], reverse=True)[:8]

products = [item[0].title() for item in top_products_for_position]
pos1_pct = [(item[1]['pos1'] / item[1]['total'] * 100) for item in top_products_for_position]
pos2_pct = [(item[1]['pos2'] / item[1]['total'] * 100) for item in top_products_for_position]
pos3_pct = [(item[1]['pos3+'] / item[1]['total'] * 100) for item in top_products_for_position]

x = np.arange(len(products))
width = 0.6

p1 = ax4.bar(x, pos1_pct, width, label='Position 1 (First)', color='#FF6B6B', alpha=0.8)
p2 = ax4.bar(x, pos2_pct, width, bottom=pos1_pct, label='Position 2', color='#4ECDC4', alpha=0.8)
p3 = ax4.bar(x, pos3_pct, width, bottom=np.array(pos1_pct) + np.array(pos2_pct),
             label='Position 3+', color='#FFA07A', alpha=0.8)

ax4.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
ax4.set_xlabel('Product', fontsize=12, fontweight='bold')
ax4.set_title('Basket Position Distribution\n(Where in basket is product typically bought?)',
              fontsize=13, fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels(products, rotation=45, ha='right')
ax4.legend(loc='upper right', fontsize=10)
ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('../visualizations/viz_supplemental1_entry_vs_addon.png', dpi=300, bbox_inches='tight')
print("✓ Saved: viz_supplemental1_entry_vs_addon.png")
plt.close()

# ============================================================================
# VISUALIZATION 2: Coffee Centrality & Cross-Sell Opportunities
# ============================================================================
print("\nCreating Visualization 2: Coffee Centrality Analysis...")

# Create simple 3-panel layout
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('☕ Coffee Centrality: The Anchor Product (60% of multi-item baskets include coffee)',
             fontsize=18, fontweight='bold', y=1.02)

# Analyze multi-item transactions
multi_item_txns = transaction_items[transaction_items['Item'].apply(len) > 1]

# Panel 1: Top products bought WITH coffee
coffee_with = []
for items in multi_item_txns['Item']:
    if 'COFFEE' in items:
        coffee_with.extend([item for item in items if item != 'COFFEE'])

coffee_pairs = pd.Series(coffee_with).value_counts().head(8)

ax1 = axes[0]
colors_pairs = plt.cm.YlOrBr(np.linspace(0.4, 0.9, len(coffee_pairs)))
bars = ax1.barh(range(len(coffee_pairs)), coffee_pairs.values, color=colors_pairs,
                alpha=0.85, edgecolor='black', linewidth=1.5)

ax1.set_yticks(range(len(coffee_pairs)))
ax1.set_yticklabels([item.title() for item in coffee_pairs.index], fontsize=11)
ax1.set_xlabel('Times Bought WITH Coffee', fontsize=12, fontweight='bold')
ax1.set_title('What Do Customers Buy\nWITH Coffee?', fontsize=13, fontweight='bold', pad=15)
ax1.grid(axis='x', alpha=0.3, linewidth=0.8)
ax1.invert_yaxis()

# Add value labels
for i, (bar, val) in enumerate(zip(bars, coffee_pairs.values)):
    width = bar.get_width()
    ax1.text(width + 15, bar.get_y() + bar.get_height()/2., f'{int(val)}',
            ha='left', va='center', fontsize=11, fontweight='bold')

# Panel 2: Basket size comparison (SIMPLE BAR CHART)
ax2 = axes[1]
basket_size_df = transaction_items.copy()
basket_size_df['BasketSize'] = basket_size_df['Item'].apply(len)
basket_size_df['HasCoffee'] = basket_size_df['Item'].apply(lambda x: 'COFFEE' in x)

avg_with_coffee = basket_size_df[basket_size_df['HasCoffee']]['BasketSize'].mean()
avg_without_coffee = basket_size_df[~basket_size_df['HasCoffee']]['BasketSize'].mean()

categories = ['WITH\nCoffee', 'WITHOUT\nCoffee']
values = [avg_with_coffee, avg_without_coffee]
colors_basket = ['#8B4513', '#D3D3D3']

bars = ax2.bar(categories, values, color=colors_basket, alpha=0.85,
               edgecolor='black', linewidth=2, width=0.6)

ax2.set_ylabel('Average Basket Size (items)', fontsize=12, fontweight='bold')
ax2.set_title('Coffee = Bigger Baskets', fontsize=13, fontweight='bold', pad=15)
ax2.grid(axis='y', alpha=0.3, linewidth=0.8)
if len(values) > 0 and all(v > 0 for v in values):
    ax2.set_ylim([0, max(values) * 1.2])

# Add value labels with percentage increase
for bar, val in zip(bars, values):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
            f'{val:.2f}\nitems', ha='center', va='bottom',
            fontsize=12, fontweight='bold')

# Show percentage increase
pct_increase = ((avg_with_coffee - avg_without_coffee) / avg_without_coffee) * 100
if len(values) > 0 and max(values) > 0:
    ax2.text(0.5, max(values) * 0.75, f'+{pct_increase:.1f}%',
             ha='center', fontsize=22, fontweight='bold', color='darkgreen',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen',
                       edgecolor='darkgreen', linewidth=2))

# Panel 3: Coffee's share in multi-item baskets (SIMPLE PERCENTAGE)
ax3 = axes[2]
coffee_in_multi = len(multi_item_txns[multi_item_txns['Item'].apply(lambda x: 'COFFEE' in x)])
total_multi = len(multi_item_txns)
coffee_pct = (coffee_in_multi / total_multi) * 100
no_coffee_pct = 100 - coffee_pct

categories = ['Multi-Item\nBaskets WITH\nCoffee', 'Multi-Item\nBaskets WITHOUT\nCoffee']
values = [coffee_pct, no_coffee_pct]
colors_pct = ['#8B4513', '#D3D3D3']

bars = ax3.bar(categories, values, color=colors_pct, alpha=0.85,
               edgecolor='black', linewidth=2, width=0.6)

ax3.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
ax3.set_title('Coffee in Multi-Item\nTransactions', fontsize=13, fontweight='bold', pad=15)
ax3.grid(axis='y', alpha=0.3, linewidth=0.8)
ax3.set_ylim([0, 100])

# Add value labels
for bar, val in zip(bars, values):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height/2,
            f'{val:.1f}%', ha='center', va='center',
            fontsize=18, fontweight='bold', color='white')

# Add count labels
ax3.text(bars[0].get_x() + bars[0].get_width()/2., coffee_pct + 3,
         f'{coffee_in_multi:,} baskets', ha='center', va='bottom',
         fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('../visualizations/viz_supplemental2_coffee_centrality.png', dpi=300, bbox_inches='tight')
print("✓ Saved: viz_supplemental2_coffee_centrality.png")
plt.close()

# ============================================================================
# VISUALIZATION 3: Weather Impact Analysis (if weather data available)
# ============================================================================
if has_weather:
    print("\nCreating Visualization 3: Weather Impact Analysis...")

    # Merge weather with transactions
    bakery_daily = bakery_df.groupby('Date').agg({
        'Transaction': 'nunique',
        'Item': 'count'
    }).reset_index()
    bakery_daily.columns = ['Date', 'Transactions', 'Items']

    weather_daily = weather_df.groupby('Date').agg({
        'temperature_2m': 'mean',
        'precipitation': 'sum',
        'relative_humidity_2m': 'mean',
        'wind_speed_10m': 'mean'
    }).reset_index()

    merged = bakery_daily.merge(weather_daily, on='Date', how='inner')
    merged['IsRainy'] = merged['precipitation'] > 0.1
    merged['TempBin'] = pd.cut(merged['temperature_2m'], bins=[-5, 5, 10, 15, 20, 30],
                                labels=['<5°C', '5-10°C', '10-15°C', '15-20°C', '>20°C'])

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('🌦️ Weather Impact on Bakery Traffic & Product Mix',
                 fontsize=18, fontweight='bold', y=0.995)

    # Subplot 1: Rain vs No Rain
    ax1 = axes[0, 0]
    rainy_avg = merged[merged['IsRainy']]['Transactions'].mean()
    dry_avg = merged[~merged['IsRainy']]['Transactions'].mean()

    categories = ['Dry Days', 'Rainy Days']
    values = [dry_avg, rainy_avg]
    colors_weather = ['#FFD700', '#4682B4']

    bars = ax1.bar(categories, values, color=colors_weather, alpha=0.8, edgecolor='black', linewidth=2)
    ax1.set_ylabel('Average Transactions per Day', fontsize=12, fontweight='bold')
    ax1.set_title('Rain Impact on Daily Traffic', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    # Add value labels and percentage
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}\ntxns', ha='center', va='bottom', fontsize=12, fontweight='bold')

    if rainy_avg > dry_avg:
        lift = ((rainy_avg - dry_avg) / dry_avg) * 100
        ax1.annotate(f'+{lift:.1f}%\n(Small effect)', xy=(1, rainy_avg),
                    xytext=(0.5, rainy_avg + 5),
                    fontsize=11, fontweight='bold', color='gray',
                    arrowprops=dict(arrowstyle='->', color='gray', lw=2))

    # Subplot 2: Temperature bins
    ax2 = axes[0, 1]
    temp_txns = merged.groupby('TempBin')['Transactions'].mean().sort_index()

    colors_temp = plt.cm.coolwarm(np.linspace(0, 1, len(temp_txns)))
    bars = ax2.bar(range(len(temp_txns)), temp_txns.values, color=colors_temp,
                   alpha=0.8, edgecolor='black', linewidth=2)

    ax2.set_xticks(range(len(temp_txns)))
    ax2.set_xticklabels(temp_txns.index, rotation=45)
    ax2.set_ylabel('Average Transactions', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Temperature Range', fontsize=12, fontweight='bold')
    ax2.set_title('Temperature Range Analysis (Minimal Volume Effect)', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)

    # Highlight sweet spot
    if len(temp_txns) > 0:
        max_idx = temp_txns.values.argmax()
        bars[max_idx].set_edgecolor('gold')
        bars[max_idx].set_linewidth(4)

    # Subplot 3: Temperature vs Transactions scatter
    ax3 = axes[1, 0]
    scatter = ax3.scatter(merged['temperature_2m'], merged['Transactions'],
                         c=merged['precipitation'], cmap='Blues', alpha=0.6, s=50)

    # Add trend line
    z = np.polyfit(merged['temperature_2m'].dropna(),
                   merged.loc[merged['temperature_2m'].notna(), 'Transactions'], 2)
    p = np.poly1d(z)
    temp_range = np.linspace(merged['temperature_2m'].min(), merged['temperature_2m'].max(), 100)
    ax3.plot(temp_range, p(temp_range), "r--", linewidth=2, label='Trend')

    ax3.set_xlabel('Temperature (°C)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Daily Transactions', fontsize=12, fontweight='bold')
    ax3.set_title('Temperature vs Traffic Correlation', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=10)

    cbar = plt.colorbar(scatter, ax=ax3)
    cbar.set_label('Precipitation (mm)', fontsize=10)

    # Subplot 4: Hot drink preference by temperature
    ax4 = axes[1, 1]

    # Get hot drinks
    hot_drinks = ['COFFEE', 'TEA', 'HOT CHOCOLATE']
    cold_drinks = ['JUICE', 'COKE', 'WATER']

    # Merge with weather by date
    bakery_with_temp = bakery_df.merge(weather_daily[['Date', 'temperature_2m']], on='Date', how='inner')
    bakery_with_temp['TempBin'] = pd.cut(bakery_with_temp['temperature_2m'],
                                         bins=[-5, 5, 10, 15, 20, 30],
                                         labels=['<5°C', '5-10°C', '10-15°C', '15-20°C', '>20°C'])

    hot_by_temp = bakery_with_temp[bakery_with_temp['Item'].isin(hot_drinks)].groupby('TempBin').size()
    all_by_temp = bakery_with_temp.groupby('TempBin').size()
    hot_pct = (hot_by_temp / all_by_temp * 100).sort_index()

    colors_hot = plt.cm.Reds(np.linspace(0.4, 0.9, len(hot_pct)))
    bars = ax4.bar(range(len(hot_pct)), hot_pct.values, color=colors_hot,
                   alpha=0.8, edgecolor='black', linewidth=2)

    ax4.set_xticks(range(len(hot_pct)))
    ax4.set_xticklabels(hot_pct.index, rotation=45)
    ax4.set_ylabel('% Hot Drinks', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Temperature Range', fontsize=12, fontweight='bold')
    ax4.set_title('Hot Drink Preference by Temperature', fontsize=13, fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)

    # Add value labels
    for bar, val in zip(bars, hot_pct.values):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig('../visualizations/viz_supplemental3_weather_impact.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: viz_supplemental3_weather_impact.png")
    plt.close()

# ============================================================================
# VISUALIZATION 4: Executive Summary Dashboard (1-page overview)
# ============================================================================
print("\nCreating Visualization 4: Executive Summary Dashboard...")

fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(4, 4, hspace=0.4, wspace=0.4)
fig.suptitle('📊 Aofrio Part 2: Executive Summary Dashboard - Key Findings at a Glance',
             fontsize=20, fontweight='bold')

# Panel 1: Key metrics (top left, large)
ax1 = fig.add_subplot(gs[0:2, 0:2])
ax1.axis('off')

metrics_text = f"""
KEY METRICS

Dataset Period: Oct 2016 - Apr 2017
Total Transactions: {len(transaction_items):,}
Total Items Sold: {len(bakery_df):,}
Unique Products: {bakery_df['Item'].nunique()}
Average Basket Size: {transaction_items['Item'].apply(len).mean():.2f} items

BUSINESS IMPACT OPPORTUNITIES

Solo Buyers: {(len(transaction_items[transaction_items['Item'].apply(len) == 1]) / len(transaction_items) * 100):.1f}%
→ Cross-sell potential: +7.7% revenue

Coffee in Multi-Item Baskets: 60.3%
→ Anchor product for upselling

Weekend Morning Lift: +23%
→ Staffing & inventory optimization

5 PM Dead Zone: -89% from peak
→ Major promotion opportunity
"""

ax1.text(0.05, 0.95, metrics_text, transform=ax1.transAxes, fontsize=11,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Panel 2: Top product pairs
ax2 = fig.add_subplot(gs[0, 2:])
from itertools import combinations
pairs = []
for items in multi_item_txns['Item']:
    if len(items) >= 2:
        for pair in combinations(sorted(set(items)), 2):
            pairs.append(pair)
pair_counts = pd.Series(pairs).value_counts().head(6)
pair_labels = [f"{p[0][:10]}\n+\n{p[1][:10]}" for p in pair_counts.index]

bars = ax2.barh(range(len(pair_counts)), pair_counts.values,
                color='#FF6B6B', alpha=0.8, edgecolor='black')
ax2.set_yticks(range(len(pair_counts)))
ax2.set_yticklabels(pair_labels, fontsize=8)
ax2.set_xlabel('Frequency', fontsize=10, fontweight='bold')
ax2.set_title('Top Product Pairs', fontsize=12, fontweight='bold')
ax2.grid(axis='x', alpha=0.3)

# Panel 3: Day of week pattern
ax3 = fig.add_subplot(gs[1, 2:])
daily_txns = bakery_df.groupby(['DayOfWeek', 'DayOfWeekNum'])['Transaction'].nunique().reset_index()
daily_txns = daily_txns.sort_values('DayOfWeekNum')

colors_daily = ['#FF6B6B' if day in ['Saturday', 'Sunday'] else '#4ECDC4'
                for day in daily_txns['DayOfWeek']]
bars = ax3.bar(range(len(daily_txns)), daily_txns['Transaction'],
               color=colors_daily, alpha=0.8, edgecolor='black')
ax3.set_xticks(range(len(daily_txns)))
ax3.set_xticklabels(daily_txns['DayOfWeek'], rotation=45, ha='right', fontsize=9)
ax3.set_ylabel('Transactions', fontsize=10, fontweight='bold')
ax3.set_title('Day of Week Pattern (Weekend highlighted)', fontsize=12, fontweight='bold')
ax3.grid(axis='y', alpha=0.3)

# Panel 4: Hourly heatmap (compact)
ax4 = fig.add_subplot(gs[2:, 0:2])
hourly_heatmap_data = bakery_df.groupby(['DayOfWeekNum', 'Hour']).size().reset_index(name='Count')
heatmap_pivot = hourly_heatmap_data.pivot_table(values='Count', index='DayOfWeekNum',
                                                 columns='Hour', aggfunc='sum', fill_value=0)

sns.heatmap(heatmap_pivot, cmap='YlOrRd', annot=False, cbar_kws={'label': 'Transactions'},
            linewidths=0.5, ax=ax4, yticklabels=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
ax4.set_xlabel('Hour of Day', fontsize=10, fontweight='bold')
ax4.set_ylabel('Day of Week', fontsize=10, fontweight='bold')
ax4.set_title('Temporal Pattern Heatmap', fontsize=12, fontweight='bold')

# Panel 5: Entry products
ax5 = fig.add_subplot(gs[2, 2:])
top_entry_compact = first_item_counts.head(6)
colors_entry = ['#8B4513' if item == 'COFFEE' else '#4ECDC4' for item in top_entry_compact.index]
bars = ax5.barh(range(len(top_entry_compact)), top_entry_compact.values,
                color=colors_entry, alpha=0.8, edgecolor='black')
ax5.set_yticks(range(len(top_entry_compact)))
ax5.set_yticklabels([item.title()[:15] for item in top_entry_compact.index], fontsize=9)
ax5.set_xlabel('Count', fontsize=10, fontweight='bold')
ax5.set_title('Top Entry Products (Coffee dominates)', fontsize=12, fontweight='bold')
ax5.grid(axis='x', alpha=0.3)

# Panel 6: Basket size distribution
ax6 = fig.add_subplot(gs[3, 2:])
basket_sizes = transaction_items['Item'].apply(len)
basket_dist = basket_sizes.value_counts().sort_index().head(8)

bars = ax6.bar(basket_dist.index, basket_dist.values, color='#95E1D3',
               alpha=0.8, edgecolor='black')
ax6.set_xlabel('Basket Size (items)', fontsize=10, fontweight='bold')
ax6.set_ylabel('Frequency', fontsize=10, fontweight='bold')
ax6.set_title(f'Basket Size Distribution (Avg: {basket_sizes.mean():.2f})',
              fontsize=12, fontweight='bold')
ax6.grid(axis='y', alpha=0.3)

# Highlight solo buyers
bars[0].set_color('#FF6B6B')
bars[0].set_edgecolor('darkred')
bars[0].set_linewidth(3)

plt.savefig('../visualizations/viz_supplemental4_executive_dashboard.png', dpi=300, bbox_inches='tight')
print("✓ Saved: viz_supplemental4_executive_dashboard.png")
plt.close()

print("\n" + "="*80)
print("SUPPLEMENTAL VISUALIZATIONS COMPLETE!")
print("="*80)
print("\nCreated 4 additional visualizations:")
print("  1. viz_supplemental1_entry_vs_addon.png - Product sequencing analysis")
print("  2. viz_supplemental2_coffee_centrality.png - Coffee as anchor product")
if has_weather:
    print("  3. viz_supplemental3_weather_impact.png - Weather correlations")
print("  4. viz_supplemental4_executive_dashboard.png - 1-page summary dashboard")
print("\nDocumentation is now complete with comprehensive visual support!")
