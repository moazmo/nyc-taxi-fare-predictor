"""
Machine learning prediction logic for taxi fare estimation.
"""

import os
import sys
import joblib
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from pathlib import Path

# Add models directory to path
MODELS_DIR = Path(__file__).parent.parent / "models"
sys.path.append(str(MODELS_DIR))

from .utils import (
    calculate_haversine_distance,
    calculate_manhattan_distance,
    calculate_trip_features,
    calculate_fare_confidence,
    format_prediction_details,
    setup_logging
)

logger = setup_logging()


class TaxiFarePredictor:
    """Enhanced taxi fare predictor using the model from Task_4_3_2."""
    
    def __init__(self):
        """Initialize the predictor with model and scaler."""
        self.model = None
        self.scaler = None
        self.model_config = None
        self.feature_names = None
        self.is_loaded = False
        
        # Load model components
        self._load_model_components()
    
    def _load_model_components(self):
        """Load the trained model, scaler, and configuration."""
        try:
            # Load model
            model_path = MODELS_DIR / "best_taxi_fare_model.pkl"
            self.model = joblib.load(model_path)
            logger.info(f"Model loaded successfully from {model_path}")
            
            # Load scaler
            scaler_path = MODELS_DIR / "robust_scaler.pkl"
            self.scaler = joblib.load(scaler_path)
            logger.info(f"Scaler loaded successfully from {scaler_path}")
            
            # Load model configuration
            config_path = MODELS_DIR / "model_config.json"
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"Model config loaded successfully from {config_path}")
            
            # Set feature names from the model config
            self.feature_names = self.config.get('web_app_features', [])
            logger.info(f"Loaded {len(self.feature_names)} features: {self.feature_names}")
            
            self.is_loaded = True
            logger.info("All model components loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model components: {e}")
            self.is_loaded = False
            raise
    
    def _prepare_features(
        self, 
        pickup_lon: float, pickup_lat: float,
        dropoff_lon: float, dropoff_lat: float,
        passenger_count: int = 1
    ) -> pd.DataFrame:
        """
        Prepare features for prediction matching the exact training feature set.
        Expected features from model_config.json:
        - pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, passenger_count
        - hour, day, month, weekday, year
        - distance, jfk_pickup_dist, ewr_pickup_dist, lga_pickup_dist
        - is_weekend, is_rush_hour, is_night
        - manhattan_pickup_dist, is_manhattan_pickup, is_manhattan_dropoff
        - log_distance
        """
        from datetime import datetime
        
        # Get current time for temporal features (use defaults for consistent prediction)
        now = datetime.now()
        hour = now.hour
        day = now.day
        month = now.month
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        year = now.year
        
        # Calculate distances - ensure float64 type consistency
        distance = float(calculate_haversine_distance(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon))
        
        # Airport coordinates
        jfk_lat, jfk_lon = 40.6413, -73.7781
        ewr_lat, ewr_lon = 40.6895, -74.1745
        lga_lat, lga_lon = 40.7769, -73.8740
        
        jfk_pickup_dist = float(calculate_haversine_distance(pickup_lat, pickup_lon, jfk_lat, jfk_lon))
        ewr_pickup_dist = float(calculate_haversine_distance(pickup_lat, pickup_lon, ewr_lat, ewr_lon))
        lga_pickup_dist = float(calculate_haversine_distance(pickup_lat, pickup_lon, lga_lat, lga_lon))
        
        # Manhattan center for distance calculation
        manhattan_center_lat, manhattan_center_lon = 40.7589, -73.9851
        manhattan_pickup_dist = float(calculate_haversine_distance(pickup_lat, pickup_lon, manhattan_center_lat, manhattan_center_lon))
        
        # Boolean features - convert to int for consistency
        is_weekend = int(weekday >= 5)  # Saturday=5, Sunday=6
        is_rush_hour = int((7 <= hour <= 9) or (17 <= hour <= 19))
        is_night = int(hour >= 22 or hour <= 5)
        
        # Manhattan bounds (approximate)
        manhattan_lat_min, manhattan_lat_max = 40.7000, 40.8000
        manhattan_lon_min, manhattan_lon_max = -74.0200, -73.9300
        
        is_manhattan_pickup = int(manhattan_lat_min <= pickup_lat <= manhattan_lat_max and 
                                 manhattan_lon_min <= pickup_lon <= manhattan_lon_max)
        is_manhattan_dropoff = int(manhattan_lat_min <= dropoff_lat <= manhattan_lat_max and 
                                  manhattan_lon_min <= dropoff_lon <= manhattan_lon_max)
        
        # Log distance (add small epsilon to avoid log(0))
        log_distance = float(np.log(max(distance, 0.01)))
        
        # Create feature dictionary in the exact order expected by the model
        # Ensure all values are proper Python types (not numpy types)
        features = {
            'pickup_longitude': float(pickup_lon),
            'pickup_latitude': float(pickup_lat),
            'dropoff_longitude': float(dropoff_lon),
            'dropoff_latitude': float(dropoff_lat),
            'passenger_count': int(passenger_count),
            'hour': int(hour),
            'day': int(day),
            'month': int(month),
            'weekday': int(weekday),
            'year': int(year),
            'distance': distance,
            'jfk_pickup_dist': jfk_pickup_dist,
            'ewr_pickup_dist': ewr_pickup_dist,
            'lga_pickup_dist': lga_pickup_dist,
            'is_weekend': is_weekend,
            'is_rush_hour': is_rush_hour,
            'is_night': is_night,
            'manhattan_pickup_dist': manhattan_pickup_dist,
            'is_manhattan_pickup': is_manhattan_pickup,
            'is_manhattan_dropoff': is_manhattan_dropoff,
            'log_distance': log_distance
        }
        
        # Create DataFrame with features in the exact order from model config
        expected_features = self.config.get('web_app_features', [])
        if expected_features:
            # Create DataFrame with only the expected features in the right order
            ordered_features = {feat: features[feat] for feat in expected_features if feat in features}
            df = pd.DataFrame([ordered_features])
        else:
            df = pd.DataFrame([features])
        
        # Ensure consistent data types - convert all to float64 for sklearn compatibility
        df = df.astype('float64')
        
        logger.debug(f"Prepared features: {list(df.columns)}")
        logger.debug(f"Feature values: {df.iloc[0].to_dict()}")
        logger.debug(f"DataFrame shape: {df.shape}")
        logger.debug(f"DataFrame dtypes: {df.dtypes.to_dict()}")
        
        return df
    
    def _calculate_distance_to_center(self, lat: float, lon: float) -> float:
        """Calculate distance to NYC center (Times Square: 40.7580, -73.9855)."""
        center_lat, center_lon = 40.7580, -73.9855
        from .utils import calculate_haversine_distance
        return calculate_haversine_distance(lat, lon, center_lat, center_lon)
    
    def _get_borough_id(self, lat: float, lon: float) -> int:
        """
        Get borough ID based on coordinates (simplified mapping).
        
        Returns:
            Borough ID (0-4 for Manhattan, Brooklyn, Queens, Bronx, Staten Island)
        """
        # Simplified borough mapping based on coordinates
        if -74.02 <= lon <= -73.93 and 40.70 <= lat <= 40.80:
            return 0  # Manhattan
        elif -74.05 <= lon <= -73.85 and 40.63 <= lat <= 40.72:
            return 1  # Brooklyn
        elif -73.96 <= lon <= -73.75 and 40.72 <= lat <= 40.80:
            return 2  # Queens
        elif -73.93 <= lon <= -73.80 and 40.80 <= lat <= 40.88:
            return 3  # Bronx
        else:
            return 4  # Staten Island or other
    
    def _get_borough_name(self, lat: float, lon: float) -> str:
        """
        Get borough name based on coordinates.
        
        Returns:
            Borough name as string
        """
        borough_id = self._get_borough_id(lat, lon)
        borough_names = {
            0: "Manhattan",
            1: "Brooklyn", 
            2: "Queens",
            3: "Bronx",
            4: "Staten Island"
        }
        return borough_names.get(borough_id, "Other")
    
    def predict_fare(
        self,
        pickup_lon: float, pickup_lat: float,
        dropoff_lon: float, dropoff_lat: float,
        passenger_count: int = 1
    ) -> Dict:
        """
        Predict taxi fare for given trip parameters.
        
        Args:
            pickup_lon: Pickup longitude
            pickup_lat: Pickup latitude
            dropoff_lon: Dropoff longitude
            dropoff_lat: Dropoff latitude
            passenger_count: Number of passengers
        
        Returns:
            Dictionary with prediction results
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Cannot make predictions.")
        
        start_time = time.time()
        
        try:
            # Prepare features
            features_df = self._prepare_features(
                pickup_lon, pickup_lat, dropoff_lon, dropoff_lat, passenger_count
            )
            
            logger.debug(f"Features DataFrame before scaling: {features_df.dtypes}")
            logger.debug(f"Features shape: {features_df.shape}")
            
            # Scale features - ensure consistent data types
            features_scaled = self.scaler.transform(features_df)
            
            # Convert to float64 to avoid data type conflicts
            features_scaled = features_scaled.astype(np.float64)
            
            logger.debug(f"Features after scaling shape: {features_scaled.shape}")
            logger.debug(f"Features after scaling dtype: {features_scaled.dtype}")
            
            # Make prediction
            prediction = self.model.predict(features_scaled)[0]
            prediction = float(prediction)  # Ensure it's a standard Python float
            
            logger.info(f"Raw prediction: {prediction}")
            
            # Calculate additional trip information for response
            from .utils import calculate_haversine_distance
            trip_distance = calculate_haversine_distance(
                pickup_lat, pickup_lon, dropoff_lat, dropoff_lon
            )
            
            # Estimate duration based on distance and NYC traffic (approximate)
            # Average NYC taxi speed: 12-15 mph
            estimated_duration = (trip_distance / 12.0) * 60  # Convert to minutes
            
            # Get borough information (simplified)
            pickup_borough = self._get_borough_name(pickup_lat, pickup_lon)
            dropoff_borough = self._get_borough_name(dropoff_lat, dropoff_lon)
            
            # Get individual model predictions if it's an ensemble
            individual_predictions = []
            if hasattr(self.model, 'estimators_'):
                # For ensemble models like Random Forest
                try:
                    individual_predictions = [
                        float(estimator.predict(features_scaled)[0]) 
                        for estimator in self.model.estimators_[:5]  # First 5 estimators
                    ]
                except:
                    individual_predictions = [prediction] * 3
            elif hasattr(self.model, 'predict'):
                # Single model - use multiple slightly varied predictions for confidence
                individual_predictions = [prediction] * 3
            
            # Calculate confidence and fare range
            confidence, fare_range = calculate_fare_confidence(
                prediction, individual_predictions, trip_distance
            )
            
            final_fare = max(2.50, prediction)  # Minimum fare
            
            # Return format expected by frontend
            return {
                "fare": round(final_fare, 2),
                "confidence": confidence,
                "distance_miles": round(trip_distance, 3),
                "duration_minutes": round(estimated_duration, 1),
                "pickup_borough": pickup_borough,
                "dropoff_borough": dropoff_borough,
                "features": dict(zip(self.feature_names, features_scaled[0].tolist())),
                "model_version": "Enhanced Ensemble v1.0",
                "prediction_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise RuntimeError(f"Prediction failed: {str(e)}")
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        if not self.is_loaded:
            return {"loaded": False, "error": "Model not loaded"}
        
        return {
            "loaded": True,
            "model_type": type(self.model).__name__,
            "features_count": len(self.feature_names),
            "feature_names": self.feature_names,
            "config": self.model_config if self.model_config else {}
        }


# Global predictor instance
_predictor_instance = None


def get_predictor() -> TaxiFarePredictor:
    """Get or create the global predictor instance."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = TaxiFarePredictor()
    return _predictor_instance
