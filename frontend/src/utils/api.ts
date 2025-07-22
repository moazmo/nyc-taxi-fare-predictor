import axios from 'axios';
import { TripRequest, PredictionResponse, HealthResponse } from '../types/api';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const predictFare = async (tripData: TripRequest): Promise<PredictionResponse> => {
  try {
    const response = await api.post<PredictionResponse>('/predict', tripData);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.message || 'Prediction failed');
    }
    throw new Error('Network error occurred');
  }
};

export const checkHealth = async (): Promise<HealthResponse> => {
  try {
    const response = await api.get<HealthResponse>('/health');
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.message || 'Health check failed');
    }
    throw new Error('Network error occurred');
  }
};

export const validateCoordinates = async (lat: number, lon: number): Promise<boolean> => {
  try {
    const response = await api.get('/validate-coordinates', {
      params: { lat, lon }
    });
    return response.data.is_valid;
  } catch (error) {
    console.error('Coordinate validation error:', error);
    return false;
  }
};

export { API_BASE_URL };
