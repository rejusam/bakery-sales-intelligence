# Quick Start Guide - Bakery Sales Intelligence

This guide will help you get the analysis running quickly.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for weather data download)

## Installation

1. **Clone or download the repository**
   ```bash
   cd /path/to/bakery-sales-intelligence
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Analysis

### Option 1: Automated Pipeline (Recommended)

Run all scripts in the correct order automatically:

```bash
cd src
chmod +x run_analysis.sh
./run_analysis.sh
```

This will execute all scripts in sequence:
1. `00a_download_weather_data.py` - Downloads Edinburgh weather data
2. `00b_data_processing.py` - Processes raw data
3. `01_create_bakery_visualizations.py` - Creates primary visualizations
4. `02_create_better_pairing_viz.py` - Creates product pairing visualizations
5. `03_analyze_temperature_statistical.py` - Statistical temperature analysis
6. `04_create_weekend_weekday_comparison.py` - Weekend vs weekday analysis
7. `05_create_supplemental_visualizations.py` - Additional visualizations
8. `06_create_surprising_findings_viz.py` - Key findings visualizations

**Total runtime**: ~30-45 seconds

### Option 2: Manual Execution

Run scripts individually for more control:

```bash
cd src

# Step 0a (Optional): Download weather data
# Only needed once, skip if edinburgh_weather.csv already exists
python 00a_download_weather_data.py

# Step 0b: Process data (REQUIRED)
python 00b_data_processing.py

# Step 1-6: Generate visualizations (run in any order after 0b)
python 01_create_bakery_visualizations.py
python 02_create_better_pairing_viz.py
python 03_analyze_temperature_statistical.py
python 04_create_weekend_weekday_comparison.py
python 05_create_supplemental_visualizations.py
python 06_create_surprising_findings_viz.py
```

## What Gets Generated

After running the analysis, you'll have:

### Data Files
- `data/processed/processed_bakery_data.csv` - Enriched transaction data with temporal features
- `data/processed/product_pairs.csv` - Top product pairing combinations
- `data/raw/edinburgh_weather.csv` - Historical weather data (if downloaded)

### Visualizations (17 PNG files in `visualizations/`)
1. `viz1_temporal_heatmap_minute_level.png` - Minute-level transaction patterns
2. `viz2_product_pairing_bar_chart.png` - Top product pairs
3. `viz2_product_pairing_network.png` - Product relationship network
4. `viz2_product_affinity_heatmap.png` - Product affinity matrix
5. `viz2_product_pairing_flow.png` - Product flow diagram
6. `viz2_coffee_centric_radial.png` - Coffee-centric pairings
7. `viz2_product_categories_analysis.png` - Category analysis
8. `viz3_daypart_performance.png` - Performance by time of day
9. `viz4_basket_and_affinity.png` - Basket analysis
10. `viz7_weekend_weekday_comprehensive.png` - Weekend vs weekday patterns
11. `viz_temperature_statistical_analysis.png` - Temperature impact analysis
12. `viz_supplemental1_entry_vs_addon.png` - Entry vs add-on products
13. `viz_supplemental2_coffee_centrality.png` - Coffee as anchor product
14. `viz_supplemental4_executive_dashboard.png` - Executive summary
15. `viz_surprise1_weekend_morning_boom.png` - Weekend morning patterns
16. `viz_surprise2_slump_and_baskets.png` - Afternoon slump analysis
17. `viz_surprise3_daves_hypotheses.png` - Hypothesis validation

## Verifying Success

Check that outputs were created:

```bash
# Check processed data
ls -lh data/processed/

# Check visualizations
ls -1 visualizations/*.png | wc -l
# Should output: 17
```

## Troubleshooting

### Missing Dependencies
```bash
# If you get import errors, install missing packages:
pip install pandas numpy matplotlib seaborn scipy requests
```

### Weather Data Download Fails
```bash
# If weather download fails, the analysis will still run
# but weather-related insights will be skipped
# You can run the analysis without weather data
```

### Permission Denied (run_analysis.sh)
```bash
# Make the script executable:
chmod +x src/run_analysis.sh
```

### File Not Found Errors
```bash
# Ensure you have the raw data file:
ls data/raw/BreadBasket_DMS.csv

# If missing, download from:
# https://www.kaggle.com/datasets/akashdeepkuila/bakery
```

## Next Steps

After running the analysis:
1. Check `README.md` for detailed findings and business insights
2. Review visualizations in `visualizations/` directory
3. Examine processed data in `data/processed/` for further analysis
4. Read `src/README.md` for script execution details

