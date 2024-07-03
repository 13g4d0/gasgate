import React from 'react';

function ButtonRibbon({ onResetDatabase, onShowRestaurants, fetchGasStations, isLoadingGasStations }) {
  return (
    <div style={{ padding: '10px', backgroundColor: '#f1f3f4', display: 'flex', justifyContent: 'flex-start', alignItems: 'center', overflowX: 'auto' }}>
      <button 
        onClick={onResetDatabase} 
        style={{ 
          padding: '8px 16px', 
          fontSize: '14px', 
          backgroundColor: '#e91e63', 
          color: '#fff', 
          border: 'none', 
          borderRadius: '4px', 
          cursor: 'pointer', 
          marginRight: '10px' }}
      >
        Reset Database
      </button>
      <button 
        onClick={onShowRestaurants} 
        style={{ 
          padding: '8px 16px', 
          fontSize: '14px', 
          backgroundColor: '#4CAF50', 
          color: '#fff', 
          border: 'none', 
          borderRadius: '4px', 
          cursor: 'pointer', 
          marginRight: '10px' 
        }}
      >
        Restaurants
      </button>
      <button 
        onClick={fetchGasStations} 
        disabled={isLoadingGasStations}
        style={{ 
          padding: '8px 16px', 
          fontSize: '14px', 
          backgroundColor: isLoadingGasStations ? '#cccccc' : '#4CAF50', 
          color: '#fff', 
          border: 'none', 
          borderRadius: '4px', 
          cursor: isLoadingGasStations ? 'not-allowed' : 'pointer', 
          marginRight: '10px' 
        }}
      >
        {isLoadingGasStations ? 'Loading...' : 'Show Gas Stations'}
      </button>
    </div>
  );
}

export default ButtonRibbon;