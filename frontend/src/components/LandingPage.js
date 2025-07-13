import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const LandingPage = () => {
  const features = [
    {
      title: "Real-time Stress Detection",
      description: "Advanced AI-powered facial analysis to detect stress levels instantly",
      icon: "🎯"
    },
    {
      title: "Guided Breathing Exercises",
      description: "Interactive breathing exercises with customizable timing and sound effects",
      icon: "🫁"
    },
    {
      title: "Mood Journal",
      description: "Track your daily mood and stress levels with detailed insights",
      icon: "📝"
    },
    {
      title: "Calming Music",
      description: "Curated collection of relaxing music and guided meditations",
      icon: "🎵"
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <motion.div
              className="flex items-center"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <span className="text-2xl font-bold text-indigo-600">StressSense</span>
            </motion.div>
            <motion.div
              className="flex space-x-4"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <Link
                to="/app"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
              >
                Launch App
              </Link>
            </motion.div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <motion.div
          className="text-center"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.h1
            className="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl"
            variants={itemVariants}
          >
            <span className="block">Take Control of Your</span>
            <span className="block text-indigo-600">Mental Well-being</span>
          </motion.h1>
          <motion.p
            className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl"
            variants={itemVariants}
          >
            StressSense uses advanced AI to help you understand and manage your stress levels.
            Get personalized recommendations and track your progress over time.
          </motion.p>
          <motion.div
            className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8"
            variants={itemVariants}
          >
            <div className="rounded-md shadow">
              <Link
                to="/app"
                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg md:px-10"
              >
                Get Started
              </Link>
            </div>
          </motion.div>
        </motion.div>
      </div>

      {/* Features Section */}
      <div className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            className="text-center"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <motion.h2
              className="text-3xl font-extrabold text-gray-900 sm:text-4xl"
              variants={itemVariants}
            >
              Everything you need to manage stress
            </motion.h2>
            <motion.p
              className="mt-4 text-lg text-gray-500"
              variants={itemVariants}
            >
              A comprehensive toolkit for stress management and mental well-being
            </motion.p>
          </motion.div>

          <motion.div
            className="mt-10"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  className="relative p-6 bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300"
                  variants={itemVariants}
                  whileHover={{ y: -5 }}
                >
                  <div className="text-4xl mb-4">{feature.icon}</div>
                  <h3 className="text-lg font-medium text-gray-900">{feature.title}</h3>
                  <p className="mt-2 text-base text-gray-500">{feature.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-indigo-700">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8 lg:flex lg:items-center lg:justify-between">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              <span className="block">Ready to start your journey?</span>
              <span className="block text-indigo-200">Begin managing your stress today.</span>
            </h2>
          </motion.div>
          <motion.div
            className="mt-8 flex lg:mt-0 lg:flex-shrink-0"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div className="inline-flex rounded-md shadow">
              <Link
                to="/app"
                className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-indigo-50"
              >
                Get Started
              </Link>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-base text-gray-500">
              &copy; 2024 StressSense. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage; 