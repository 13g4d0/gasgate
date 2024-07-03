// App.jsx
import React, { useState, useEffect } from 'react';
import { GoogleMap, useJsApiLoader, Marker, InfoWindow } from '@react-google-maps/api';
import Sidebar from './Sidebar';
import ButtonRibbon from './ButtonRibbon';

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [currentLocation, setCurrentLocation] = useState(null);
  const [savedLocations, setSavedLocations] = useState([]);
  const [mapCenter, setMapCenter] = useState({ lat: 0, lng: 0 });
  const [mapZoom, setMapZoom] = useState(2);
  const [isLocationSaved, setIsLocationSaved] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [restaurants, setRestaurants] = useState([]);
  const [gasStations, setGasStations] = useState([]);
  const [isLoadingGasStations, setIsLoadingGasStations] = useState(false);
  const [selectedStation, setSelectedStation] = useState(null);

  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: "YOUT GOOGLE API KEY HERE",
    libraries: ['places', 'geometry', 'marker'],
  })

  useEffect(() => {
    console.log('App component mounted');
    fetchSavedLocations();
    getUserLocation();
  }, []);

  const fetchSavedLocations = async () => {
    console.log('Fetching saved locations');
    try {
      const response = await fetch('http://localhost:5000/locations');
      const data = await response.json();
      console.log('Saved locations:', data);
      setSavedLocations(data);
    } catch (error) {
      console.error('Error fetching saved locations:', error);
    }
  };

  const getUserLocation = () => {
    console.log('Getting user location');
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          console.log('User location:', position.coords);
          setMapCenter({ lat: position.coords.latitude, lng: position.coords.longitude });
          setMapZoom(13);
        },
        (error) => {
          console.error("Error getting user location:", error);
          setMapCenter({ lat: 0, lng: 0 });
        }
      );
    } else {
      console.log('Geolocation is not supported by this browser.');
      setMapCenter({ lat: 0, lng: 0 });
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    console.log('Searching for:', searchQuery);
    try {
      const response = await fetch(`http://localhost:5000/search?q=${searchQuery}`);
      const data = await response.json();

      console.log('Search result:', data);
      setCurrentLocation(data);
      setMapCenter({ lat: parseFloat(data.latitude), lng: parseFloat(data.longitude) });
      setMapZoom(15);
      setIsLocationSaved(false);
    } catch (error) {
      console.error('Error searching location:', error);
    }
  };

  const handleSave = async () => {
    if (currentLocation && !isLocationSaved) {
      console.log('Saving location:', currentLocation);
      try {
        const response = await fetch('http://localhost:5000/save', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(currentLocation),
        });
        const result = await response.json();
        console.log('Save response:', result);
        if (response.status === 201) {
          setIsLocationSaved(true);
          fetchSavedLocations();
          setCurrentLocation(null);
        } else {
          console.log('Location already saved or error occurred');
        }
      } catch (error) {
        console.error('Error saving location:', error);
      }
    }
  };

  const handleDelete = async (id) => {
    console.log('Deleting location with id:', id);
    try {
      const response = await fetch(`http://localhost:5000/delete/${id}`, {
        method: 'DELETE',
      });
      const result = await response.json();
      console.log('Delete response:', result);
      fetchSavedLocations();
    } catch (error) {
      console.error('Error deleting location:', error);
    }
  };

  const handleShowRestaurants = async () => {
    try {
      const response = await fetch(`http://localhost:5000/restaurants?lat=${mapCenter.lat}&lng=${mapCenter.lng}`);
      const data = await response.json();
      setRestaurants(data);
    } catch (error) {
      console.error('Error fetching restaurants:', error);
    }
  };

  const fetchGasStations = async () => {
    setIsLoadingGasStations(true);
    try {
      const response = await fetch(`http://localhost:5000/gas-stations?lat=${mapCenter.lat}&lng=${mapCenter.lng}`);
      const data = await response.json();
      console.log('Fetched gas stations:', data);
      setGasStations(data);
    } catch (error) {
      console.error('Error fetching gas stations:', error);
    } finally {
      setIsLoadingGasStations(false);
    }
  };

  useEffect(() => {
    console.log('Gas stations updated:', gasStations);
  }, [gasStations]);

  useEffect(() => {
    if (gasStations.length > 0) {
      const bounds = new window.google.maps.LatLngBounds();
      gasStations.forEach((station) => {
        bounds.extend({ lat: Number(station.latitude), lng: Number(station.longitude) });
      });
      setMapCenter(bounds.getCenter());
      // If you're using a map ref, you can fit the bounds like this:
      // mapRef.current.fitBounds(bounds);
    }
  }, [gasStations]);

  const handleResetDatabase = async () => {
    try {
      const response = await fetch('http://localhost:5000/reset', {
        method: 'POST',
      });
      const result = await response.json();
      console.log('Reset response:', result);
      setSavedLocations([]);
      setCurrentLocation(null);
      setRestaurants([]);
      setGasStations([]);
    } catch (error) {
      console.error('Error resetting database:', error);
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="App" style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '10px', backgroundColor: '#fff', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', display: 'flex', alignItems: 'center' }}>
        <button onClick={toggleSidebar} style={{ marginRight: '10px' }}>
          {isSidebarOpen ? '≡' : '☰'}
        </button>
        <form onSubmit={handleSearch} style={{ display: 'flex', flex: 1 }}>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search Google Maps"
            style={{ flex: 1, padding: '10px', fontSize: '16px', border: '1px solid #ccc', borderRadius: '4px 0 0 4px' }}
          />
          <button type="submit" style={{ padding: '10px 20px', fontSize: '16px', backgroundColor: '#1a73e8', color: '#fff', border: 'none', borderRadius: '0 4px 4px 0', cursor: 'pointer' }}>Search</button>
        </form>
      </div>
      <ButtonRibbon
        onResetDatabase={handleResetDatabase}
        onShowRestaurants={handleShowRestaurants}
        fetchGasStations={fetchGasStations}
        isLoadingGasStations={isLoadingGasStations}
      />
      <div style={{ display: 'flex', flex: 1, position: 'relative' }}>
        {isSidebarOpen && (
          <Sidebar
            currentLocation={currentLocation}
            savedLocations={savedLocations}
            onSave={handleSave}
            onDelete={handleDelete}
            isLocationSaved={isLocationSaved}
          />
        )}
        {isLoaded ? (
          <div style={{ flex: 1, height: '100%' }}>
            <GoogleMap
              center={mapCenter}
              zoom={mapZoom}
              onLoad={map => {
                console.log('Map loaded');
              }}
              mapContainerStyle={{ width: '100%', height: '100%' }}
            >
              {currentLocation && (
                <Marker
                  position={{ lat: Number(currentLocation.latitude), lng: Number(currentLocation.longitude) }}
                  title={currentLocation.name}
                />
              )}
              {savedLocations.map((location) => (
                <Marker
                  key={location.id}
                  position={{ lat: Number(location.latitude), lng: Number(location.longitude) }}
                  title={location.name}
                />
              ))}
              {restaurants.map((restaurant) => (
                <Marker
                  key={restaurant.id}
                  position={{ lat: Number(restaurant.latitude), lng: Number(restaurant.longitude) }}
                  title={restaurant.name}
                />
              ))}
              {gasStations.map((station) => {
                console.log('Rendering station:', station);
                return (
                  <Marker
                    key={station.id}
                    position={{ lat: Number(station.latitude), lng: Number(station.longitude) }}
                    title={station.name}
                    onClick={() => setSelectedStation(station)}
                  />
                );
              })}
              {selectedStation && (
                <InfoWindow
                  position={{ lat: Number(selectedStation.latitude), lng: Number(selectedStation.longitude) }}
                  onCloseClick={() => setSelectedStation(null)}
                >
                  <div>
                    <h3>{selectedStation.name}</h3>
                    <p>{selectedStation.address}</p>
                  </div>
                </InfoWindow>
              )}
            </GoogleMap>
          </div>
        ) : <div>Loading...</div>}
      </div>
    </div>
  );
}

export default App;