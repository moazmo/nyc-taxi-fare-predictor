import React, { useState, useEffect } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import MapComponent from './components/MapComponent';
import PredictionForm from './components/PredictionForm';
import { Coordinates, MapMarker, TripRequest, PredictionResponse, HealthResponse } from './types/api';
import { predictFare, checkHealth } from './utils/api';
import './App.css';

const App: React.FC = () => {
  const [markers, setMarkers] = useState<MapMarker[]>([]);
  const [pickupLocation, setPickupLocation] = useState<Coordinates | null>(null);
  const [dropoffLocation, setDropoffLocation] = useState<Coordinates | null>(null);
  const [loading, setLoading] = useState(false);
  const [apiHealth, setApiHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    // Check API health on mount
    const checkApiHealth = async () => {
      try {
        const health = await checkHealth();
        setApiHealth(health);
        if (health.status === 'healthy') {
          toast.success('API connected successfully');
        } else {
          toast.error('API is not ready');
        }
      } catch (error) {
        toast.error('Failed to connect to API');
        console.error('Health check failed:', error);
      }
    };

    checkApiHealth();
  }, []);

  const handleMarkerAdd = (position: Coordinates, type: 'pickup' | 'dropoff') => {
    const newMarker: MapMarker = { position, type };
    
    if (type === 'pickup') {
      setPickupLocation(position);
      setMarkers(prev => [
        ...prev.filter(m => m.type !== 'pickup'),
        newMarker
      ]);
      toast.success('Pickup location set');
    } else {
      setDropoffLocation(position);
      setMarkers(prev => [
        ...prev.filter(m => m.type !== 'dropoff'),
        newMarker
      ]);
      toast.success('Dropoff location set');
    }
  };

  const handleMarkerRemove = (type: 'pickup' | 'dropoff') => {
    if (type === 'pickup') {
      setPickupLocation(null);
      toast.success('Pickup location removed');
    } else {
      setDropoffLocation(null);
      toast.success('Dropoff location removed');
    }
    
    setMarkers(prev => prev.filter(m => m.type !== type));
  };

  const handlePredict = async (tripData: TripRequest): Promise<PredictionResponse> => {
    setLoading(true);
    try {
      const result = await predictFare(tripData);
      toast.success('Fare predicted successfully');
      return result;
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Prediction failed');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🚖 NYC Taxi Fare Predictor</h1>
        <div className="api-status">
          {apiHealth ? (
            <span className={`status ${apiHealth.status}`}>
              {apiHealth.status === 'healthy' ? '🟢' : '🔴'} API {apiHealth.status}
            </span>
          ) : (
            <span className="status loading">🟡 Checking API...</span>
          )}
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          <div className="instructions">
            <p>
              Select pickup and dropoff locations on the map, choose passenger count, 
              and get an AI-powered fare prediction for your NYC taxi trip.
            </p>
          </div>

          <div className="app-content">
            <div className="map-section">
              <h2>📍 Select Locations</h2>
              <MapComponent
                markers={markers}
                onMarkerAdd={handleMarkerAdd}
                onMarkerRemove={handleMarkerRemove}
              />
            </div>

            <div className="prediction-section">
              <h2>💰 Get Fare Prediction</h2>
              <PredictionForm
                pickupLocation={pickupLocation}
                dropoffLocation={dropoffLocation}
                onPredict={handlePredict}
                loading={loading}
              />
            </div>
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <p>Powered by Enhanced ML Model with Ensemble Learning</p>
      </footer>

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
    </div>
  );
};

export default App;
