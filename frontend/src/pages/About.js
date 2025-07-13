import React from 'react';
import { motion } from 'framer-motion';

const defaultThemeColors = {
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

const About = ({ theme = 'calm', themeColors = defaultThemeColors }) => {
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

  const team = [
    {
      name: 'AI Technology',
      role: 'Powered by advanced machine learning algorithms',
      description: 'Our stress detection system uses state-of-the-art facial recognition and emotion analysis.'
    },
    {
      name: 'User Experience',
      role: 'Designed for simplicity and effectiveness',
      description: 'Intuitive interface with personalized features to help you manage stress effectively.'
    },
    {
      name: 'Privacy First',
      role: 'Your data is secure',
      description: 'We prioritize your privacy with local processing and secure data handling.'
    }
  ];

  return (
    <div className="min-h-screen pt-20">
      <div className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h1 className={`text-4xl md:text-5xl font-bold mb-6 ${themeColors[theme].text}`}>
            About StressSense
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            StressSense is an innovative application that helps you monitor and manage your stress levels
            using advanced technology and proven relaxation techniques.
          </p>
        </motion.div>

        {/* Features Section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16"
        >
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`p-6 rounded-lg ${themeColors[theme].secondary} shadow-lg`}
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className={`text-xl font-semibold mb-2 ${themeColors[theme].text}`}>
                {feature.title}
              </h3>
              <p className="text-gray-600">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Team Section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8"
        >
          {team.map((member, index) => (
            <motion.div
              key={member.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`p-6 rounded-lg ${themeColors[theme].secondary} shadow-lg`}
            >
              <h3 className={`text-xl font-semibold mb-2 ${themeColors[theme].text}`}>
                {member.name}
              </h3>
              <p className={`text-sm mb-4 ${themeColors[theme].primary}`}>{member.role}</p>
              <p className="text-gray-600">{member.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  );
};

export default About; 