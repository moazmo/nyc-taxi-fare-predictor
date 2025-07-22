# NYC Taxi Fare Predictor - Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-07-22

### Added
- 🚀 **Initial Release** - Complete NYC Taxi Fare Predictor web application
- 🗺️ **Interactive Map Interface** - Leaflet-based map with pickup/dropoff selection
- 🤖 **Enhanced ML Model** - Ensemble model with XGBoost, Random Forest, and Gradient Boosting
- 📊 **Real-time Predictions** - Instant fare estimates with confidence scores
- 🎯 **NYC Bounds Validation** - Coordinate validation for NYC area
- 💻 **Modern Tech Stack** - FastAPI backend with React TypeScript frontend
- 📚 **API Documentation** - Auto-generated docs with FastAPI
- 🎨 **Responsive UI** - Mobile-friendly design with React Hot Toast notifications

### Features
- **Backend API** (`/predict`, `/health`, `/model-info`)
- **Frontend Components** (MapComponent, PredictionForm, App)
- **ML Pipeline** (21 optimized features, robust scaling, ensemble prediction)
- **Development Environment** (Hot reload, CORS support, error handling)

### Performance Metrics
- **RMSE**: 3.42
- **R²**: 0.877  
- **MAE**: 1.55
- **MAPE**: 14.5%

---

## Development Notes

### Version Format
We use [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)  
- **PATCH**: Bug fixes (backward compatible)

### Categories
- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security vulnerability fixes
