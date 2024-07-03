import React from 'react';

function Sidebar({ currentLocation, savedLocations, onSave, onDelete, isLocationSaved }) {
  return (
    <div style={{ width: '300px', height: '100%', overflowY: 'auto', backgroundColor: '#fff', boxShadow: '2px 0 5px rgba(0,0,0,0.1)', padding: '20px' }}>
      <h2>Google Maps Clone</h2>
      {currentLocation && (
        <div style={{ marginBottom: '20px' }}>
          <h3>Current Location:</h3>
          <p>Name: {currentLocation.name}</p>
          <p>Latitude: {currentLocation.latitude}</p>
          <p>Longitude: {currentLocation.longitude}</p>
          <button onClick={onSave} disabled={isLocationSaved} style={{ padding: '10px 20px', fontSize: '16px', backgroundColor: '#1a73e8', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Save Location
          </button>
        </div>
      )}
      <h3>Saved Locations</h3>
      {savedLocations.map((location) => (
        <div key={location.id} style={{ marginBottom: '10px', padding: '10px', border: '1px solid #ccc', borderRadius: '4px' }}>
          <p>{location.name}</p>
          <button onClick={() => onDelete(location.id)} style={{ padding: '5px 10px', fontSize: '12px', backgroundColor: '#f44336', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Delete
          </button>
        </div>
      ))}
    </div>
  );
}

export default Sidebar;