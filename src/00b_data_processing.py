"""
Bakery Analysis 
Market Basket Analysis and Temporal Patterns for Bakery Outlets
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("BAKERY ANALYSIS - MARKET BASKET & TEMPORAL PATTERNS")
print("="*80)
print()

# ============================================================================
# 1. LOAD AND PREPARE DATA
# ============================================================================

print("Step 1: Loading Bakery Sales Data")
print("-"*80)

try:
    # Load bakery data
    bakery_df = pd.read_csv('../data/raw/BreadBasket_DMS.csv')
    print(f"✓ Loaded bakery data: {len(bakery_df):,} records")
    print(f"  Columns: {list(bakery_df.columns)}")

    # Display first few records
    print("\nSample data:")
    print(bakery_df.head())

except FileNotFoundError:
    print("✗ Error: ../data/raw/BreadBasket_DMS.csv not found")
    print("\nPlease download the dataset:")
    print("1. Visit: https://www.kaggle.com/datasets/akashdeepkuila/bakery")
    print("2. Download and extract to ../data/raw/ directory")
    print("3. Run this script again")
    exit(1)

# Load weather data
try:
    weather_df = pd.read_csv('../data/raw/edinburgh_weather.csv')
    weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
    print(f"\n✓ Loaded weather data: {len(weather_df):,} hourly records")
except:
    print("\n⚠ Weather data not found, continuing without weather analysis")
    weather_df = None

print()

# ============================================================================
# 2. DATA PREPARATION
# ============================================================================

print("Step 2: Data Preparation and Feature Engineering")
print("-"*80)

# Rename columns to standard names
if 'TransactionNo' in bakery_df.columns:
    bakery_df.rename(columns={'TransactionNo': 'Transaction'}, inplace=True)
if 'Items' in bakery_df.columns:
    bakery_df.rename(columns={'Items': 'Item'}, inplace=True)

# Parse datetime
if 'DateTime' in bakery_df.columns:
    bakery_df['DateTime'] = pd.to_datetime(bakery_df['DateTime'])
elif 'Date' in bakery_df.columns and 'Time' in bakery_df.columns:
    bakery_df['DateTime'] = pd.to_datetime(bakery_df['Date'] + ' ' + bakery_df['Time'])
else:
    print("✗ Error: No datetime column found")
    exit(1)

# Extract temporal features
bakery_df['Date'] = bakery_df['DateTime'].dt.date
bakery_df['Year'] = bakery_df['DateTime'].dt.year
bakery_df['Month'] = bakery_df['DateTime'].dt.month
bakery_df['MonthName'] = bakery_df['DateTime'].dt.month_name()
bakery_df['DayOfWeek'] = bakery_df['DateTime'].dt.dayofweek
bakery_df['DayName'] = bakery_df['DateTime'].dt.day_name()
bakery_df['Hour'] = bakery_df['DateTime'].dt.hour
bakery_df['Minute'] = bakery_df['DateTime'].dt.minute
bakery_df['TimeOfDay'] = bakery_df['Hour'] + bakery_df['Minute']/60
bakery_df['IsWeekend'] = bakery_df['DayOfWeek'].isin([5, 6])

# Create 15-minute intervals
bakery_df['QuarterHour'] = (bakery_df['Hour'] * 4 + bakery_df['Minute'] // 15) / 4

# Daypart classification
def classify_daypart(hour):
    if 5 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 17:
        return 'Afternoon'
    elif 17 <= hour < 21:
        return 'Evening'
    else:
        return 'Night'

bakery_df['DayPart'] = bakery_df['Hour'].apply(classify_daypart)

# Clean item names
bakery_df['Item'] = bakery_df['Item'].str.strip().str.upper()

# Remove "NONE" and empty items
bakery_df = bakery_df[bakery_df['Item'] != 'NONE']
bakery_df = bakery_df[bakery_df['Item'].notna()]

print(f"Clean records: {len(bakery_df):,}")
print(f"Unique transactions: {bakery_df['Transaction'].nunique():,}")
print(f"Unique items: {bakery_df['Item'].nunique():,}")
print(f"Date range: {bakery_df['DateTime'].min()} to {bakery_df['DateTime'].max()}")

print()

# ============================================================================
# 3. TEMPORAL ANALYSIS - MINUTE-LEVEL GRANULARITY
# ============================================================================

print("="*80)
print("ANALYSIS 1: TEMPORAL PATTERNS (MINUTE-LEVEL GRANULARITY)")
print("="*80)

# Day of week analysis
print("\nTransactions by Day of Week:")
print("-"*60)

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_analysis = bakery_df.groupby(['DayName', 'Transaction']).size().reset_index(name='items_per_trans')
dow_counts = dow_analysis.groupby('DayName').agg({
    'Transaction': 'count',
    'items_per_trans': 'mean'
}).reset_index()
dow_counts.columns = ['DayName', 'NumTransactions', 'AvgItemsPerTransaction']

dow_counts['DayName'] = pd.Categorical(dow_counts['DayName'], categories=day_order, ordered=True)
dow_counts = dow_counts.sort_values('DayName')

for _, row in dow_counts.iterrows():
    print(f"{row['DayName']:12s}: {row['NumTransactions']:,} transactions, {row['AvgItemsPerTransaction']:.2f} items/transaction")

# Weekend effect
weekend_trans = dow_counts[dow_counts['DayName'].isin(['Saturday', 'Sunday'])]['NumTransactions'].sum()
weekday_trans = dow_counts[~dow_counts['DayName'].isin(['Saturday', 'Sunday'])]['NumTransactions'].sum()
weekend_avg = weekend_trans / 2
weekday_avg = weekday_trans / 5
weekend_lift = ((weekend_avg / weekday_avg) - 1) * 100

print(f"\n✓ Weekend Effect:")
print(f"  Weekend daily avg: {weekend_avg:,.0f} transactions")
print(f"  Weekday daily avg: {weekday_avg:,.0f} transactions")
print(f"  Weekend lift: {weekend_lift:+.1f}%")

# Hourly patterns with 15-minute granularity
print("\n\nHourly Patterns (15-minute intervals):")
print("-"*60)

quarter_analysis = bakery_df.groupby('QuarterHour')['Transaction'].nunique().reset_index()
quarter_analysis.columns = ['QuarterHour', 'NumTransactions']

# Find peak quarter hour
peak_quarter = quarter_analysis.loc[quarter_analysis['NumTransactions'].idxmax()]
peak_hour = int(peak_quarter['QuarterHour'])
peak_min = int((peak_quarter['QuarterHour'] % 1) * 60)

print(f"Peak time: {peak_hour:02d}:{peak_min:02d} ({peak_quarter['NumTransactions']:.0f} transactions)")

# Show top 10 busiest 15-min windows
print("\nTop 10 Busiest 15-Minute Windows:")
top_quarters = quarter_analysis.sort_values('NumTransactions', ascending=False).head(10)
for _, row in top_quarters.iterrows():
    hour = int(row['QuarterHour'])
    minute = int((row['QuarterHour'] % 1) * 60)
    print(f"  {hour:02d}:{minute:02d} - {row['NumTransactions']:4.0f} transactions")

# Daypart analysis
print("\n\nDaypart Performance:")
print("-"*60)

daypart_analysis = bakery_df.groupby('DayPart')['Transaction'].nunique().reset_index()
daypart_analysis.columns = ['DayPart', 'NumTransactions']
daypart_order = ['Morning', 'Afternoon', 'Evening', 'Night']
daypart_analysis['DayPart'] = pd.Categorical(daypart_analysis['DayPart'], categories=daypart_order, ordered=True)
daypart_analysis = daypart_analysis.sort_values('DayPart')

for _, row in daypart_analysis.iterrows():
    pct = row['NumTransactions'] / daypart_analysis['NumTransactions'].sum() * 100
    print(f"  {row['DayPart']:12s}: {row['NumTransactions']:,} transactions ({pct:.1f}%)")

print()

# ============================================================================
# 4. MARKET BASKET ANALYSIS
# ============================================================================

print("="*80)
print("ANALYSIS 2: MARKET BASKET ANALYSIS (Products Bought Together)")
print("="*80)

# Top selling items
print("\nTop 20 Best-Selling Items:")
print("-"*60)

item_counts = bakery_df['Item'].value_counts().head(20)
for i, (item, count) in enumerate(item_counts.items(), 1):
    print(f"  {i:2d}. {item[:50]:50s}: {count:,}")

# Transaction-level analysis for basket analysis
print("\n\nBasket Size Distribution:")
print("-"*60)

basket_sizes = bakery_df.groupby('Transaction').size()
print(f"Average basket size: {basket_sizes.mean():.2f} items")
print(f"Median basket size: {basket_sizes.median():.0f} items")
print(f"Max basket size: {basket_sizes.max()} items")

basket_dist = basket_sizes.value_counts().sort_index()
print("\nBasket size frequency:")
for size, count in basket_dist.head(10).items():
    pct = count / len(basket_sizes) * 100
    bar = '█' * int(pct / 2)
    print(f"  {size:2d} items: {count:5,} transactions ({pct:5.1f}%) {bar}")

# Product pairs (co-occurrence analysis)
print("\n\nProduct Pairing Analysis:")
print("-"*60)

# Create transaction-item matrix
transactions_items = bakery_df.groupby('Transaction')['Item'].apply(list).reset_index()

# Find frequent pairs
from itertools import combinations
pair_counts = Counter()

for items in transactions_items['Item']:
    if len(items) >= 2:
        # Get all 2-item combinations
        for pair in combinations(sorted(set(items)), 2):
            pair_counts[pair] += 1

# Top 15 product pairs
print("Top 15 Product Pairs (Frequently Bought Together):")
top_pairs = pair_counts.most_common(15)

for i, (pair, count) in enumerate(top_pairs, 1):
    # Calculate support
    total_trans = bakery_df['Transaction'].nunique()
    support = count / total_trans * 100
    print(f"  {i:2d}. {pair[0][:25]:25s} + {pair[1][:25]:25s}: {count:4,} times ({support:.1f}%)")

# Product triplets for cross-selling
print("\n\nTop 10 Product Triplets (3 items bought together):")
triplet_counts = Counter()

for items in transactions_items['Item']:
    if len(items) >= 3:
        for triplet in combinations(sorted(set(items)), 3):
            triplet_counts[triplet] += 1

top_triplets = triplet_counts.most_common(10)
for i, (triplet, count) in enumerate(top_triplets, 1):
    print(f"  {i:2d}. {triplet[0][:20]:20s} + {triplet[1][:20]:20s} + {triplet[2][:20]:20s}: {count:3,} times")

print()

# ============================================================================
# 5. WEATHER CORRELATION ANALYSIS
# ============================================================================

if weather_df is not None:
    print("="*80)
    print("ANALYSIS 3: WEATHER IMPACT ON BAKERY SALES")
    print("="*80)

    # Merge with weather
    bakery_df['Date_dt'] = pd.to_datetime(bakery_df['Date'])
    weather_df['Date'] = weather_df['timestamp'].dt.date

    # Hourly merge
    bakery_df['DateHour'] = bakery_df['DateTime'].dt.floor('H')
    weather_df['DateHour'] = weather_df['timestamp'].dt.floor('H')

    merged_df = bakery_df.merge(
        weather_df[['DateHour', 'temperature', 'precipitation', 'humidity']],
        on='DateHour',
        how='left'
    )

    print(f"\nMerged {merged_df['temperature'].notna().sum():,} records with weather data")

    # Temperature impact
    merged_df['TempCategory'] = pd.cut(
        merged_df['temperature'],
        bins=[-np.inf, 5, 10, 15, np.inf],
        labels=['Cold (<5°C)', 'Cool (5-10°C)', 'Mild (10-15°C)', 'Warm (>15°C)']
    )

    # Rain analysis
    merged_df['IsRaining'] = merged_df['precipitation'] > 0.5

    # Top products by temperature
    print("\nTop Products by Temperature:")
    print("-"*60)

    for temp_cat in ['Cold (<5°C)', 'Mild (10-15°C)', 'Warm (>15°C)']:
        temp_products = merged_df[merged_df['TempCategory'] == temp_cat]['Item'].value_counts().head(5)
        print(f"\n{temp_cat}:")
        for item, count in temp_products.items():
            print(f"  - {item[:40]:40s}: {count:,}")

    # Rain impact on sales
    print("\n\nRain Impact on Transaction Volume:")
    print("-"*60)

    rain_trans = merged_df[merged_df['IsRaining'] == True].groupby('Date')['Transaction'].nunique().mean()
    no_rain_trans = merged_df[merged_df['IsRaining'] == False].groupby('Date')['Transaction'].nunique().mean()

    if no_rain_trans > 0:
        rain_effect = ((rain_trans / no_rain_trans) - 1) * 100
        print(f"  Rainy days: {rain_trans:.1f} avg transactions/day")
        print(f"  No rain days: {no_rain_trans:.1f} avg transactions/day")
        print(f"  Rain effect: {rain_effect:+.1f}%")

    print()

# ============================================================================
# 6. DAY-OF-WEEK × TIME-OF-DAY ANALYSIS
# ============================================================================

print("="*80)
print("ANALYSIS 4: DAY × TIME INTERACTION PATTERNS")
print("="*80)

# Create heatmap data
heatmap_data = bakery_df.groupby(['DayName', 'Hour'])['Transaction'].nunique().reset_index()
heatmap_pivot = heatmap_data.pivot(index='DayName', columns='Hour', values='Transaction')
heatmap_pivot = heatmap_pivot.reindex(day_order)

print("\nBusiest Hour by Day of Week:")
print("-"*60)

for day in day_order:
    if day in heatmap_pivot.index:
        day_data = heatmap_pivot.loc[day]
        peak_hour = day_data.idxmax()
        peak_trans = day_data.max()
        print(f"  {day:12s}: Peak at {int(peak_hour):02d}:00 ({peak_trans:.0f} transactions)")

print()

# ============================================================================
# 7. PRODUCT SEQUENCING ANALYSIS
# ============================================================================

print("="*80)
print("ANALYSIS 5: PRODUCT SEQUENCING (What's Bought First)")
print("="*80)

# For each transaction, identify first item (earliest in item list or random if simultaneous)
first_items = bakery_df.sort_values(['Transaction', 'DateTime']).groupby('Transaction')['Item'].first()

print("\nTop 15 'First Purchase' Items (Entry Products):")
print("-"*60)

first_item_counts = first_items.value_counts().head(15)
total_first = len(first_items)

for i, (item, count) in enumerate(first_item_counts.items(), 1):
    pct = count / total_first * 100
    print(f"  {i:2d}. {item[:45]:45s}: {count:4,} times ({pct:.1f}%)")

# Items that are never first (always added to basket)
all_items = set(bakery_df['Item'].unique())
first_item_set = set(first_items.unique())
add_on_items = all_items - first_item_set

if add_on_items:
    print(f"\n\nAdd-On Items (Never bought first): {len(add_on_items)} items")
    add_on_counts = bakery_df[bakery_df['Item'].isin(add_on_items)]['Item'].value_counts().head(10)
    for item, count in add_on_counts.items():
        print(f"  - {item[:45]:45s}: {count:,} total sales (never first)")

print()

# ============================================================================
# 8. KEY INSIGHTS SUMMARY
# ============================================================================

print("="*80)
print("KEY INSIGHTS FOR AOFRIO BAKERY OUTLETS")
print("="*80)

print("""
DATA PROCESSING SUMMARY:
✓ Transactions analyzed: {total_trans:,}
✓ Unique items: {unique_items:,}
✓ Time period: {date_range}
✓ Granularity: Minute-level (96 15-min intervals per day)
✓ Product pairs discovered: {num_pairs:,}
✓ Weather integration: {weather_status}
""".format(
    peak_time=f"{peak_hour:02d}:{peak_min:02d}",
    morning_pct=daypart_analysis[daypart_analysis['DayPart'] == 'Morning']['NumTransactions'].values[0] / daypart_analysis['NumTransactions'].sum() * 100,
    weekend_lift=weekend_lift,
    avg_basket=basket_sizes.mean(),
    top_pair=f"{top_pairs[0][0][0][:20]} + {top_pairs[0][0][1][:20]} ({top_pairs[0][1]} times)" if top_pairs else "N/A",
    num_pairs=len(pair_counts),
    num_triplets=len(triplet_counts),
    num_addon=len(add_on_items),
    total_trans=bakery_df['Transaction'].nunique(),
    unique_items=bakery_df['Item'].nunique(),
    date_range=f"{bakery_df['DateTime'].min().date()} to {bakery_df['DateTime'].max().date()}",
    weather_status="Yes" if weather_df is not None else "No"
))

print("="*80)
print("ANALYSIS COMPLETE - Ready for visualization")
print("="*80)

# Save processed data
bakery_df.to_csv('../data/processed/processed_bakery_data.csv', index=False)
print("\n✓ Saved processed data to: ../data/processed/processed_bakery_data.csv")

# Save product pairs for visualization
pairs_df = pd.DataFrame(top_pairs, columns=['Products', 'Count'])
pairs_df['Product1'] = pairs_df['Products'].apply(lambda x: x[0])
pairs_df['Product2'] = pairs_df['Products'].apply(lambda x: x[1])
pairs_df = pairs_df[['Product1', 'Product2', 'Count']]
pairs_df.to_csv('../data/processed/product_pairs.csv', index=False)
print("✓ Saved product pairs to: ../data/processed/product_pairs.csv")
