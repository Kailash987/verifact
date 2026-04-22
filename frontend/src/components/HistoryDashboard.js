import React, { useState, useEffect } from 'react';
import { 
  ClockIcon, 
  DocumentTextIcon,
  ChartBarIcon,
  MagnifyingGlassIcon,
  CheckCircleIcon,
  ArrowTrendingUpIcon
} from '@heroicons/react/24/outline';
import api from '../services/api';
import { format } from 'date-fns';
import DashboardCharts from './DashboardCharts';

const HistoryDashboard = () => {
  const [predictions, setPredictions] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [historyData, statsData] = await Promise.all([
        api.getPredictionHistory(0, 50, 30),
        api.getStatistics(30)
      ]);
      
      setPredictions(historyData.predictions || []);
      setStatistics(statsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    try {
      const results = await api.searchPredictions(searchQuery, 0, 20);
      setSearchResults(results.predictions || []);
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const getLabelColor = (label) => {
    return label === 'FAKE' ? 'text-fake-600 bg-fake-100' : 'text-real-600 bg-real-100';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Dashboard Charts */}
      {statistics && predictions.length > 0 && (
        <DashboardCharts statistics={statistics} predictionHistory={predictions} />
      )}

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card p-4">
            <div className="flex items-center gap-3">
              <DocumentTextIcon className="w-8 h-8 text-primary-600" />
              <div>
                <p className="text-sm text-gray-600">Total Predictions</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.total_predictions}</p>
              </div>
            </div>
          </div>

          <div className="card p-4">
            <div className="flex items-center gap-3">
              <ChartBarIcon className="w-8 h-8 text-fake-600" />
              <div>
                <p className="text-sm text-gray-600">Fake News</p>
                <p className="text-2xl font-bold text-fake-600">
                  {statistics.label_distribution?.FAKE || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="card p-4">
            <div className="flex items-center gap-3">
              <CheckCircleIcon className="w-8 h-8 text-real-600" />
              <div>
                <p className="text-sm text-gray-600">Real News</p>
                <p className="text-2xl font-bold text-real-600">
                  {statistics.label_distribution?.REAL || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="card p-4">
            <div className="flex items-center gap-3">
              <ArrowTrendingUpIcon className="w-8 h-8 text-primary-600" />
              <div>
                <p className="text-sm text-gray-600">Avg Confidence</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(statistics.average_confidence * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search */}
      <div className="card p-4">
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search predictions..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <button type="submit" className="btn btn-primary">
            Search
          </button>
        </form>
      </div>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="card p-4">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Search Results</h3>
          <div className="space-y-3">
            {searchResults.map((prediction) => (
              <div key={prediction.id} className="border-b border-gray-200 pb-3 last:border-b-0">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <p className="text-gray-800 line-clamp-2">{prediction.text}</p>
                    <div className="flex items-center gap-4 mt-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getLabelColor(prediction.prediction)}`}>
                        {prediction.prediction}
                      </span>
                      <span className={`text-sm font-medium ${getConfidenceColor(prediction.confidence)}`}>
                        {(prediction.confidence * 100).toFixed(1)}%
                      </span>
                      <span className="text-sm text-gray-500">
                        {format(new Date(prediction.created_at), 'MMM d, yyyy HH:mm')}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Predictions */}
      <div className="card p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <ClockIcon className="w-5 h-5" />
          Recent Predictions
        </h3>
        
        {predictions.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No predictions yet. Start analyzing some text!</p>
        ) : (
          <div className="space-y-3">
            {predictions.map((prediction) => (
              <div key={prediction.id} className="border-b border-gray-200 pb-3 last:border-b-0">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <p className="text-gray-800 line-clamp-2">{prediction.text}</p>
                    <div className="flex items-center gap-4 mt-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getLabelColor(prediction.prediction)}`}>
                        {prediction.prediction}
                      </span>
                      <span className={`text-sm font-medium ${getConfidenceColor(prediction.confidence)}`}>
                        {(prediction.confidence * 100).toFixed(1)}%
                      </span>
                      <span className="text-sm text-gray-500">
                        {format(new Date(prediction.created_at), 'MMM d, yyyy HH:mm')}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoryDashboard;
