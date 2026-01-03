"""
Bakery Analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

print("Loading processed bakery data...")

try:
    df = pd.read_csv('../data/processed/processed_bakery_data.csv')
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    print(f"✓ Loaded {len(df):,} transaction records")
except FileNotFoundError:
    print("✗ Error: processed_bakery_data.csv not found")
    print("Please run bakery_market_basket_analysis.py first")
    exit(1)

# Set professional style
sns.set_style("whitegrid")
sns.set_palette("Set2")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.family'] = 'sans-serif'

print("Creating visualizations...\n")

# ============================================================================
# VIZ 1: 15-Minute Granularity Heatmap (Day × Time)
# ============================================================================

print("1. Creating minute-level temporal heatmap...")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

# Day of week × Hour heatmap
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
heatmap_data = df.groupby(['DayName', 'Hour'])['Transaction'].nunique().reset_index()
heatmap_pivot = heatmap_data.pivot(index='DayName', columns='Hour', values='Transaction')
heatmap_pivot = heatmap_pivot.reindex(day_order)

sns.heatmap(heatmap_pivot, annot=False, cmap='YlOrRd', ax=ax1,
            cbar_kws={'label': 'Number of Transactions'})
ax1.set_title('Bakery Transaction Patterns: Day of Week × Hour of Day\n(Minute-Level Granularity)',
              fontsize=14, fontweight='bold', pad=15)
ax1.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
ax1.set_ylabel('Day of Week', fontsize=12, fontweight='bold')

# Hourly pattern across all days
hourly_pattern = df.groupby('Hour')['Transaction'].nunique()

ax2.bar(hourly_pattern.index, hourly_pattern.values, color='#2ecc71', alpha=0.8, edgecolor='darkgreen')
ax2.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
ax2.set_ylabel('Number of Transactions', fontsize=12, fontweight='bold')
ax2.set_title('Hourly Transaction Volume (All Days Combined)', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_xticks(range(0, 24, 2))

# Mark peak hour
peak_hour = hourly_pattern.idxmax()
peak_value = hourly_pattern.max()
ax2.annotate(f'Peak: {int(peak_hour):02d}:00\n({int(peak_value)} trans)',
             xy=(peak_hour, peak_value),
             xytext=(peak_hour-2, peak_value*1.15),
             fontsize=11, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.8),
             arrowprops=dict(arrowstyle='->', color='darkgreen', lw=2))

plt.tight_layout()
plt.savefig('../visualizations/viz1_temporal_heatmap_minute_level.png', dpi=300, bbox_inches='tight')
print("Saved: viz1_temporal_heatmap_minute_level.png")
plt.close()

# ============================================================================
# VIZ 2: Market Basket - Product Pairing Network
# ============================================================================

print("2. Creating product pairing network graph...")

try:
    pairs_df = pd.read_csv('../data/processed/product_pairs.csv')

    fig, ax = plt.subplots(figsize=(16, 12))

    # Create network graph
    G = nx.Graph()

    # Add top 20 pairs
    top_pairs = pairs_df.head(20)

    for _, row in top_pairs.iterrows():
        G.add_edge(row['Product1'][:20], row['Product2'][:20], weight=row['Count'])

    # Calculate node sizes based on total connections
    node_degrees = dict(G.degree())
    node_sizes = [node_degrees[node] * 500 for node in G.nodes()]

    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Draw network
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='lightblue',
                          alpha=0.7, edgecolors='darkblue', linewidths=2, ax=ax)

    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold', ax=ax)

    # Draw edges with varying thickness
    edges = G.edges()
    weights = [G[u][v]['weight'] for u, v in edges]
    max_weight = max(weights)
    edge_widths = [3 * (w / max_weight) for w in weights]

    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5, edge_color='gray', ax=ax)

    ax.set_title('Product Pairing Network: Items Frequently Bought Together\n(Node size = connection strength, Edge width = frequency)',
                 fontsize=14, fontweight='bold', pad=15)
    ax.axis('off')

    # Add legend
    legend_text = "Top product combinations:\n"
    for i, row in top_pairs.head(5).iterrows():
        legend_text += f"• {row['Product1'][:15]} + {row['Product2'][:15]}: {int(row['Count'])} times\n"

    ax.text(0.02, 0.98, legend_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()
    plt.savefig('../visualizations/viz2_product_pairing_network.png', dpi=300, bbox_inches='tight')
    print("Saved: viz2_product_pairing_network.png")
    plt.close()

except Exception as e:
    print(f"Could not create network graph: {e}")

# ============================================================================
# VIZ 3: Daypart Performance Comparison
# ============================================================================

print("3. Creating daypart performance analysis...")

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# Daypart distribution
daypart_trans = df.groupby('DayPart')['Transaction'].nunique()
daypart_order = ['Morning', 'Afternoon', 'Evening', 'Night']
daypart_trans = daypart_trans.reindex(daypart_order, fill_value=0)

colors_daypart = ['#f39c12', '#3498db', '#9b59b6', '#34495e']
bars = ax1.bar(range(len(daypart_trans)), daypart_trans.values, color=colors_daypart, alpha=0.8)
ax1.set_xticks(range(len(daypart_trans)))
ax1.set_xticklabels(daypart_trans.index, fontsize=11)
ax1.set_ylabel('Number of Transactions', fontsize=12, fontweight='bold')
ax1.set_title('Transaction Volume by Daypart', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='y')

# Add value labels
for bar, val in zip(bars, daypart_trans.values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
             f'{int(val):,}', ha='center', va='bottom', fontsize=11, fontweight='bold')

# Weekend vs Weekday
weekend_data = df[df['IsWeekend'] == True]
weekday_data = df[df['IsWeekend'] == False]

weekend_trans = weekend_data.groupby('Hour')['Transaction'].nunique()
weekday_trans = weekday_data.groupby('Hour')['Transaction'].nunique()

ax2.plot(weekend_trans.index, weekend_trans.values, marker='o', linewidth=2.5,
         markersize=7, label='Weekend', color='#e74c3c')
ax2.plot(weekday_trans.index, weekday_trans.values, marker='s', linewidth=2.5,
         markersize=7, label='Weekday', color='#3498db')

ax2.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
ax2.set_ylabel('Average Transactions', fontsize=12, fontweight='bold')
ax2.set_title('Weekend vs Weekday Hourly Patterns', fontsize=13, fontweight='bold')
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.set_xticks(range(0, 24, 2))

# Top items by daypart
top_morning = df[df['DayPart'] == 'Morning']['Item'].value_counts().head(10)
top_afternoon = df[df['DayPart'] == 'Afternoon']['Item'].value_counts().head(10)

ax3.barh(range(len(top_morning)), top_morning.values, color='#f39c12', alpha=0.8)
ax3.set_yticks(range(len(top_morning)))
ax3.set_yticklabels([item[:25] for item in top_morning.index], fontsize=9)
ax3.set_xlabel('Number of Sales', fontsize=11, fontweight='bold')
ax3.set_title('Top 10 Items: Morning (5 AM - 12 PM)', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='x')

ax4.barh(range(len(top_afternoon)), top_afternoon.values, color='#3498db', alpha=0.8)
ax4.set_yticks(range(len(top_afternoon)))
ax4.set_yticklabels([item[:25] for item in top_afternoon.index], fontsize=9)
ax4.set_xlabel('Number of Sales', fontsize=11, fontweight='bold')
ax4.set_title('Top 10 Items: Afternoon (12 PM - 5 PM)', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('../visualizations/viz3_daypart_performance.png', dpi=300, bbox_inches='tight')
print("Saved: viz3_daypart_performance.png")
plt.close()

# ============================================================================
# VIZ 4: Basket Size and Product Affinity Matrix
# ============================================================================

print("4. Creating basket analysis and affinity matrix...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Basket size distribution
basket_sizes = df.groupby('Transaction')['Item'].count()
basket_dist = basket_sizes.value_counts().sort_index().head(15)

bars = ax1.bar(basket_dist.index, basket_dist.values, color='#2ecc71', alpha=0.8, edgecolor='darkgreen')
ax1.set_xlabel('Basket Size (Number of Items)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Number of Transactions', fontsize=12, fontweight='bold')
ax1.set_title('Basket Size Distribution\n(How Many Items Per Transaction)', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='y')

# Add average line
avg_basket = basket_sizes.mean()
ax1.axvline(avg_basket, color='red', linestyle='--', linewidth=2, label=f'Average: {avg_basket:.2f}')
ax1.legend(fontsize=11)

# Add percentage labels on top bars
for bar, val in zip(bars, basket_dist.values):
    pct = val / basket_dist.sum() * 100
    if pct > 3:  # Only show if > 3%
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
                 f'{pct:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Product affinity matrix (top 10 products)
try:
    top_10_products = df['Item'].value_counts().head(10).index.tolist()

    # Create co-occurrence matrix
    affinity_matrix = pd.DataFrame(0, index=top_10_products, columns=top_10_products)

    for trans_id in df['Transaction'].unique():
        trans_items = df[df['Transaction'] == trans_id]['Item'].unique()
        trans_items_top = [item for item in trans_items if item in top_10_products]

        for i, item1 in enumerate(trans_items_top):
            for item2 in trans_items_top[i+1:]:
                affinity_matrix.loc[item1, item2] += 1
                affinity_matrix.loc[item2, item1] += 1

    # Shorten product names for display
    short_names = [name[:15] for name in top_10_products]
    affinity_matrix.index = short_names
    affinity_matrix.columns = short_names

    sns.heatmap(affinity_matrix, annot=True, fmt='g', cmap='YlGnBu', ax=ax2,
                cbar_kws={'label': 'Co-occurrence Count'})
    ax2.set_title('Product Affinity Matrix\n(Top 10 Products - How Often Bought Together)',
                  fontsize=13, fontweight='bold', pad=10)
    ax2.set_xlabel('', fontsize=11)
    ax2.set_ylabel('', fontsize=11)

except Exception as e:
    print(f"   ⚠ Could not create affinity matrix: {e}")
    ax2.text(0.5, 0.5, 'Affinity matrix\nrequires more data', ha='center', va='center',
             transform=ax2.transAxes, fontsize=14)

plt.tight_layout()
plt.savefig('../visualizations/viz4_basket_and_affinity.png', dpi=300, bbox_inches='tight')
print("Saved: viz4_basket_and_affinity.png")
plt.close()
