import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

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

const MoodJournal = ({ theme = 'calm', themeColors = defaultThemeColors }) => {
  const [entries, setEntries] = useState([]);
  const [newEntry, setNewEntry] = useState({
    mood: '',
    note: '',
    stressLevel: 'medium'
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'calendar'

  const moodOptions = [
    { emoji: '😊', label: 'Happy', value: 'happy' },
    { emoji: '😌', label: 'Calm', value: 'calm' },
    { emoji: '😐', label: 'Neutral', value: 'neutral' },
    { emoji: '😔', label: 'Sad', value: 'sad' },
    { emoji: '😡', label: 'Angry', value: 'angry' },
    { emoji: '😰', label: 'Anxious', value: 'anxious' }
  ];

  const stressLevels = [
    { label: 'Low', value: 'low', color: 'bg-green-500' },
    { label: 'Medium', value: 'medium', color: 'bg-yellow-500' },
    { label: 'High', value: 'high', color: 'bg-red-500' }
  ];

  useEffect(() => {
    fetchEntries();
  }, [selectedDate]);

  const fetchEntries = async () => {
    try {
      const response = await axios.get('http://localhost:8000/journal-entries');
      setEntries(response.data);
    } catch (error) {
      console.error('Error fetching entries:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await axios.post('http://localhost:8000/journal-entries', {
        ...newEntry,
        timestamp: new Date().toISOString()
      });

      setEntries([...entries, response.data]);
      setNewEntry({ mood: '', note: '', stressLevel: 'medium' });
      setShowEmojiPicker(false);
    } catch (error) {
      console.error('Error submitting entry:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.3 }
    }
  };

  const emojiVariants = {
    hidden: { scale: 0, opacity: 0 },
    visible: {
      scale: 1,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 260,
        damping: 20
      }
    }
  };

  return (
    <motion.div
      className="mt-8 space-y-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.h2
        className="text-2xl font-semibold text-center"
        variants={itemVariants}
      >
        Daily Mood Journal
      </motion.h2>

      {/* View Mode Toggle */}
      <motion.div
        className="flex justify-center space-x-4 mb-6"
        variants={itemVariants}
      >
        <motion.button
          onClick={() => setViewMode('list')}
          className={`px-4 py-2 rounded-full ${
            viewMode === 'list'
              ? themeColors[theme].primary + ' text-white'
              : themeColors[theme].secondary + ' ' + themeColors[theme].text
          }`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          List View
        </motion.button>
        <motion.button
          onClick={() => setViewMode('calendar')}
          className={`px-4 py-2 rounded-full ${
            viewMode === 'calendar'
              ? themeColors[theme].primary + ' text-white'
              : themeColors[theme].secondary + ' ' + themeColors[theme].text
          }`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Calendar View
        </motion.button>
      </motion.div>

      {/* New Entry Form */}
      <motion.form
        onSubmit={handleSubmit}
        className={`bg-white p-6 rounded-lg shadow-md ${themeColors[theme].secondary}`}
        variants={itemVariants}
      >
        <h3 className={`text-xl font-semibold mb-4 ${themeColors[theme].text}`}>
          How are you feeling today?
        </h3>

        {/* Mood Selection */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Select Mood</label>
          <div className="relative">
            <motion.button
              type="button"
              onClick={() => setShowEmojiPicker(!showEmojiPicker)}
              className={`w-full p-2 rounded-md border ${
                newEntry.mood ? 'border-gray-300' : 'border-red-300'
              } ${themeColors[theme].accent} flex items-center justify-between`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <span>
                {newEntry.mood
                  ? `${moodOptions.find(m => m.value === newEntry.mood)?.emoji} ${
                      moodOptions.find(m => m.value === newEntry.mood)?.label
                    }`
                  : 'Select Mood'}
              </span>
              <span className="text-gray-500">▼</span>
            </motion.button>

            <AnimatePresence>
              {showEmojiPicker && (
                <motion.div
                  className="absolute z-10 mt-1 w-full bg-white rounded-md shadow-lg border border-gray-200"
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                >
                  <div className="grid grid-cols-2 gap-2 p-2">
                    {moodOptions.map((mood) => (
                      <motion.button
                        key={mood.value}
                        type="button"
                        onClick={() => {
                          setNewEntry({ ...newEntry, mood: mood.value });
                          setShowEmojiPicker(false);
                        }}
                        className="p-2 hover:bg-gray-100 rounded-md flex items-center space-x-2"
                        variants={emojiVariants}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                      >
                        <span className="text-2xl">{mood.emoji}</span>
                        <span className="text-sm">{mood.label}</span>
                      </motion.button>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Stress Level */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Stress Level</label>
          <div className="flex space-x-2">
            {stressLevels.map((level) => (
              <motion.button
                key={level.value}
                type="button"
                onClick={() => setNewEntry({ ...newEntry, stressLevel: level.value })}
                className={`flex-1 py-2 px-4 rounded-md ${
                  newEntry.stressLevel === level.value
                    ? level.color + ' text-white'
                    : 'bg-gray-200'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {level.label}
              </motion.button>
            ))}
          </div>
        </div>

        {/* Journal Entry */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Journal Entry</label>
          <textarea
            value={newEntry.note}
            onChange={(e) => setNewEntry({ ...newEntry, note: e.target.value })}
            className="w-full p-2 border border-gray-300 rounded-md"
            rows="4"
            placeholder="How are you feeling today? What's on your mind?"
          />
        </div>

        {/* Date Selection */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Date</label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-md"
          />
        </div>

        <motion.button
          type="submit"
          disabled={isSubmitting || !newEntry.mood}
          className={`w-full ${themeColors[theme].primary} text-white py-2 px-4 rounded-md ${
            isSubmitting || !newEntry.mood ? 'opacity-50' : 'hover:bg-opacity-90'
          } transition-colors`}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {isSubmitting ? 'Saving...' : 'Save Entry'}
        </motion.button>
      </motion.form>

      {/* Entries List */}
      <motion.div
        className={`bg-white p-6 rounded-lg shadow-md ${themeColors[theme].secondary}`}
        variants={itemVariants}
      >
        <h3 className={`text-xl font-semibold mb-4 ${themeColors[theme].text}`}>
          Recent Entries
        </h3>
        <AnimatePresence>
          {entries.map((entry, index) => (
            <motion.div
              key={entry.timestamp}
              className="mb-4 p-4 bg-white rounded-lg shadow"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">
                    {moodOptions.find(m => m.value === entry.mood)?.emoji}
                  </span>
                  <span className="font-medium">
                    {moodOptions.find(m => m.value === entry.mood)?.label}
                  </span>
                </div>
                <span className={`px-2 py-1 rounded-full text-sm text-white ${
                  stressLevels.find(s => s.value === entry.stressLevel)?.color
                }`}>
                  {entry.stressLevel}
                </span>
              </div>
              <p className="text-gray-600">{entry.note}</p>
              <p className="text-sm text-gray-400 mt-2">
                {new Date(entry.timestamp).toLocaleString()}
              </p>
            </motion.div>
          ))}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
};

export default MoodJournal; 