/**
 * API service for communicating with the backend.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Prediction endpoints
  async predictText(text, includeExplanation = true) {
    return this.request(`/predict/?include_explanation=${includeExplanation}`, {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
  }

  async predictBatch(texts, includeExplanation = false) {
    return this.request(`/predict/batch?include_explanation=${includeExplanation}`, {
      method: 'POST',
      body: JSON.stringify({ texts }),
    });
  }

  async getPredictionHistory(skip = 0, limit = 50, daysBack = null) {
    let url = `/predict/history?skip=${skip}&limit=${limit}`;
    if (daysBack) {
      url += `&days_back=${daysBack}`;
    }
    return this.request(url);
  }

  async getPredictionById(id) {
    return this.request(`/predict/${id}`);
  }

  async searchPredictions(query, skip = 0, limit = 20) {
    return this.request(`/predict/search?q=${encodeURIComponent(query)}&skip=${skip}&limit=${limit}`);
  }

  async getStatistics(daysBack = 30) {
    return this.request(`/predict/statistics?days_back=${daysBack}`);
  }

  // Health endpoints
  async getHealthStatus() {
    return this.request('/health/');
  }

  async getModelInfo() {
    return this.request('/health/model');
  }

  async getDatabaseStatus() {
    return this.request('/health/database');
  }

  // Utility endpoints
  async ping() {
    return this.request('/ping');
  }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;
