import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { 
  ShieldCheckIcon,
  ClockIcon,
  CogIcon,
  InformationCircleIcon 
} from '@heroicons/react/24/outline';
import HomePage from './pages/HomePage';
import HistoryPage from './pages/HistoryPage';

function App() {
  const [currentPage, setCurrentPage] = useState('home');

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              {/* Logo */}
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary-600 rounded-lg">
                  <ShieldCheckIcon className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-gray-900">VeriFact</span>
              </div>

              {/* Navigation Links */}
              <div className="hidden md:flex items-center gap-8">
                <button
                  onClick={() => setCurrentPage('home')}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                    currentPage === 'home' 
                      ? 'bg-primary-100 text-primary-700' 
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <ShieldCheckIcon className="w-4 h-4" />
                  <span>Detect</span>
                </button>

                <button
                  onClick={() => setCurrentPage('history')}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                    currentPage === 'history' 
                      ? 'bg-primary-100 text-primary-700' 
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <ClockIcon className="w-4 h-4" />
                  <span>History</span>
                </button>

                <button className="flex items-center gap-2 px-3 py-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors">
                  <CogIcon className="w-4 h-4" />
                  <span>Settings</span>
                </button>

                <button className="flex items-center gap-2 px-3 py-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors">
                  <InformationCircleIcon className="w-4 h-4" />
                  <span>About</span>
                </button>
              </div>

              {/* Mobile menu button */}
              <div className="md:hidden">
                <button className="p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>

        {/* Mobile Navigation */}
        <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200">
          <div className="grid grid-cols-4 gap-1">
            <button
              onClick={() => setCurrentPage('home')}
              className={`flex flex-col items-center gap-1 py-2 text-xs ${
                currentPage === 'home' ? 'text-primary-600' : 'text-gray-600'
              }`}
            >
              <ShieldCheckIcon className="w-5 h-5" />
              <span>Detect</span>
            </button>
            
            <button
              onClick={() => setCurrentPage('history')}
              className={`flex flex-col items-center gap-1 py-2 text-xs ${
                currentPage === 'history' ? 'text-primary-600' : 'text-gray-600'
              }`}
            >
              <ClockIcon className="w-5 h-5" />
              <span>History</span>
            </button>
            
            <button className="flex flex-col items-center gap-1 py-2 text-xs text-gray-600">
              <CogIcon className="w-5 h-5" />
              <span>Settings</span>
            </button>
            
            <button className="flex flex-col items-center gap-1 py-2 text-xs text-gray-600">
              <InformationCircleIcon className="w-5 h-5" />
              <span>About</span>
            </button>
          </div>
        </div>
      </div>
    </Router>
  );
}

export default App;
