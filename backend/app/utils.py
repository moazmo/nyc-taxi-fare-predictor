"""
Utility functions for the taxi fare prediction API.
"""

import math
import logging
from datetime import datetime
from typing import Tuple


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def calculate_haversine_distance(
    pickup_lat: float, pickup_lon: float,
    dropoff_lat: float, dropoff_lon: float
) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees).
    
    Returns distance in miles.
    """
    # Convert decimal degrees to radians
    pickup_lat, pickup_lon, dropoff_lat, dropoff_lon = map(
        math.radians, [pickup_lat, pickup_lon, dropoff_lat, dropoff_lon]
    )
    
    # Haversine formula
    dlat = dropoff_lat - pickup_lat
    dlon = dropoff_lon - pickup_lon
    a = (math.sin(dlat/2)**2 + 
         math.cos(pickup_lat) * math.cos(dropoff_lat) * math.sin(dlon/2)**2)
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in miles
    r = 3956
    
    return c * r


def calculate_manhattan_distance(
    pickup_lat: float, pickup_lon: float,
    dropoff_lat: float, dropoff_lon: float
) -> float:
    """
    Calculate Manhattan distance in miles.
    """
    lat_dist = abs(pickup_lat - dropoff_lat) * 69  # Approximate miles per degree latitude
    lon_dist = abs(pickup_lon - dropoff_lon) * 54.6  # Approximate miles per degree longitude in NYC
    return lat_dist + lon_dist


def validate_nyc_coordinates(lat: float, lon: float) -> bool:
    """
    Validate if coordinates are within NYC bounds.
    
    NYC approximate bounds:
    - Latitude: 40.63 to 40.85
    - Longitude: -74.05 to -73.75
    """
    return (40.63 <= lat <= 40.85) and (-74.05 <= lon <= -73.75)


def calculate_fare_confidence(
    prediction: float,
    model_predictions: list,
    trip_distance: float
) -> Tuple[float, dict]:
    """
    Calculate confidence score and fare range based on model predictions.
    
    Args:
        prediction: Main prediction value
        model_predictions: List of predictions from different models
        trip_distance: Calculated trip distance
    
    Returns:
        Tuple of (confidence_score, fare_range_dict)
    """
    if not model_predictions or len(model_predictions) < 2:
        # Default confidence for single model
        confidence = 0.7
        margin = prediction * 0.2
        fare_range = {
            "min": max(2.50, prediction - margin),  # Minimum fare
            "max": prediction + margin
        }
        return confidence, fare_range
    
    # Calculate standard deviation of predictions
    import statistics
    std_dev = statistics.stdev(model_predictions)
    mean_pred = statistics.mean(model_predictions)
    
    # Confidence based on prediction consistency
    # Lower std_dev = higher confidence
    relative_std = std_dev / mean_pred if mean_pred > 0 else 1.0
    confidence = max(0.1, min(0.95, 1.0 - (relative_std * 2)))
    
    # Fare range based on standard deviation
    margin = std_dev * 1.5
    fare_range = {
        "min": max(2.50, prediction - margin),
        "max": prediction + margin
    }
    
    return round(confidence, 3), {
        "min": round(fare_range["min"], 2),
        "max": round(fare_range["max"], 2)
    }


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


def format_prediction_details(
    model_type: str,
    features_count: int,
    trip_distance: float,
    processing_time: float = None
) -> dict:
    """
    Format prediction details for response.
    
    Args:
        model_type: Type of model used
        features_count: Number of features used
        trip_distance: Calculated trip distance
        processing_time: Time taken for prediction (optional)
    
    Returns:
        Dictionary with prediction details
    """
    details = {
        "model_used": model_type,
        "features_used": features_count,
        "trip_distance_miles": round(trip_distance, 3),
        "prediction_time": get_current_timestamp()
    }
    
    if processing_time is not None:
        details["processing_time_ms"] = round(processing_time * 1000, 2)
    
    return details


def validate_passenger_count(count: int) -> bool:
    """Validate passenger count is reasonable."""
    return 1 <= count <= 6


def calculate_trip_features(
    pickup_lat: float, pickup_lon: float,
    dropoff_lat: float, dropoff_lon: float,
    passenger_count: int = 1
) -> dict:
    """
    Calculate all trip-related features for prediction.
    
    Returns:
        Dictionary with calculated features
    """
    haversine_dist = calculate_haversine_distance(
        pickup_lat, pickup_lon, dropoff_lat, dropoff_lon
    )
    manhattan_dist = calculate_manhattan_distance(
        pickup_lat, pickup_lon, dropoff_lat, dropoff_lon
    )
    
    # Additional feature calculations
    lat_diff = abs(pickup_lat - dropoff_lat)
    lon_diff = abs(pickup_lon - dropoff_lon)
    
    # Direction features
    bearing = math.atan2(
        dropoff_lon - pickup_lon,
        dropoff_lat - pickup_lat
    )
    
    return {
        "haversine_distance": haversine_dist,
        "manhattan_distance": manhattan_dist,
        "latitude_difference": lat_diff,
        "longitude_difference": lon_diff,
        "bearing": bearing,
        "passenger_count": passenger_count,
        "pickup_latitude": pickup_lat,
        "pickup_longitude": pickup_lon,
        "dropoff_latitude": dropoff_lat,
        "dropoff_longitude": dropoff_lon
    }
