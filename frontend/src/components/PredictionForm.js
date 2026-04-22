import React, { useState } from 'react';
import { MagnifyingGlassIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import api from '../services/api';

const PredictionForm = ({ onPrediction, loading, setLoading }) => {
  const [text, setText] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!text.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    if (text.length > 10000) {
      setError('Text is too long. Maximum 10,000 characters allowed.');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const result = await api.predictText(text, true);
      onPrediction(result);
      setText('');
    } catch (err) {
      setError(err.message || 'Failed to analyze text. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter news text, headline, or social media post to analyze..."
            className="w-full h-32 p-4 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            disabled={loading}
          />
          <div className="absolute bottom-4 right-4 text-sm text-gray-500">
            {text.length}/10,000
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <ExclamationTriangleIcon className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !text.trim()}
          className="w-full btn btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Analyzing...
            </>
          ) : (
            <>
              <MagnifyingGlassIcon className="w-5 h-5" />
              Analyze Text
            </>
          )}
        </button>
      </form>

      <div className="mt-4 text-center text-sm text-gray-600">
        <p>Enter any news text, headline, or social media post to check if it's likely fake or real.</p>
        <p className="mt-1">Our AI model will analyze the content and provide an explanation.</p>
      </div>
    </div>
  );
};

export default PredictionForm;
