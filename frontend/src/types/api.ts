export interface Coordinates {
  lat: number;
  lng: number;
}

export interface TripRequest {
  pickup_latitude: number;
  pickup_longitude: number;
  dropoff_latitude: number;
  dropoff_longitude: number;
  passenger_count: number;
}

export interface PredictionResponse {
  fare: number;
  confidence: number;
  distance_miles: number;
  duration_minutes: number;
  pickup_borough: string;
  dropoff_borough: string;
  features: {
    [key: string]: number;
  };
  model_version: string;
  prediction_timestamp: string;
}

export interface ApiError {
  error: string;
  message: string;
  details?: any;
}

export interface HealthResponse {
  status: string;
  version: string;
  model_loaded: boolean;
  timestamp: string;
}

export interface MapMarker {
  position: Coordinates;
  type: 'pickup' | 'dropoff';
}
