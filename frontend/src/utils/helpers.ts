export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

export const formatDistance = (miles: number): string => {
  return `${miles.toFixed(1)} miles`;
};

export const formatDuration = (minutes: number): string => {
  if (minutes < 60) {
    return `${Math.round(minutes)} min`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = Math.round(minutes % 60);
  return `${hours}h ${remainingMinutes}m`;
};

export const formatConfidence = (confidence: number): string => {
  return `${(confidence * 100).toFixed(0)}%`;
};

export const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.8) return '#10b981'; // green
  if (confidence >= 0.6) return '#f59e0b'; // yellow
  return '#ef4444'; // red
};

export const isValidNYCCoordinates = (lat: number, lng: number): boolean => {
  // NYC bounds
  const nycBounds = {
    north: 40.85,
    south: 40.63,
    east: -73.75,
    west: -74.05
  };
  
  return lat >= nycBounds.south && 
         lat <= nycBounds.north && 
         lng >= nycBounds.west && 
         lng <= nycBounds.east;
};
