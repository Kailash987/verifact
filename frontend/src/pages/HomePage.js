import React, { useState } from 'react';
import { 
  SparklesIcon,
  ShieldCheckIcon,
  CpuChipIcon,
  ChartBarIcon 
} from '@heroicons/react/24/outline';
import PredictionForm from '../components/PredictionForm';
import PredictionResult from '../components/PredictionResult';

const HomePage = () => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const handlePrediction = (result) => {
    setPrediction(result);
  };

  const features = [
    {
      icon: CpuChipIcon,
      title: 'AI-Powered Detection',
      description: 'Uses advanced BERT-based transformer models to analyze text patterns and detect misinformation.'
    },
    {
      icon: SparklesIcon,
      title: 'Explainable AI',
      description: 'Get insights into why text was classified as fake or real with highlighted important words.'
    },
    {
      icon: ShieldCheckIcon,
      title: 'Real-time Analysis',
      description: 'Instantly analyze news articles, social media posts, and headlines for authenticity.'
    },
    {
      icon: ChartBarIcon,
      title: 'Confidence Scoring',
      description: 'Receive confidence scores to help you make informed decisions about content credibility.'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Detect Fake News with AI
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Our advanced machine learning model analyzes text content to identify potential misinformation, 
            helping you make informed decisions about the news you consume.
          </p>
        </div>

        {/* Prediction Section */}
        <div className="mb-16">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-semibold text-gray-900 mb-2">
              Analyze Text Now
            </h3>
            <p className="text-gray-600">
              Enter any news text, headline, or social media post to check if it's likely fake or real.
            </p>
          </div>

          <div className="space-y-8">
            <PredictionForm 
              onPrediction={handlePrediction} 
              loading={loading} 
              setLoading={setLoading} 
            />
            
            {prediction && (
              <PredictionResult prediction={prediction} />
            )}
          </div>
        </div>

        {/* Features Section */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Why Choose Our Detector?
            </h3>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Built with cutting-edge technology to provide accurate and explainable fake news detection.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center group">
                <div className="mx-auto w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-primary-200 transition-colors">
                  <feature.icon className="w-8 h-8 text-primary-600" />
                </div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h4>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-16">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              How It Works
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-lg font-bold">
                1
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Input Text</h4>
              <p className="text-gray-600 text-sm">
                Paste any news text, headline, or social media post into the analysis field.
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-lg font-bold">
                2
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">AI Analysis</h4>
              <p className="text-gray-600 text-sm">
                Our BERT-based model analyzes the text for patterns associated with fake news.
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-lg font-bold">
                3
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Get Results</h4>
              <p className="text-gray-600 text-sm">
                Receive instant classification with confidence score and explanation.
              </p>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center bg-primary-600 rounded-2xl p-8 text-white">
          <h3 className="text-2xl font-bold mb-4">
            Start Detecting Fake News Today
          </h3>
          <p className="text-lg mb-6 opacity-90">
            Join thousands of users who are already using AI to combat misinformation.
          </p>
          <div className="flex items-center justify-center gap-4">
            <div className="text-sm">
              <div className="font-semibold">Accuracy Rate</div>
              <div className="text-2xl font-bold">92%</div>
            </div>
            <div className="text-sm">
              <div className="font-semibold">Texts Analyzed</div>
              <div className="text-2xl font-bold">100K+</div>
            </div>
            <div className="text-sm">
              <div className="font-semibold">Response Time</div>
              <div className="text-2xl font-bold">&lt;1s</div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-4">
              <ShieldCheckIcon className="w-6 h-6" />
              <span className="text-lg font-semibold">VeriFact</span>
            </div>
            <p className="text-gray-400 text-sm">
              Powered by advanced AI technology to help combat misinformation.
            </p>
            <p className="text-gray-500 text-xs mt-2">
              © 2024 VeriFact. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
