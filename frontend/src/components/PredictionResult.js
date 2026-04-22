import React from 'react';
import { 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  InformationCircleIcon,
  SparklesIcon 
} from '@heroicons/react/24/outline';

const PredictionResult = ({ prediction }) => {
  if (!prediction) return null;

  const isFake = prediction.label === 'FAKE';
  const confidence = prediction.confidence;
  const confidenceColor = confidence >= 0.8 ? 'bg-green-500' : 
                          confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500';

  const highlightImportantWords = (text, importantWords) => {
    if (!importantWords || importantWords.length === 0) return text;

    let highlightedText = text;
    importantWords.forEach(word => {
      const regex = new RegExp(`\\b${word}\\b`, 'gi');
      highlightedText = highlightedText.replace(regex, `**${word}**`);
    });

    return highlightedText.split('**').map((part, index) => 
      index % 2 === 1 ? <mark key={index} className="bg-yellow-200 px-1 rounded">{part}</mark> : part
    );
  };

  return (
    <div className="w-full max-w-2xl mx-auto animate-fade-in">
      <div className={`card p-6 border-l-4 ${
        isFake ? 'border-l-fake-500' : 'border-l-real-500'
      }`}>
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            {isFake ? (
              <ExclamationTriangleIcon className="w-8 h-8 text-fake-600" />
            ) : (
              <CheckCircleIcon className="w-8 h-8 text-real-600" />
            )}
            <div>
              <h2 className={`text-2xl font-bold ${
                isFake ? 'text-fake-600' : 'text-real-600'
              }`}>
                {prediction.label}
              </h2>
              <p className="text-sm text-gray-600">
                Confidence: {(confidence * 100).toFixed(1)}%
              </p>
            </div>
          </div>
          
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            isFake ? 'bg-fake-100 text-fake-800' : 'bg-real-100 text-real-800'
          }`}>
            {isFake ? 'Misinformation' : 'Reliable'}
          </div>
        </div>

        {/* Confidence Bar */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Confidence Score</span>
            <span className="text-sm text-gray-600">{(confidence * 100).toFixed(1)}%</span>
          </div>
          <div className="confidence-bar">
            <div 
              className={`confidence-fill ${confidenceColor}`}
              style={{ width: `${confidence * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Original Text with Highlights */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-2 flex items-center gap-2">
            <SparklesIcon className="w-5 h-5 text-primary-600" />
            Analyzed Text
          </h3>
          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-gray-700 leading-relaxed">
              {prediction.explanation?.important_words ? 
                highlightImportantWords(prediction.text, prediction.explanation.important_words) :
                prediction.text
              }
            </p>
          </div>
        </div>

        {/* Explanation */}
        {prediction.explanation && (
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <InformationCircleIcon className="w-5 h-5 text-primary-600" />
              Key Indicators
            </h3>
            
            <div className="space-y-3">
              {/* Important Words */}
              {prediction.explanation.important_words && prediction.explanation.important_words.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Important Words:</p>
                  <div className="flex flex-wrap gap-2">
                    {prediction.explanation.important_words.map((word, index) => (
                      <span 
                        key={index}
                        className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm font-medium"
                      >
                        {word}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Method Info */}
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <InformationCircleIcon className="w-4 h-4" />
                <span>Analysis method: {prediction.explanation.method}</span>
              </div>
            </div>
          </div>
        )}

        {/* Warning for Low Confidence */}
        {confidence < 0.6 && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center gap-2 text-yellow-800">
              <ExclamationTriangleIcon className="w-5 h-5" />
              <span className="text-sm font-medium">
                Low Confidence: The model is uncertain about this prediction. 
                Please verify with additional sources.
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictionResult;
