"""
Pydantic models for API request/response validation.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class PredictionRequest(BaseModel):
    """Request model for taxi fare prediction."""
    
    pickup_longitude: float = Field(
        ..., 
        ge=-74.05, 
        le=-73.75,
        description="Pickup longitude (NYC bounds: -74.05 to -73.75)"
    )
    pickup_latitude: float = Field(
        ..., 
        ge=40.63, 
        le=40.85,
        description="Pickup latitude (NYC bounds: 40.63 to 40.85)"
    )
    dropoff_longitude: float = Field(
        ..., 
        ge=-74.05, 
        le=-73.75,
        description="Dropoff longitude (NYC bounds: -74.05 to -73.75)"
    )
    dropoff_latitude: float = Field(
        ..., 
        ge=40.63, 
        le=40.85,
        description="Dropoff latitude (NYC bounds: 40.63 to 40.85)"
    )
    passenger_count: int = Field(
        default=1,
        ge=1,
        le=6,
        description="Number of passengers (1-6)"
    )
    
    @validator('pickup_longitude', 'dropoff_longitude')
    def validate_longitude(cls, v):
        """Validate longitude is within NYC bounds."""
        if not (-74.05 <= v <= -73.75):
            raise ValueError('Longitude must be within NYC bounds (-74.05 to -73.75)')
        return v
    
    @validator('pickup_latitude', 'dropoff_latitude')
    def validate_latitude(cls, v):
        """Validate latitude is within NYC bounds."""
        if not (40.63 <= v <= 40.85):
            raise ValueError('Latitude must be within NYC bounds (40.63 to 40.85)')
        return v


class PredictionResponse(BaseModel):
    """Response model for taxi fare prediction."""
    
    fare: float = Field(..., description="Predicted fare amount in USD")
    confidence: float = Field(..., description="Prediction confidence (0-1)")
    distance_miles: float = Field(..., description="Trip distance in miles")
    duration_minutes: float = Field(..., description="Estimated trip duration in minutes")
    pickup_borough: str = Field(..., description="Pickup borough")
    dropoff_borough: str = Field(..., description="Dropoff borough")
    features: dict = Field(..., description="Model features used for prediction")
    model_version: str = Field(..., description="Model version used")
    prediction_timestamp: str = Field(..., description="Prediction timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fare": 15.75,
                "confidence": 0.85,
                "distance_miles": 3.2,
                "duration_minutes": 16.0,
                "pickup_borough": "Manhattan",
                "dropoff_borough": "Brooklyn",
                "features": {},
                "model_version": "Enhanced Ensemble v1.0",
                "prediction_timestamp": "2025-01-01T12:00:00Z"
            }
        }


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    model_loaded: bool = Field(..., description="Whether ML model is loaded")
    timestamp: str = Field(..., description="Current timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "model_loaded": True,
                "timestamp": "2025-01-01T12:00:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid coordinates provided",
                "details": {
                    "field": "pickup_longitude",
                    "provided_value": -75.0,
                    "valid_range": "(-74.05, -73.75)"
                }
            }
        }
