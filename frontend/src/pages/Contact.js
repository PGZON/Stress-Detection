import React, { useState } from 'react';
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

const Contact = ({ theme = 'calm', themeColors = defaultThemeColors }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle form submission
    console.log('Form submitted:', formData);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const socialLinks = [
    {
      name: 'GitHub',
      url: 'https://github.com',
      icon: '📦'
    },
    {
      name: 'LinkedIn',
      url: 'https://linkedin.com',
      icon: '💼'
    },
    {
      name: 'Twitter',
      url: 'https://twitter.com',
      icon: '🐦'
    }
  ];

  return (
    <div className="min-h-screen pt-20">
      <div className="container mx-auto px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-4xl mx-auto"
        >
          <h1 className={`text-4xl font-bold mb-8 text-center ${themeColors[theme].text}`}>
            Contact Us
          </h1>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Contact Form */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className={`p-6 rounded-lg ${themeColors[theme].secondary} shadow-lg`}
            >
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                    Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className="w-full px-4 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full px-4 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
                    Message
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    rows="4"
                    className="w-full px-4 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  ></textarea>
                </div>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  type="submit"
                  className={`w-full py-2 px-4 rounded-md text-white ${themeColors[theme].primary} hover:opacity-90 transition-opacity`}
                >
                  Send Message
                </motion.button>
              </form>
            </motion.div>

            {/* Contact Info */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className={`p-6 rounded-lg ${themeColors[theme].secondary} shadow-lg`}
            >
              <h2 className={`text-2xl font-semibold mb-6 ${themeColors[theme].text}`}>
                Get in Touch
              </h2>
              
              <div className="space-y-4">
                <p className="text-gray-600">
                  Have questions or feedback? We'd love to hear from you. Send us a message and we'll respond as soon as possible.
                </p>

                <div className="space-y-2">
                  <p className="text-gray-600">
                    <span className="font-medium">Email:</span> support@stresstracker.com
                  </p>
                  <p className="text-gray-600">
                    <span className="font-medium">Location:</span> San Francisco, CA
                  </p>
                </div>

                <div className="pt-4">
                  <h3 className={`text-lg font-semibold mb-4 ${themeColors[theme].text}`}>
                    Connect with us
                  </h3>
                  <div className="flex space-x-4">
                    {socialLinks.map((link) => (
                      <motion.a
                        key={link.name}
                        href={link.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        className={`p-2 rounded-full ${themeColors[theme].accent} hover:opacity-80 transition-opacity`}
                        aria-label={`Visit our ${link.name} page`}
                      >
                        <span className="text-xl">{link.icon}</span>
                      </motion.a>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Contact; 