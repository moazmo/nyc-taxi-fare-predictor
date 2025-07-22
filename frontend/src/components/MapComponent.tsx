import React, { useState, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Coordinates, MapMarker } from '../types/api';
import { isValidNYCCoordinates } from '../utils/helpers';

// Fix for default markers in react-leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icons for pickup and dropoff
const pickupIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="green" width="24px" height="24px">
      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

const dropoffIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="red" width="24px" height="24px">
      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

interface MapComponentProps {
  markers: MapMarker[];
  onMarkerAdd: (position: Coordinates, type: 'pickup' | 'dropoff') => void;
  onMarkerRemove: (type: 'pickup' | 'dropoff') => void;
}

const MapClickHandler: React.FC<{
  onMapClick: (position: Coordinates) => void;
}> = ({ onMapClick }) => {
  useMapEvents({
    click: (e) => {
      const { lat, lng } = e.latlng;
      onMapClick({ lat, lng });
    },
  });
  return null;
};

const MapComponent: React.FC<MapComponentProps> = ({
  markers,
  onMarkerAdd,
  onMarkerRemove,
}) => {
  const [clickMode, setClickMode] = useState<'pickup' | 'dropoff' | null>(null);

  const handleMapClick = useCallback((position: Coordinates) => {
    if (!clickMode) return;
    
    if (!isValidNYCCoordinates(position.lat, position.lng)) {
      alert('Please select a location within NYC bounds');
      return;
    }

    onMarkerAdd(position, clickMode);
    setClickMode(null);
  }, [clickMode, onMarkerAdd]);

  const nycCenter: Coordinates = { lat: 40.7128, lng: -74.0060 };

  return (
    <div className="map-container">
      <div className="map-controls">
        <button
          className={`control-btn ${clickMode === 'pickup' ? 'active' : ''}`}
          onClick={() => setClickMode(clickMode === 'pickup' ? null : 'pickup')}
        >
          📍 Set Pickup
        </button>
        <button
          className={`control-btn ${clickMode === 'dropoff' ? 'active' : ''}`}
          onClick={() => setClickMode(clickMode === 'dropoff' ? null : 'dropoff')}
        >
          🏁 Set Dropoff
        </button>
        <button
          className="control-btn clear"
          onClick={() => {
            onMarkerRemove('pickup');
            onMarkerRemove('dropoff');
            setClickMode(null);
          }}
        >
          🗑️ Clear All
        </button>
      </div>

      <div className="map-wrapper">
        <MapContainer
          center={[nycCenter.lat, nycCenter.lng]}
          zoom={11}
          style={{ height: '400px', width: '100%' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          
          <MapClickHandler onMapClick={handleMapClick} />
          
          {markers.map((marker, index) => (
            <Marker
              key={`${marker.type}-${index}`}
              position={[marker.position.lat, marker.position.lng]}
              icon={marker.type === 'pickup' ? pickupIcon : dropoffIcon}
            >
              <Popup>
                <div>
                  <strong>{marker.type === 'pickup' ? 'Pickup' : 'Dropoff'} Location</strong>
                  <br />
                  Lat: {marker.position.lat.toFixed(6)}
                  <br />
                  Lng: {marker.position.lng.toFixed(6)}
                  <br />
                  <button
                    onClick={() => onMarkerRemove(marker.type)}
                    style={{ marginTop: '5px', padding: '2px 8px' }}
                  >
                    Remove
                  </button>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {clickMode && (
        <div className="click-instruction">
          Click on the map to set {clickMode} location
        </div>
      )}
    </div>
  );
};

export default MapComponent;
