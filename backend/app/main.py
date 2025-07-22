"""
FastAPI main application for NYC Taxi Fare Prediction.
"""

import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .models import (
    PredictionRequest, 
    PredictionResponse, 
    HealthResponse, 
    ErrorResponse
)
from .prediction import get_predictor
from .utils import setup_logging, validate_nyc_coordinates

# Setup logging
logger = setup_logging()

# Create FastAPI application
app = FastAPI(
    title="NYC Taxi Fare Predictor API",
    description="A machine learning API for predicting NYC taxi fares using enhanced ensemble models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global predictor instance
predictor = None


@app.on_event("startup")
async def startup_event():
    """Initialize the ML model on startup."""
    global predictor
    try:
        logger.info("Initializing taxi fare predictor...")
        predictor = get_predictor()
        logger.info("Taxi fare predictor initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize predictor: {e}")
        raise


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {"type": type(exc).__name__}
        }
    )


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "NYC Taxi Fare Predictor API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "predict": "/predict"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global predictor
    
    model_loaded = predictor is not None and predictor.is_loaded
    
    return HealthResponse(
        status="healthy" if model_loaded else "unhealthy",
        version="1.0.0",
        model_loaded=model_loaded,
        timestamp=datetime.now().isoformat()
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict_fare(request: PredictionRequest):
    """
    Predict taxi fare for a given trip.
    
    Args:
        request: Trip details including pickup/dropoff coordinates and passenger count
    
    Returns:
        Prediction response with fare estimate, confidence, and details
    """
    global predictor
    
    if predictor is None or not predictor.is_loaded:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "ServiceUnavailable",
                "message": "ML model not loaded",
                "details": {"model_loaded": False}
            }
        )
    
    try:
        # Additional validation
        if not validate_nyc_coordinates(request.pickup_latitude, request.pickup_longitude):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "ValidationError",
                    "message": "Pickup coordinates are outside NYC bounds",
                    "details": {
                        "pickup_lat": request.pickup_latitude,
                        "pickup_lon": request.pickup_longitude,
                        "valid_lat_range": "(40.63, 40.85)",
                        "valid_lon_range": "(-74.05, -73.75)"
                    }
                }
            )
        
        if not validate_nyc_coordinates(request.dropoff_latitude, request.dropoff_longitude):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "ValidationError",
                    "message": "Dropoff coordinates are outside NYC bounds",
                    "details": {
                        "dropoff_lat": request.dropoff_latitude,
                        "dropoff_lon": request.dropoff_longitude,
                        "valid_lat_range": "(40.63, 40.85)",
                        "valid_lon_range": "(-74.05, -73.75)"
                    }
                }
            )
        
        # Make prediction
        result = predictor.predict_fare(
            pickup_lon=request.pickup_longitude,
            pickup_lat=request.pickup_latitude,
            dropoff_lon=request.dropoff_longitude,
            dropoff_lat=request.dropoff_latitude,
            passenger_count=request.passenger_count
        )
        
        return PredictionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "PredictionError",
                "message": "Failed to generate prediction",
                "details": {"error_type": type(e).__name__, "error_message": str(e)}
            }
        )


@app.get("/model-info")
async def get_model_info():
    """Get information about the loaded ML model."""
    global predictor
    
    if predictor is None:
        return {"loaded": False, "error": "Predictor not initialized"}
    
    return predictor.get_model_info()


@app.get("/validate-coordinates")
async def validate_coordinates(lat: float, lon: float):
    """Validate if coordinates are within NYC bounds."""
    is_valid = validate_nyc_coordinates(lat, lon)
    
    return {
        "latitude": lat,
        "longitude": lon,
        "is_valid": is_valid,
        "bounds": {
            "lat_range": "(40.63, 40.85)",
            "lon_range": "(-74.05, -73.75)"
        }
    }


# For development testing
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
