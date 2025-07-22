
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

class EnhancedTaxiFarePredictor:
    def __init__(self, model_dir="."):
        """Initialize the enhanced taxi fare predictor"""
        self.model_dir = model_dir
        
        # Load model and scaler
        self.model = joblib.load(f"{model_dir}/best_taxi_fare_model.pkl")
        self.scaler = joblib.load(f"{model_dir}/robust_scaler.pkl")
        
        # Load configuration
        with open(f"{model_dir}/model_config.json", 'r') as f:
            self.config = json.load(f)
        
        self.feature_names = self.config['web_app_features']
        
        # Check which log-transformed features are actually used
        self.has_log_distance = 'log_distance' in self.feature_names
        self.has_log_jfk = 'log_jfk_pickup_dist' in self.feature_names
        self.has_log_ewr = 'log_ewr_pickup_dist' in self.feature_names
        self.has_log_lga = 'log_lga_pickup_dist' in self.feature_names
        
        print(f"🔧 Enhanced Predictor initialized")
        print(f"📊 Model: {self.config['model_type']} ({self.config['model_class']})")
        print(f"📊 Features: {len(self.feature_names)}")
        print(f"📊 Expected RMSE: ±${self.config['performance_metrics']['test_rmse']:.2f}")
        print(f"🔧 Log features: distance={self.has_log_distance}, airports={self.has_log_jfk or self.has_log_ewr or self.has_log_lga}")
        
    def haversine_distance(self, lat1, lng1, lat2, lng2):
        """Calculate distance between two points using Haversine formula"""
        R = 3959  # Earth radius in miles
        lat1, lng1, lat2, lng2 = map(np.radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlng/2)**2
        return 2 * R * np.arcsin(np.sqrt(a))
    
    def validate_inputs(self, pickup_lng, pickup_lat, dropoff_lng, dropoff_lat, passenger_count):
        """Validate input parameters"""
        # NYC coordinate bounds
        nyc_bounds = {
            'min_lng': -74.3, 'max_lng': -73.7,
            'min_lat': 40.5, 'max_lat': 40.9
        }
        
        errors = []
        
        # Check coordinate bounds
        if not (nyc_bounds['min_lng'] <= pickup_lng <= nyc_bounds['max_lng']):
            errors.append(f"Pickup longitude {pickup_lng} outside NYC bounds")
        if not (nyc_bounds['min_lat'] <= pickup_lat <= nyc_bounds['max_lat']):
            errors.append(f"Pickup latitude {pickup_lat} outside NYC bounds")
        if not (nyc_bounds['min_lng'] <= dropoff_lng <= nyc_bounds['max_lng']):
            errors.append(f"Dropoff longitude {dropoff_lng} outside NYC bounds")
        if not (nyc_bounds['min_lat'] <= dropoff_lat <= nyc_bounds['max_lat']):
            errors.append(f"Dropoff latitude {dropoff_lat} outside NYC bounds")
        
        # Check passenger count
        if not (1 <= passenger_count <= 6):
            errors.append(f"Passenger count {passenger_count} must be between 1 and 6")
        
        # Check if pickup and dropoff are the same
        distance = self.haversine_distance(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng)
        if distance < 0.01:  # Less than 0.01 miles
            errors.append("Pickup and dropoff locations are too close")
        
        return errors
    
    def predict_fare(self, pickup_lng, pickup_lat, dropoff_lng, dropoff_lat, 
                    pickup_datetime, passenger_count=1, debug=False):
        """
        Predict taxi fare with enhanced feature engineering and validation
        """
        # Validate inputs
        validation_errors = self.validate_inputs(pickup_lng, pickup_lat, dropoff_lng, dropoff_lat, passenger_count)
        if validation_errors:
            raise ValueError(f"Input validation failed: {'; '.join(validation_errors)}")
        
        # Parse datetime
        if isinstance(pickup_datetime, str):
            pickup_datetime = pd.to_datetime(pickup_datetime)
        
        # Calculate basic distance
        distance = self.haversine_distance(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng)
        
        # Airport coordinates
        airports = {
            'jfk': (40.6413, -73.7781),
            'ewr': (40.6895, -74.1745),
            'lga': (40.7769, -73.8740)
        }
        
        # Manhattan center
        manhattan_center = (40.7589, -73.9851)
        
        # Calculate airport distances
        jfk_dist = self.haversine_distance(pickup_lat, pickup_lng, *airports['jfk'])
        ewr_dist = self.haversine_distance(pickup_lat, pickup_lng, *airports['ewr'])
        lga_dist = self.haversine_distance(pickup_lat, pickup_lng, *airports['lga'])
        
        # Create feature dictionary with base features
        features = {
            'pickup_longitude': pickup_lng,
            'pickup_latitude': pickup_lat,
            'dropoff_longitude': dropoff_lng,
            'dropoff_latitude': dropoff_lat,
            'passenger_count': passenger_count,
            'hour': pickup_datetime.hour,
            'day': pickup_datetime.day,
            'month': pickup_datetime.month,
            'weekday': pickup_datetime.weekday(),
            'year': pickup_datetime.year,
            'distance': distance,
            'jfk_pickup_dist': jfk_dist,
            'ewr_pickup_dist': ewr_dist,
            'lga_pickup_dist': lga_dist,
            'is_weekend': int(pickup_datetime.weekday() >= 5),
            'is_rush_hour': int(pickup_datetime.hour in [7, 8, 9, 17, 18, 19]),
            'is_night': int(pickup_datetime.hour >= 22 or pickup_datetime.hour <= 6),
            'manhattan_pickup_dist': self.haversine_distance(pickup_lat, pickup_lng, *manhattan_center),
            'is_manhattan_pickup': int((40.7 <= pickup_lat <= 40.8) and (-74.02 <= pickup_lng <= -73.93)),
            'is_manhattan_dropoff': int((40.7 <= dropoff_lat <= 40.8) and (-74.02 <= dropoff_lng <= -73.93))
        }
        
        # Add log-transformed features only if they exist in the model
        if self.has_log_distance:
            features['log_distance'] = np.log1p(distance)
        
        if self.has_log_jfk:
            features['log_jfk_pickup_dist'] = np.log1p(jfk_dist)
        
        if self.has_log_ewr:
            features['log_ewr_pickup_dist'] = np.log1p(ewr_dist)
        
        if self.has_log_lga:
            features['log_lga_pickup_dist'] = np.log1p(lga_dist)
        
        # Create DataFrame with only the features that exist in the model
        available_features = {k: v for k, v in features.items() if k in self.feature_names}
        X = pd.DataFrame([available_features])[self.feature_names]
        
        if debug:
            print(f"🔍 Input features shape: {X.shape}")
            print(f"📊 Feature names: {list(X.columns)}")
            print(f"📊 Sample values: {X.values[0][:5]}")
            print(f"📊 Distance: {distance:.2f} miles")
            print(f"🔧 Log features included: {[col for col in X.columns if col.startswith('log_')]}")
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        if debug:
            print(f"🔧 Scaled features shape: {X_scaled.shape}")
            print(f"📊 Sample scaled values: {X_scaled[0][:5]}")
        
        # Make prediction
        prediction = self.model.predict(X_scaled)[0]
        
        # Apply business logic validation
        validated_prediction = self.validate_prediction(prediction, distance, features)
        
        if debug:
            print(f"🎯 Raw prediction: ${prediction:.2f}")
            print(f"🎯 Validated prediction: ${validated_prediction:.2f}")
        
        return validated_prediction
    
    def validate_prediction(self, prediction, distance, features):
        """Apply business logic validation to predictions"""
        # NYC taxi base fare and per-mile rates
        base_fare = 2.50  # NYC base fare
        base_rate_per_mile = 2.50
        
        # Time-based multipliers
        multiplier = 1.0
        if features['is_rush_hour']:
            multiplier *= 1.2  # 20% surge for rush hour
        if features['is_night']:
            multiplier *= 1.3  # 30% surge for night
        if features['is_weekend'] and features['is_night']:
            multiplier *= 1.4  # 40% surge for weekend nights
        
        # Airport surcharge
        airport_threshold = 2.0  # Within 2 miles of airport
        is_airport_trip = (
            features['jfk_pickup_dist'] < airport_threshold or
            features['ewr_pickup_dist'] < airport_threshold or
            features['lga_pickup_dist'] < airport_threshold
        )
        if is_airport_trip:
            base_rate_per_mile *= 1.5  # 50% higher rate for airport trips
        
        # Calculate expected fare range
        min_expected = base_fare + (distance * base_rate_per_mile * multiplier)
        max_expected = min_expected * 2.5  # Allow for surge pricing
        
        # If prediction is way off, use business logic estimate
        if prediction < min_expected * 0.5:
            return min_expected
        elif prediction > max_expected:
            return max_expected
        else:
            return prediction
    
    def get_prediction_confidence(self, prediction, distance):
        """Get confidence level for prediction"""
        expected_rmse = self.config['performance_metrics']['test_rmse']
        
        # Confidence decreases with distance and extreme fares
        confidence = 1.0
        
        if distance > 20:  # Very long trips are less reliable
            confidence *= 0.8
        elif distance < 0.5:  # Very short trips might have flat rates
            confidence *= 0.9
        
        if prediction > 100:  # Very expensive trips
            confidence *= 0.7
        elif prediction < 5:  # Very cheap trips
            confidence *= 0.8
        
        return {
            'confidence': min(confidence, 1.0),
            'expected_error': f"±${expected_rmse:.2f}",
            'confidence_interval': [
                max(0, prediction - expected_rmse * (2 - confidence)),
                prediction + expected_rmse * (2 - confidence)
            ]
        }

# Example usage:
# predictor = EnhancedTaxiFarePredictor("taxi_fare_model_deployment")
# fare = predictor.predict_fare(-73.986, 40.748, -73.959, 40.783, "2023-12-15 14:30:00", 2)
# confidence = predictor.get_prediction_confidence(fare, 2.5)
# print(f"Predicted fare: ${fare:.2f} (confidence: {confidence['confidence']:.1%})")
