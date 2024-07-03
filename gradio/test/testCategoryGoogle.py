from dotenv import load_dotenv
import os
import googlemaps
from datetime import datetime
import csv
import time

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

# Initialize the Google Maps client
gmaps = googlemaps.Client(key=google_maps_api_key)

# Define the search area (approximate coordinates for Dominican Republic)
location = (18.7357, -70.1627)

# Function to search for gas stations and handle pagination
def search_gas_stations(location):
    gas_stations = []
    next_page_token = None

    while True:
        # Search for gas stations
        results = gmaps.places_nearby(
            location=location,
            radius=50000,  # 50km radius, adjust as needed
            type='gas_station',
            page_token=next_page_token
        )

        gas_stations.extend(results['results'])

        next_page_token = results.get('next_page_token')

        if not next_page_token:
            break

        # Wait before making the next request (required for next page token to become valid)
        time.sleep(2)

    return gas_stations

# Perform the search
all_gas_stations = search_gas_stations(location)

# Write results to CSV
with open('gradio/sample_data/dominican_republic_gas_stations_google.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Name', 'Address', 'Latitude', 'Longitude', 'Place ID'])

    for station in all_gas_stations:
        writer.writerow([
            station.get('name', 'N/A'),
            station.get('vicinity', 'N/A'),
            station['geometry']['location']['lat'],
            station['geometry']['location']['lng'],
            station.get('place_id', 'N/A')
        ])

print(f"Found and saved {len(all_gas_stations)} gas stations to CSV.")