"""
Product Pairing Visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle, FancyBboxPatch
import warnings
warnings.filterwarnings('ignore')

print("Loading product pairing data...")

# Load the pairing data
pairs_df = pd.read_csv('../data/processed/product_pairs.csv')
bakery_df = pd.read_csv('../data/processed/processed_bakery_data.csv')

print(f"Loaded {len(pairs_df)} product pairs")
print()

# Set professional style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.family'] = 'sans-serif'

# ============================================================================
# VISUALIZATION 1: Clean Bar Chart of Top Product Pairs
# ============================================================================

print("Creating Visualization 1: Top Product Pairs Bar Chart...")

fig, ax = plt.subplots(figsize=(14, 10))

# Get top 20 pairs
top_pairs = pairs_df.head(20).copy()

# Create labels
top_pairs['Label'] = top_pairs['Product1'].str[:20] + '\n+\n' + top_pairs['Product2'].str[:20]

# Create color gradient
colors = plt.cm.RdYlGn_r(np.linspace(0.3, 0.9, len(top_pairs)))

# Create horizontal bar chart
bars = ax.barh(range(len(top_pairs)), top_pairs['Count'], color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

# Customize axes
ax.set_yticks(range(len(top_pairs)))
ax.set_yticklabels(top_pairs['Label'], fontsize=9)
ax.set_xlabel('Number of Times Bought Together', fontsize=13, fontweight='bold')
ax.set_title('Top 20 Product Pairings: Most Frequently Purchased Together\nBakery Analysis - Cross-Selling Opportunities',
             fontsize=15, fontweight='bold', pad=20)

# Add value labels on bars
for i, (bar, count) in enumerate(zip(bars, top_pairs['Count'])):
    # Calculate percentage
    total_trans = 9465  # From analysis
    pct = (count / total_trans) * 100

    ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2,
            f'{int(count)} ({pct:.1f}%)',
            va='center', fontsize=10, fontweight='bold')

# Add grid
ax.grid(True, alpha=0.3, axis='x')
ax.set_axisbelow(True)

# Add annotation for top pair
top_count = top_pairs.iloc[0]['Count']
top_pct = (top_count / 9465) * 100
ax.annotate(f'Most Common Pair!\n{top_count} times ({top_pct:.1f}% of transactions)',
            xy=(top_count, 0),
            xytext=(top_count + 150, 3),
            fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='yellow', alpha=0.8, edgecolor='black', linewidth=2),
            arrowprops=dict(arrowstyle='->', color='black', lw=2))

plt.tight_layout()
plt.savefig('../visualizations/viz2_product_pairing_bar_chart.png', dpi=300, bbox_inches='tight')
print("Saved: viz2_product_pairing_bar_chart.png")
plt.close()

# ============================================================================
# VISUALIZATION 2: Product Affinity Matrix (Heatmap Style)
# ============================================================================

print("Creating Visualization 2: Product Affinity Heatmap...")

fig, ax = plt.subplots(figsize=(16, 14))

# Get top 12 products
top_products = bakery_df['Item'].value_counts().head(12).index.tolist()

# Create affinity matrix
affinity_matrix = pd.DataFrame(0, index=top_products, columns=top_products, dtype=int)

# Fill matrix with co-occurrence counts
for _, row in pairs_df.iterrows():
    if row['Product1'] in top_products and row['Product2'] in top_products:
        affinity_matrix.loc[row['Product1'], row['Product2']] = row['Count']
        affinity_matrix.loc[row['Product2'], row['Product1']] = row['Count']

# Shorten names for display
short_names = [name[:15] for name in top_products]
affinity_matrix.index = short_names
affinity_matrix.columns = short_names

# Create heatmap
mask = np.triu(np.ones_like(affinity_matrix, dtype=bool), k=1)  # Mask upper triangle
sns.heatmap(affinity_matrix, mask=mask, annot=True, fmt='g', cmap='YlOrRd',
            ax=ax, cbar_kws={'label': 'Times Bought Together'},
            linewidths=1, linecolor='white', square=True,
            vmin=0, vmax=affinity_matrix.max().max())

ax.set_title('Product Affinity Matrix: How Often Are Products Purchased Together?\n(Top 12 Products - Lower Triangle Shows Co-Purchase Frequency)',
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('', fontsize=11)
ax.set_ylabel('', fontsize=11)

# Rotate labels
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
plt.setp(ax.get_yticklabels(), rotation=0, fontsize=10)

plt.tight_layout()
plt.savefig('../visualizations/viz2_product_affinity_heatmap.png', dpi=300, bbox_inches='tight')
print("Saved: viz2_product_affinity_heatmap.png")
plt.close()

# ============================================================================
# VISUALIZATION 3: Sankey-Style Flow Diagram
# ============================================================================

print("Creating Visualization 3: Product Pairing Flow Chart...")

fig, ax = plt.subplots(figsize=(16, 12))

# Get top 8 pairs for clarity
top_8_pairs = pairs_df.head(8)

# Get unique products from top pairs
all_products = list(set(top_8_pairs['Product1'].tolist() + top_8_pairs['Product2'].tolist()))

# Position products in two columns
left_products = sorted(set(top_8_pairs['Product1']))
right_products = sorted(set(top_8_pairs['Product2']))

# Create positions
y_spacing = 1.0
left_x = 0.2
right_x = 0.8

left_positions = {prod: (left_x, i * y_spacing) for i, prod in enumerate(left_products)}
right_positions = {prod: (right_x, i * y_spacing) for i, prod in enumerate(right_products)}

# Combine positions
positions = {**left_positions, **right_positions}

# Draw connections
for _, row in top_8_pairs.iterrows():
    prod1, prod2, count = row['Product1'], row['Product2'], row['Count']

    if prod1 in left_positions and prod2 in right_positions:
        x1, y1 = left_positions[prod1]
        x2, y2 = right_positions[prod2]

        # Line width based on frequency
        linewidth = 1 + (count / top_8_pairs['Count'].max()) * 10

        # Draw curved connection
        ax.plot([x1 + 0.1, x2 - 0.1], [y1, y2],
                linewidth=linewidth, alpha=0.6, color='steelblue')

        # Add count label in middle
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        ax.text(mid_x, mid_y, f'{count}',
                fontsize=9, fontweight='bold', ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))

# Draw product boxes
for prod, (x, y) in left_positions.items():
    box = FancyBboxPatch((x, y - 0.3), 0.15, 0.6,
                         boxstyle="round,pad=0.05",
                         facecolor='lightcoral', edgecolor='black', linewidth=2)
    ax.add_patch(box)
    ax.text(x + 0.075, y, prod[:12], ha='center', va='center',
            fontsize=9, fontweight='bold')

for prod, (x, y) in right_positions.items():
    if prod not in left_positions:  # Don't duplicate
        box = FancyBboxPatch((x - 0.15, y - 0.3), 0.15, 0.6,
                             boxstyle="round,pad=0.05",
                             facecolor='lightgreen', edgecolor='black', linewidth=2)
        ax.add_patch(box)
        ax.text(x - 0.075, y, prod[:12], ha='center', va='center',
                fontsize=9, fontweight='bold')

ax.set_xlim(0, 1)
ax.set_ylim(-1, max(len(left_products), len(right_products)) * y_spacing)
ax.axis('off')

ax.set_title('Product Pairing Flow: Top 8 Combinations\n(Line thickness = purchase frequency)',
             fontsize=15, fontweight='bold', pad=20)

# Add legend
legend_text = "Product Pairs (Frequency):\n"
for i, row in top_8_pairs.iterrows():
    legend_text += f"{i+1}. {row['Product1'][:15]} + {row['Product2'][:15]}: {row['Count']}\n"

ax.text(0.02, 0.98, legend_text, transform=ax.transAxes,
        fontsize=9, verticalalignment='top', family='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
plt.savefig('../visualizations/viz2_product_pairing_flow.png', dpi=300, bbox_inches='tight')
print("Saved: viz2_product_pairing_flow.png")
plt.close()

# ============================================================================
# VISUALIZATION 4: Coffee-Centric Radial Chart
# ============================================================================

print("Creating Visualization 4: Coffee-Centric Product Pairs...")

fig, ax = plt.subplots(figsize=(14, 14), subplot_kw=dict(projection='polar'))

# Get all pairs involving Coffee
coffee_pairs = pairs_df[(pairs_df['Product1'] == 'COFFEE') | (pairs_df['Product2'] == 'COFFEE')].copy()

# Get the other product in each pair
coffee_pairs['Partner'] = coffee_pairs.apply(
    lambda row: row['Product2'] if row['Product1'] == 'COFFEE' else row['Product1'],
    axis=1
)

# Sort by count and take top 15
coffee_pairs = coffee_pairs.sort_values('Count', ascending=False).head(15)

# Create angles for each product
n = len(coffee_pairs)
angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()

# Plot bars
bars = ax.bar(angles, coffee_pairs['Count'],
              width=0.4, alpha=0.8, edgecolor='black', linewidth=2)

# Color bars by value
colors = plt.cm.RdYlGn_r(np.linspace(0.3, 0.9, n))
for bar, color in zip(bars, colors):
    bar.set_facecolor(color)

# Add labels
ax.set_xticks(angles)
ax.set_xticklabels(coffee_pairs['Partner'].str[:15], fontsize=10)

# Add value labels
for angle, count, bar in zip(angles, coffee_pairs['Count'], bars):
    rotation = np.rad2deg(angle)
    if rotation > 90 and rotation < 270:
        rotation = rotation + 180

    ax.text(angle, count + 30, f'{int(count)}',
            ha='center', va='center', fontsize=9, fontweight='bold',
            rotation=rotation)

ax.set_title('Coffee Pairing Analysis: What Products Are Bought With Coffee?\n(Coffee appears in 60.3% of multi-item transactions)',
             fontsize=14, fontweight='bold', pad=30, y=1.08)

# Add central label
ax.text(0, 0, 'COFFEE\n(Center)', ha='center', va='center',
        fontsize=16, fontweight='bold',
        bbox=dict(boxstyle='circle,pad=0.3', facecolor='yellow', alpha=0.9, edgecolor='black', linewidth=3))

plt.tight_layout()
plt.savefig('../visualizations/viz2_coffee_centric_radial.png', dpi=300, bbox_inches='tight')
print("Saved: viz2_coffee_centric_radial.png")
plt.close()

# ============================================================================
# VISUALIZATION 5: Grouped Product Categories
# ============================================================================

print("Creating Visualization 5: Product Pairing by Category...")

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# Define product categories
categories = {
    'Hot Drinks': ['COFFEE', 'TEA', 'HOT CHOCOLATE'],
    'Baked Goods': ['BREAD', 'CAKE', 'PASTRY', 'MUFFIN', 'SCONE', 'TOAST', 'BROWNIE'],
    'Lunch Items': ['SANDWICH', 'SOUP', 'SALAD'],
    'Sweets': ['COOKIES', 'TRUFFLES', 'ALFAJORES', 'MEDIALUNA']
}

# Analyze pairing patterns between categories
cat_pairs = {}
for cat1, prods1 in categories.items():
    for cat2, prods2 in categories.items():
        if cat1 <= cat2:  # Avoid duplicates
            count = 0
            for _, row in pairs_df.iterrows():
                if ((row['Product1'] in prods1 and row['Product2'] in prods2) or
                    (row['Product1'] in prods2 and row['Product2'] in prods1)):
                    count += row['Count']
            if count > 0:
                key = f"{cat1} +\n{cat2}" if cat1 != cat2 else cat1
                cat_pairs[key] = count

# Plot 1: Category pairing frequencies
sorted_cats = sorted(cat_pairs.items(), key=lambda x: x[1], reverse=True)[:10]
cats, counts = zip(*sorted_cats)

bars = ax1.barh(range(len(cats)), counts, color='steelblue', alpha=0.8, edgecolor='black')
ax1.set_yticks(range(len(cats)))
ax1.set_yticklabels(cats, fontsize=10)
ax1.set_xlabel('Total Co-Purchases', fontsize=11, fontweight='bold')
ax1.set_title('Product Category Pairings', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='x')

# Add value labels
for bar, count in zip(bars, counts):
    ax1.text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2,
             f'{int(count)}', va='center', fontsize=10, fontweight='bold')

# Plot 2: Top individual products
top_items = bakery_df['Item'].value_counts().head(10)
bars2 = ax2.bar(range(len(top_items)), top_items.values, color='coral', alpha=0.8, edgecolor='black')
ax2.set_xticks(range(len(top_items)))
ax2.set_xticklabels([item[:12] for item in top_items.index], rotation=45, ha='right', fontsize=9)
ax2.set_ylabel('Total Sales', fontsize=11, fontweight='bold')
ax2.set_title('Top 10 Individual Products', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

# Plot 3: Basket size by entry product
entry_products = ['COFFEE', 'BREAD', 'TEA', 'CAKE', 'SANDWICH']
basket_sizes = []
for prod in entry_products:
    # Get transactions that start with this product
    avg_size = bakery_df[bakery_df['Item'] == prod].groupby('Transaction').size().mean()
    basket_sizes.append(avg_size if not pd.isna(avg_size) else 0)

bars3 = ax3.bar(range(len(entry_products)), basket_sizes, color='lightgreen', alpha=0.8, edgecolor='black')
ax3.set_xticks(range(len(entry_products)))
ax3.set_xticklabels(entry_products, fontsize=10)
ax3.set_ylabel('Average Basket Size', fontsize=11, fontweight='bold')
ax3.set_title('Average Basket Size When Starting With Each Product', fontsize=12, fontweight='bold')
ax3.axhline(y=2.17, color='red', linestyle='--', linewidth=2, label='Overall Average (2.17)')
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3, axis='y')

# Plot 4: Cross-selling potential
cross_sell_potential = pairs_df.head(8).copy()
cross_sell_potential['Label'] = (cross_sell_potential['Product1'].str[:10] + '\n→\n' +
                                  cross_sell_potential['Product2'].str[:10])

bars4 = ax4.barh(range(len(cross_sell_potential)), cross_sell_potential['Count'],
                 color=plt.cm.RdYlGn_r(np.linspace(0.3, 0.9, len(cross_sell_potential))),
                 alpha=0.8, edgecolor='black')
ax4.set_yticks(range(len(cross_sell_potential)))
ax4.set_yticklabels(cross_sell_potential['Label'], fontsize=9)
ax4.set_xlabel('Cross-Sell Opportunities (Frequency)', fontsize=11, fontweight='bold')
ax4.set_title('Top 8 Cross-Selling Recommendations', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='x')

plt.suptitle('Product Pairing Analysis: Category & Cross-Selling Insights',
             fontsize=15, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('../visualizations/viz2_product_categories_analysis.png', dpi=300, bbox_inches='tight')
print("Saved: viz2_product_categories_analysis.png")
plt.close()
