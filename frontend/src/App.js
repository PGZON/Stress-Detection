import React, { useState, createContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import About from './pages/About';
import Contact from './pages/Contact';
import LandingPage from './pages/LandingPage';
import StressDetector from './components/StressDetector';
import RelaxationToolkit from './components/RelaxationToolkit';
import MoodJournal from './components/MoodJournal';

// Theme context
export const ThemeContext = createContext();

const themeColors = {
  calm: {
    primary: 'bg-blue-500',
    secondary: 'bg-blue-100',
    text: 'text-blue-900',
    accent: 'bg-blue-200'
  },
  focus: {
    primary: 'bg-purple-500',
    secondary: 'bg-purple-100',
    text: 'text-purple-900',
    accent: 'bg-purple-200'
  },
  night: {
    primary: 'bg-indigo-500',
    secondary: 'bg-indigo-100',
    text: 'text-indigo-900',
    accent: 'bg-indigo-200'
  }
};

const AppContent = () => {
  const [activeTab, setActiveTab] = useState('stress');
  const [theme, setTheme] = useState('calm');

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar theme={theme} themeColors={themeColors} setTheme={setTheme} />
      
      <div className="container mx-auto px-4 pt-20">
        <div className="flex space-x-4 mb-6">
          <button
            onClick={() => setActiveTab('stress')}
            className={`px-4 py-2 rounded-md ${
              activeTab === 'stress' ? themeColors[theme].primary : 'bg-gray-200'
            } text-white`}
          >
            Stress Detection
          </button>
          <button
            onClick={() => setActiveTab('relaxation')}
            className={`px-4 py-2 rounded-md ${
              activeTab === 'relaxation' ? themeColors[theme].primary : 'bg-gray-200'
            } text-white`}
          >
            Relaxation Tools
          </button>
          <button
            onClick={() => setActiveTab('journal')}
            className={`px-4 py-2 rounded-md ${
              activeTab === 'journal' ? themeColors[theme].primary : 'bg-gray-200'
            } text-white`}
          >
            Mood Journal
          </button>
        </div>

        {activeTab === 'stress' && <StressDetector theme={theme} themeColors={themeColors} />}
        {activeTab === 'relaxation' && <RelaxationToolkit theme={theme} themeColors={themeColors} />}
        {activeTab === 'journal' && <MoodJournal theme={theme} themeColors={themeColors} />}
      </div>
    </div>
  );
};

const App = () => {
  return (
    <Router>
      <ThemeContext.Provider value={themeColors}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/app" element={<AppContent />} />
          <Route path="/about" element={<About theme="calm" themeColors={themeColors} />} />
          <Route path="/contact" element={<Contact theme="calm" themeColors={themeColors} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </ThemeContext.Provider>
    </Router>
  );
};

export default App; 