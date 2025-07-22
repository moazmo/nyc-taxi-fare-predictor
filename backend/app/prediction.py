"""
Machine learning prediction logic for taxi fare estimation.
"""

import os
import sys
import pickle
import json
import logging
import time
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from pathlib import Path

# Add models directory to path
MODELS_DIR = Path(__file__).parent.parent / "models"
sys.path.append(str(MODELS_DIR))

from .utils import (
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
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"Model loaded successfully from {model_path}")
            
            # Load scaler
            scaler_path = MODELS_DIR / "robust_scaler.pkl"
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info(f"Scaler loaded successfully from {scaler_path}")
            
            # Load model configuration
            config_path = MODELS_DIR / "model_config.json"
            with open(config_path, 'r') as f:
                self.model_config = json.load(f)
            logger.info(f"Model config loaded successfully from {config_path}")
            
            # Set feature names (from the enhanced model)
            self.feature_names = [
                'pickup_longitude', 'pickup_latitude', 'dropoff_longitude',
                'dropoff_latitude', 'passenger_count', 'trip_distance',
                'trip_duration_estimated', 'haversine_distance', 'manhattan_distance',
                'bearing', 'pickup_hour', 'pickup_day_of_week', 'pickup_month',
                'is_weekend', 'distance_to_center', 'pickup_borough', 'dropoff_borough'
            ]
            
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
        Prepare features for prediction based on the enhanced model structure.
        
        Args:
            pickup_lon: Pickup longitude
            pickup_lat: Pickup latitude
            dropoff_lon: Dropoff longitude
            dropoff_lat: Dropoff latitude
            passenger_count: Number of passengers
        
        Returns:
            DataFrame with prepared features
        """
        # Calculate basic trip features
        trip_features = calculate_trip_features(
            pickup_lat, pickup_lon, dropoff_lat, dropoff_lon, passenger_count
        )
        
        # Create feature dictionary
        features = {
            'pickup_longitude': pickup_lon,
            'pickup_latitude': pickup_lat,
            'dropoff_longitude': dropoff_lon,
            'dropoff_latitude': dropoff_lat,
            'passenger_count': passenger_count,
            'trip_distance': trip_features['haversine_distance'],
            'trip_duration_estimated': trip_features['haversine_distance'] * 4.5,  # Estimated minutes
            'haversine_distance': trip_features['haversine_distance'],
            'manhattan_distance': trip_features['manhattan_distance'],
            'bearing': trip_features['bearing'],
            'pickup_hour': 12,  # Default to noon
            'pickup_day_of_week': 2,  # Default to Tuesday
            'pickup_month': 6,  # Default to June
            'is_weekend': 0,  # Default to weekday
            'distance_to_center': self._calculate_distance_to_center(pickup_lat, pickup_lon),
            'pickup_borough': self._get_borough_id(pickup_lat, pickup_lon),
            'dropoff_borough': self._get_borough_id(dropoff_lat, dropoff_lon)
        }
        
        # Create DataFrame with correct feature order
        df = pd.DataFrame([features])
        
        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in df.columns:
                df[feature] = 0  # Default value for missing features
        
        # Reorder columns to match training data
        df = df[self.feature_names]
        
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
            
            # Scale features
            features_scaled = self.scaler.transform(features_df)
            
            # Make prediction
            prediction = self.model.predict(features_scaled)[0]
            
            # Calculate trip distance for response
            from .utils import calculate_haversine_distance
            trip_distance = calculate_haversine_distance(
                pickup_lat, pickup_lon, dropoff_lat, dropoff_lon
            )
            
            # Get individual model predictions if it's an ensemble
            individual_predictions = []
            if hasattr(self.model, 'estimators_'):
                # For ensemble models like Random Forest
                individual_predictions = [
                    estimator.predict(features_scaled)[0] 
                    for estimator in self.model.estimators_[:5]  # First 5 estimators
                ]
            elif hasattr(self.model, 'predict'):
                # Single model - use multiple slightly varied predictions for confidence
                individual_predictions = [prediction] * 3
            
            # Calculate confidence and fare range
            confidence, fare_range = calculate_fare_confidence(
                prediction, individual_predictions, trip_distance
            )
            
            # Format prediction details
            processing_time = time.time() - start_time
            details = format_prediction_details(
                model_type="ensemble" if hasattr(self.model, 'estimators_') else "single",
                features_count=len(self.feature_names),
                trip_distance=trip_distance,
                processing_time=processing_time
            )
            
            return {
                "predicted_fare": round(max(2.50, prediction), 2),  # Minimum fare
                "confidence_score": confidence,
                "fare_range": fare_range,
                "trip_distance": round(trip_distance, 3),
                "prediction_details": details
            }
            
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
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
