# app.py
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import requests
import os
import googlemaps
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# Initialize database
def init_db():
    conn = sqlite3.connect('backend/db/maps.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS locations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  latitude REAL,
                  longitude REAL)''')
    conn.commit()
    conn.close()

init_db()

# Geocoding API (replace with your preferred service)
GEOCODING_API_URL = "https://nominatim.openstreetmap.org/search"

# Load environment variables and set up Google Maps client
load_dotenv()
google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=google_maps_api_key)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    params = {
        'q': query,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'Gas/1.0 (legaldesigndo@gmail.com)'
    }
    try:
        print(f"Sending request to: {GEOCODING_API_URL}")
        print(f"With params: {params}")
        response = requests.get(GEOCODING_API_URL, params=params, headers=headers)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        if data:
            location = data[0]
            return jsonify({
                'name': location['display_name'],
                'latitude': float(location['lat']),
                'longitude': float(location['lon'])
            })
        else:
            print("No data returned from API")
            return jsonify({'error': 'Location not found'}), 404
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {str(e)}")
        return jsonify({'error': f'API request failed: {str(e)}'}), 500
    except ValueError as e:
        print(f"JSON decode error: {str(e)}")
        return jsonify({'error': f'Invalid JSON response: {str(e)}'}), 500

@app.route('/save', methods=['POST'])
def save_location():
    data = request.json
    print(f"Received data to save: {data}")
    conn = sqlite3.connect('backend/db/maps.db')
    c = conn.cursor()
    
    # Check for duplicate
    c.execute("SELECT * FROM locations WHERE name = ? AND latitude = ? AND longitude = ?",
              (data['name'], data['latitude'], data['longitude']))
    existing_location = c.fetchone()
    
    if existing_location:
        conn.close()
        return jsonify({'message': 'Location already saved'}), 200
    
    c.execute("INSERT INTO locations (name, latitude, longitude) VALUES (?, ?, ?)",
              (data['name'], data['latitude'], data['longitude']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Location saved successfully'}), 201

@app.route('/locations', methods=['GET'])
def get_locations():
    conn = sqlite3.connect('backend/db/maps.db')
    c = conn.cursor()
    c.execute("SELECT * FROM locations")
    locations = [{'id': row[0], 'name': row[1], 'latitude': row[2], 'longitude': row[3]} for row in c.fetchall()]
    conn.close()
    return jsonify(locations)

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_location(id):
    print(f"Deleting location with id: {id}")
    conn = sqlite3.connect(''backend/db/maps.db'')
    c = conn.cursor()
    c.execute("DELETE FROM locations WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Location deleted successfully'}), 200

@app.route('/reset', methods=['POST'])
def reset_database():
    print("Resetting database")
    conn = sqlite3.connect('backend/db/maps.db')
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS locations")
    c.execute('''CREATE TABLE locations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  latitude REAL,
                  longitude REAL)''')
    conn.commit()
    conn.close()
    return jsonify({'message': 'Database reset successfully'}), 200

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    
    if lat is None or lng is None:
        return jsonify({'error': 'Latitude and longitude are required'}), 400

    # This is a placeholder. In a real application, you would use a service like Google Places API
    # to fetch real restaurant data. For demonstration, we'll return mock data.
    mock_restaurants = [
        {"id": 1, "name": "Pizza Place", "latitude": lat + 0.01, "longitude": lng + 0.01},
        {"id": 2, "name": "Burger Joint", "latitude": lat - 0.01, "longitude": lng - 0.01},
        {"id": 3, "name": "Sushi Bar", "latitude": lat + 0.02, "longitude": lng - 0.02},
    ]

    return jsonify(mock_restaurants)

def search_gas_stations(location):
    gas_stations = []
    next_page_token = None

    while True:
        results = gmaps.places_nearby(
            location=location,
            radius=5000,  # 5km radius, adjust as needed
            type='gas_station',
            page_token=next_page_token
        )

        gas_stations.extend(results['results'])
        next_page_token = results.get('next_page_token')

        if not next_page_token:
            break

        time.sleep(2)

    return gas_stations

@app.route('/gas-stations', methods=['GET'])
def get_gas_stations():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    
    if lat is None or lng is None:
        return jsonify({'error': 'Latitude and longitude are required'}), 400

    all_gas_stations = search_gas_stations((lat, lng))

    formatted_stations = [
        {
            "id": station.get('place_id', 'N/A'),
            "name": station.get('name', 'N/A'),
            "latitude": station['geometry']['location']['lat'],
            "longitude": station['geometry']['location']['lng'],
            "address": station.get('vicinity', 'N/A')
        }
        for station in all_gas_stations
    ]

    print("Formatted gas stations:", formatted_stations)  # Added debug log
    return jsonify(formatted_stations)

if __name__ == '__main__':
    app.run(debug=True)