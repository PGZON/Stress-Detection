import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const LandingPage = () => {
  const features = [
    {
      title: 'Real-time Stress Detection',
      description: 'Using advanced facial recognition and machine learning to detect stress levels in real-time.',
      icon: '🎯'
    },
    {
      title: 'Personalized Suggestions',
      description: 'Get tailored recommendations based on your stress patterns and preferences.',
      icon: '💡'
    },
    {
      title: 'Mood Tracking',
      description: 'Track your daily mood and stress levels to identify patterns and triggers.',
      icon: '📊'
    },
    {
      title: 'Relaxation Tools',
      description: 'Access guided breathing exercises, calming music, and meditation videos.',
      icon: '🧘'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-sm shadow-sm">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            <span className="text-2xl font-bold text-blue-900">StressSense</span>
            <div className="flex space-x-8">
              <Link to="/about" className="text-gray-600 hover:text-blue-900 transition-colors">
                About
              </Link>
              <Link to="/contact" className="text-gray-600 hover:text-blue-900 transition-colors">
                Contact
              </Link>
              <Link
                to="/app"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Launch App
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="container mx-auto px-4 pt-32 pb-16">
        <div className="max-w-4xl mx-auto text-center">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-5xl font-bold text-blue-900 mb-6"
          >
            Take Control of Your Stress
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-xl text-gray-600 mb-8"
          >
            StressSense helps you monitor and manage your stress levels using advanced technology
            and proven relaxation techniques.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Link
              to="/app"
              className="inline-block px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-md hover:bg-blue-700 transition-colors"
            >
              Get Started
            </Link>
          </motion.div>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-white p-6 rounded-lg shadow-lg"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-blue-900 mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Call to Action */}
      <div className="container mx-auto px-4 py-16">
        <div className="bg-blue-600 rounded-lg p-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Start Your Journey?</h2>
          <p className="text-blue-100 mb-8">
            Join thousands of users who have already improved their stress management with StressSense.
          </p>
          <Link
            to="/app"
            className="inline-block px-8 py-4 bg-white text-blue-600 text-lg font-semibold rounded-md hover:bg-blue-50 transition-colors"
          >
            Launch App
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white py-8">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>&copy; 2024 StressSense. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage; 