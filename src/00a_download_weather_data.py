"""
Weather Data Download Script
Downloads historical weather data for Edinburgh from Open-Meteo API
Date range: 2016-01-11 to 2017-12-03 (matching bakery dataset)
"""

import requests
import pandas as pd
import json
from datetime import datetime
import time

print("="*80)
print("WEATHER DATA DOWNLOAD - Edinburgh Historical Data")
print("="*80)
print()

# Edinburgh coordinates
LATITUDE = 55.9533
LONGITUDE = -3.1883
LOCATION = "Edinburgh, Scotland"

# Date range matching bakery dataset
START_DATE = "2016-01-11"
END_DATE = "2017-12-03"

print(f"Location: {LOCATION}")
print(f"Coordinates: {LATITUDE}°N, {LONGITUDE}°W")
print(f"Date range: {START_DATE} to {END_DATE}")
print()

# Open-Meteo API endpoint
API_URL = "https://archive-api.open-meteo.com/v1/archive"

# Parameters for historical weather data
params = {
    'latitude': LATITUDE,
    'longitude': LONGITUDE,
    'start_date': START_DATE,
    'end_date': END_DATE,
    'hourly': [
        'temperature_2m',
        'precipitation',
        'relative_humidity_2m',
        'wind_speed_10m',
        'cloud_cover'
    ],
    'timezone': 'Europe/London'
}

print("Fetching weather data from Open-Meteo API...")
print("-"*80)

try:
    # Make API request
    response = requests.get(API_URL, params=params)
    response.raise_for_status()

    # Parse JSON response
    data = response.json()

    print(f"✓ Successfully retrieved data from API")
    print(f"  API URL: {API_URL}")
    print()

    # Extract hourly data
    hourly = data['hourly']

    # Create DataFrame
    weather_df = pd.DataFrame({
        'timestamp': pd.to_datetime(hourly['time']),
        'temperature': hourly['temperature_2m'],
        'precipitation': hourly['precipitation'],
        'humidity': hourly['relative_humidity_2m'],
        'wind_speed': hourly['wind_speed_10m'],
        'cloud_cover': hourly['cloud_cover']
    })

    # Data summary
    print("Data Summary:")
    print("-"*80)
    print(f"Total records: {len(weather_df):,} hourly observations")
    print(f"Date range: {weather_df['timestamp'].min()} to {weather_df['timestamp'].max()}")
    print(f"Number of days: {(weather_df['timestamp'].max() - weather_df['timestamp'].min()).days}")
    print()

    print("Weather Statistics:")
    print("-"*80)
    print(f"Temperature:")
    print(f"  Min: {weather_df['temperature'].min():.1f}°C")
    print(f"  Max: {weather_df['temperature'].max():.1f}°C")
    print(f"  Mean: {weather_df['temperature'].mean():.1f}°C")
    print()

    print(f"Precipitation:")
    print(f"  Total: {weather_df['precipitation'].sum():.1f} mm")
    print(f"  Rainy hours: {(weather_df['precipitation'] > 0).sum():,} ({(weather_df['precipitation'] > 0).sum() / len(weather_df) * 100:.1f}%)")
    print()

    print(f"Humidity:")
    print(f"  Min: {weather_df['humidity'].min():.1f}%")
    print(f"  Max: {weather_df['humidity'].max():.1f}%")
    print(f"  Mean: {weather_df['humidity'].mean():.1f}%")
    print()

    print(f"Wind Speed:")
    print(f"  Min: {weather_df['wind_speed'].min():.1f} km/h")
    print(f"  Max: {weather_df['wind_speed'].max():.1f} km/h")
    print(f"  Mean: {weather_df['wind_speed'].mean():.1f} km/h")
    print()

    print(f"Cloud Cover:")
    print(f"  Min: {weather_df['cloud_cover'].min():.1f}%")
    print(f"  Max: {weather_df['cloud_cover'].max():.1f}%")
    print(f"  Mean: {weather_df['cloud_cover'].mean():.1f}%")
    print()

    # Sample data
    print("Sample data (first 5 records):")
    print("-"*80)
    print(weather_df.head())
    print()

    # Save to CSV
    output_path = '../data/raw/edinburgh_weather.csv'
    weather_df.to_csv(output_path, index=False)

    print("="*80)
    print(f"✓ Weather data saved to: {output_path}")
    print("="*80)
    print()

    print("Data Source Attribution:")
    print("-"*80)
    print("Weather data by Open-Meteo.com")
    print("API: https://open-meteo.com/")
    print("License: CC BY 4.0")
    print()

    print("Next Steps:")
    print("-"*80)
    print("1. Run: python 00_data_processing.py")
    print("   This will merge weather data with bakery transactions")
    print()
    print("2. Weather integration features:")
    print("   - Temperature impact on product preferences")
    print("   - Rain correlation with transaction volume")
    print("   - Humidity and cloud cover analysis")
    print()

except requests.exceptions.RequestException as e:
    print(f"✗ Error fetching data from API: {e}")
    print()
    print("Troubleshooting:")
    print("- Check internet connection")
    print("- Verify Open-Meteo API is accessible")
    print("- Try again later if API is temporarily unavailable")
    exit(1)

except KeyError as e:
    print(f"✗ Error parsing API response: {e}")
    print()
    print("The API response structure may have changed.")
    print("Check Open-Meteo API documentation: https://open-meteo.com/en/docs/historical-weather-api")
    exit(1)

except Exception as e:
    print(f"✗ Unexpected error: {e}")
    exit(1)
