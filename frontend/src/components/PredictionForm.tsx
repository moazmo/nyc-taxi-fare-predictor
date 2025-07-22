import React, { useState } from 'react';
import { TripRequest, PredictionResponse } from '../types/api';
import { formatCurrency, formatDistance, formatDuration, formatConfidence, getConfidenceColor } from '../utils/helpers';

interface PredictionFormProps {
  pickupLocation: { lat: number; lng: number } | null;
  dropoffLocation: { lat: number; lng: number } | null;
  onPredict: (tripData: TripRequest) => Promise<PredictionResponse>;
  loading: boolean;
}

const PredictionForm: React.FC<PredictionFormProps> = ({
  pickupLocation,
  dropoffLocation,
  onPredict,
  loading,
}) => {
  const [passengerCount, setPassengerCount] = useState(1);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async () => {
    if (!pickupLocation || !dropoffLocation) {
      setError('Please set both pickup and dropoff locations on the map');
      return;
    }

    setError(null);
    setPrediction(null);

    try {
      const tripData: TripRequest = {
        pickup_latitude: pickupLocation.lat,
        pickup_longitude: pickupLocation.lng,
        dropoff_latitude: dropoffLocation.lat,
        dropoff_longitude: dropoffLocation.lng,
        passenger_count: passengerCount,
      };

      const result = await onPredict(tripData);
      setPrediction(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Prediction failed');
    }
  };

  const canPredict = pickupLocation && dropoffLocation && !loading;

  return (
    <div className="prediction-form">
      <div className="form-section">
        <h3>Trip Details</h3>
        
        <div className="form-group">
          <label htmlFor="passenger-count">Passenger Count:</label>
          <select
            id="passenger-count"
            value={passengerCount}
            onChange={(e) => setPassengerCount(Number(e.target.value))}
          >
            {[1, 2, 3, 4, 5, 6].map((count) => (
              <option key={count} value={count}>
                {count} passenger{count > 1 ? 's' : ''}
              </option>
            ))}
          </select>
        </div>

        <div className="location-status">
          <div className={`status-item ${pickupLocation ? 'set' : 'unset'}`}>
            <span className="status-icon">{pickupLocation ? '✅' : '❌'}</span>
            <span>Pickup Location</span>
            {pickupLocation && (
              <span className="coordinates">
                ({pickupLocation.lat.toFixed(4)}, {pickupLocation.lng.toFixed(4)})
              </span>
            )}
          </div>
          
          <div className={`status-item ${dropoffLocation ? 'set' : 'unset'}`}>
            <span className="status-icon">{dropoffLocation ? '✅' : '❌'}</span>
            <span>Dropoff Location</span>
            {dropoffLocation && (
              <span className="coordinates">
                ({dropoffLocation.lat.toFixed(4)}, {dropoffLocation.lng.toFixed(4)})
              </span>
            )}
          </div>
        </div>

        <button
          className="predict-btn"
          onClick={handlePredict}
          disabled={!canPredict}
        >
          {loading ? 'Predicting...' : '🚖 Predict Fare'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      {prediction && (
        <div className="prediction-result">
          <h3>Fare Prediction</h3>
          
          <div className="main-result">
            <div className="fare-amount">
              {formatCurrency(prediction.fare)}
            </div>
            <div 
              className="confidence"
              style={{ color: getConfidenceColor(prediction.confidence) }}
            >
              Confidence: {formatConfidence(prediction.confidence)}
            </div>
          </div>

          <div className="trip-details">
            <div className="detail-item">
              <span className="label">Distance:</span>
              <span className="value">{formatDistance(prediction.distance_miles)}</span>
            </div>
            <div className="detail-item">
              <span className="label">Duration:</span>
              <span className="value">{formatDuration(prediction.duration_minutes)}</span>
            </div>
            <div className="detail-item">
              <span className="label">From:</span>
              <span className="value">{prediction.pickup_borough}</span>
            </div>
            <div className="detail-item">
              <span className="label">To:</span>
              <span className="value">{prediction.dropoff_borough}</span>
            </div>
          </div>

          <div className="model-info">
            <small>
              Model: {prediction.model_version} | 
              Generated: {new Date(prediction.prediction_timestamp).toLocaleTimeString()}
            </small>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictionForm;
