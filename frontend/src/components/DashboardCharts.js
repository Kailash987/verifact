import React from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend
} from 'recharts';

const DashboardCharts = ({ statistics, predictionHistory }) => {
  // Prepare data for charts
  const labelDistributionData = statistics?.label_distribution ? [
    { name: 'Fake News', value: statistics.label_distribution.FAKE || 0, color: '#ef4444' },
    { name: 'Real News', value: statistics.label_distribution.REAL || 0, color: '#22c55e' }
  ] : [];

  const dailyCountsData = statistics?.daily_counts?.map(item => ({
    date: new Date(item.date).toLocaleDateString(),
    count: item.count
  })) || [];

  const confidenceDistribution = predictionHistory?.reduce((acc, pred) => {
    const confidence = pred.confidence;
    if (confidence >= 0.8) acc.high++;
    else if (confidence >= 0.6) acc.medium++;
    else acc.low++;
    return acc;
  }, { high: 0, medium: 0, low: 0 });

  const confidenceData = [
    { name: 'High (80-100%)', value: confidenceDistribution.high, color: '#22c55e' },
    { name: 'Medium (60-80%)', value: confidenceDistribution.medium, color: '#eab308' },
    { name: 'Low (0-60%)', value: confidenceDistribution.low, color: '#ef4444' }
  ];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900">{`${label}: ${payload[0].value}`}</p>
        </div>
      );
    }
    return null;
  };

  const PieTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900">{`${payload[0].name}: ${payload[0].value}`}</p>
          <p className="text-xs text-gray-600">{`${((payload[0].percent) * 100).toFixed(1)}%`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      {/* Label Distribution Pie Chart */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Label Distribution</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={labelDistributionData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {labelDistributionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<PieTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Daily Predictions Line Chart */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Daily Prediction Trends</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={dailyCountsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis />
              <Tooltip content={<CustomTooltip />} />
              <Line 
                type="monotone" 
                dataKey="count" 
                stroke="#3b82f6" 
                strokeWidth={2}
                dot={{ fill: '#3b82f6', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Confidence Distribution Bar Chart */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Confidence Score Distribution</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={confidenceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" fill="#3b82f6">
                {confidenceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-primary-600">
            {statistics?.total_predictions || 0}
          </div>
          <div className="text-sm text-gray-600">Total Predictions</div>
        </div>
        
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-green-600">
            {statistics?.average_confidence ? (statistics.average_confidence * 100).toFixed(1) : 0}%
          </div>
          <div className="text-sm text-gray-600">Average Confidence</div>
        </div>
        
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">
            {statistics?.period_days || 0}
          </div>
          <div className="text-sm text-gray-600">Days Analyzed</div>
        </div>
      </div>
    </div>
  );
};

export default DashboardCharts;
