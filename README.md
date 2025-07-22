# 🚖 NYC Taxi Fare Predictor

A modern web application that predicts NYC taxi fares using machine learning. Built with FastAPI backend and React frontend for local development.

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **RESTful API** with FastAPI framework
- **Enhanced ML Model** - Uses the best performing model from Task_4_3_2
- **Input Validation** - NYC coordinate bounds and business logic validation
- **Confidence Scoring** - Prediction reliability assessment
- **CORS Support** - Configured for local frontend integration

### Frontend (React + TypeScript + Vite)
- **Interactive Map** - Visual trip planning with pickup/dropoff selection
- **Real-time Prediction** - Instant fare estimates
- **Confidence Display** - Visual confidence indicators
- **Responsive Design** - Mobile-friendly interface
- **Modern UI** - Built with Tailwind CSS

## 📁 Project Structure
```
Task_4_5/
├── README.md                    # This file
├── backend/                     # FastAPI backend
│   ├── app/                     # Application package
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI application
│   │   ├── models.py           # Pydantic models
│   │   ├── prediction.py       # ML prediction logic
│   │   └── utils.py            # Utility functions
│   ├── models/                  # ML model files
│   ├── requirements.txt         # Python dependencies
│   └── run.py                  # Local development server
├── frontend/                    # React frontend
│   ├── public/                  # Static assets
│   ├── src/                     # Source code
│   │   ├── components/         # React components
│   │   ├── types/              # TypeScript types
│   │   ├── utils/              # Utility functions
│   │   ├── App.tsx             # Main app component
│   │   └── main.tsx            # Entry point
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.ts          # Vite configuration
│   └── tailwind.config.js      # Tailwind CSS config
└── .gitignore                  # Git ignore file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### 1. Clone and Setup
```bash
git clone <your-repo>
cd Task_4_5
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python run.py
```
Backend will be available at: http://localhost:8000

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will be available at: http://localhost:5173

## 🧪 Testing
- Backend API: http://localhost:8000/docs (FastAPI auto-generated docs)
- Health Check: http://localhost:8000/health
- Frontend: http://localhost:5173

## 🔧 Development

### Backend Development
- Uses the enhanced model from Task_4_3_2
- Hot reload enabled for development
- Comprehensive logging and error handling

### Frontend Development
- Vite for fast development and building
- TypeScript for type safety
- Tailwind CSS for styling
- React hooks for state management

## 📊 ML Model Details
- **Source**: Enhanced model from Task_4_3_2
- **Type**: Ensemble model (Random Forest, XGBoost, LightGBM, Gradient Boosting)
- **Features**: Enhanced feature engineering with 17 optimized features
- **Performance**: Significantly improved over previous iterations
- **Confidence**: Provides prediction confidence scores

## 🎯 Features
- Interactive map for pickup/dropoff selection
- Real-time fare prediction
- Confidence scoring and error estimation
- Input validation and error handling
- Responsive design for all devices
- Local development optimized

## 🛠️ Tech Stack
- **Backend**: FastAPI, Python, scikit-learn, pandas, numpy
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Development**: Hot reload, auto-restart, source maps
- **Version Control**: Git

---
Built with ❤️ for local development and testing
