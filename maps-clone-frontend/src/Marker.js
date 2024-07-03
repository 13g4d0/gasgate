import React from 'react';

const Marker = ({ text }) => {
  return (
    <div style={{
      position: 'absolute',
      transform: 'translate(-50%, -100%)',
      color: 'white', 
      background: 'red',
      padding: '5px 10px',
      display: 'inline-flex',
      textAlign: 'center',
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: '4px',
      fontWeight: 'bold',
      fontSize: '14px',
      boxShadow: '0 2px 5px rgba(0,0,0,0.3)'
    }}>
      {text}
      <div style={{
        position: 'absolute',
        bottom: '-8px',
        left: '50%',
        transform: 'translateX(-50%)',
        width: 0,
        height: 0,
        borderLeft: '8px solid transparent',
        borderRight: '8px solid transparent',
        borderTop: '8px solid red'
      }} />
    </div>
  );
};

export default Marker;