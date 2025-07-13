import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './BreathingExercise.css';
import ErrorDisplay from './ErrorDisplay';
import StressGraph from './StressGraph';

const RelaxationToolkit = () => {
  const [isBreathingActive, setIsBreathingActive] = useState(false);
  const [breathingPhase, setBreathingPhase] = useState('inhale');
  const [breathingCount, setBreathingCount] = useState(0);
  const [isMusicPlaying, setIsMusicPlaying] = useState(false);
  const [currentTrack, setCurrentTrack] = useState(0);
  const [timing, setTiming] = useState({
    inhale: 4,
    hold: 4,
    exhale: 4,
    rest: 2
  });
  const [isCustomizing, setIsCustomizing] = useState(false);
  const [audioError, setAudioError] = useState(false);
  const [theme, setTheme] = useState('calm'); // 'calm', 'focus', 'night'
  const [activeTab, setActiveTab] = useState('breathing');
  const [error, setError] = useState(null);
  const [stressHistory, setStressHistory] = useState([]);
  
  const audioRef = useRef(null);
  const breathingIntervalRef = useRef(null);
  const soundEffectsRef = useRef({
    inhale: null,
    exhale: null,
    bell: null
  });

  // Theme colors
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

  // Initialize sound effects with error handling
  useEffect(() => {
    try {
      soundEffectsRef.current = {
        inhale: new Audio('/sounds/inhale.mp3'),
        exhale: new Audio('/sounds/exhale.mp3'),
        bell: new Audio('/sounds/bell.mp3')
      };
    } catch (error) {
      console.warn('Sound effects could not be loaded:', error);
      setAudioError(true);
    }
  }, []);

  const breathingPhases = {
    inhale: { duration: timing.inhale * 1000, text: 'Breathe In...' },
    hold: { duration: timing.hold * 1000, text: 'Hold...' },
    exhale: { duration: timing.exhale * 1000, text: 'Breathe Out...' },
    rest: { duration: timing.rest * 1000, text: 'Rest...' }
  };

  const musicTracks = [
    { title: 'Calming Track 1', src: '/music/calming1.mp3' },
    { title: 'Calming Track 2', src: '/music/calming2.mp3' },
    { title: 'Calming Track 3', src: '/music/calming3.mp3' }
  ];

  const youtubeVideoId = 'yDv0WSgXJVg?si=mpitOP4oXZcUQjJ9';

  const playSound = (sound) => {
    if (soundEffectsRef.current[sound] && !audioError) {
      try {
        soundEffectsRef.current[sound].play().catch(error => {
          console.warn(`Could not play ${sound} sound:`, error);
        });
      } catch (error) {
        console.warn(`Error playing ${sound} sound:`, error);
      }
    }
  };

  const startBreathingExercise = () => {
    setIsBreathingActive(true);
    setBreathingCount(0);
    setBreathingPhase('inhale');
    playSound('inhale');
    breathingIntervalRef.current = setInterval(updateBreathingPhase, breathingPhases.inhale.duration);
  };

  const stopBreathingExercise = () => {
    setIsBreathingActive(false);
    clearInterval(breathingIntervalRef.current);
    playSound('bell');
  };

  const updateBreathingPhase = () => {
    const phases = Object.keys(breathingPhases);
    const currentIndex = phases.indexOf(breathingPhase);
    const nextIndex = (currentIndex + 1) % phases.length;
    const nextPhase = phases[nextIndex];

    setBreathingPhase(nextPhase);

    if (nextPhase === 'inhale') {
      setBreathingCount(prev => prev + 1);
      playSound('inhale');
    } else if (nextPhase === 'exhale') {
      playSound('exhale');
    }

    clearInterval(breathingIntervalRef.current);
    breathingIntervalRef.current = setInterval(updateBreathingPhase, breathingPhases[nextPhase].duration);
  };

  const handleTimingChange = (phase, value) => {
    const newValue = Math.max(1, Math.min(10, parseInt(value) || 1));
    setTiming(prev => ({
      ...prev,
      [phase]: newValue
    }));
  };

  const toggleMusic = () => {
    if (!audioRef.current) return;
    
    try {
      if (isMusicPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play().catch(error => {
          console.warn('Could not play music:', error);
          setAudioError(true);
        });
      }
      setIsMusicPlaying(!isMusicPlaying);
    } catch (error) {
      console.warn('Error toggling music:', error);
      setAudioError(true);
    }
  };

  const nextTrack = () => {
    setCurrentTrack((prev) => (prev + 1) % musicTracks.length);
    if (isMusicPlaying && audioRef.current) {
      try {
        audioRef.current.load();
        audioRef.current.play().catch(error => {
          console.warn('Could not play next track:', error);
          setAudioError(true);
        });
      } catch (error) {
        console.warn('Error loading next track:', error);
        setAudioError(true);
      }
    }
  };

  const prevTrack = () => {
    setCurrentTrack((prev) => (prev - 1 + musicTracks.length) % musicTracks.length);
    if (isMusicPlaying && audioRef.current) {
      try {
        audioRef.current.load();
        audioRef.current.play().catch(error => {
          console.warn('Could not play previous track:', error);
          setAudioError(true);
        });
      } catch (error) {
        console.warn('Error loading previous track:', error);
        setAudioError(true);
      }
    }
  };

  useEffect(() => {
    return () => {
      clearInterval(breathingIntervalRef.current);
    };
  }, []);

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
      transition: {
        duration: 0.3
      }
    }
  };

  const breathingExercises = [
    {
      name: '4-7-8 Breathing',
      description: 'Inhale for 4 seconds, hold for 7, exhale for 8',
      duration: '5 minutes',
    },
    {
      name: 'Box Breathing',
      description: 'Equal duration for inhale, hold, exhale, and hold',
      duration: '4 minutes',
    },
    {
      name: 'Deep Breathing',
      description: 'Slow, deep breaths from the diaphragm',
      duration: '3 minutes',
    },
  ];

  const meditationExercises = [
    {
      name: 'Body Scan',
      description: 'Progressive relaxation through body awareness',
      duration: '10 minutes',
    },
    {
      name: 'Mindful Breathing',
      description: 'Focus on breath sensations',
      duration: '8 minutes',
    },
    {
      name: 'Loving Kindness',
      description: 'Cultivate compassion and positive emotions',
      duration: '12 minutes',
    },
  ];

  // Fetch stress history
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch('/api/stress-history');
        if (response.ok) {
          const data = await response.json();
          setStressHistory(data);
        }
      } catch (error) {
        console.error('Error fetching stress history:', error);
      }
    };
    fetchHistory();
  }, []);

  const renderContent = () => {
    if (error) {
      return <ErrorDisplay error={error} onRetry={() => setError(null)} theme={theme} />;
    }

    switch (activeTab) {
      case 'breathing':
        return (
          <div className="space-y-6">
            <h3 className={`text-xl font-semibold ${themeColors[theme].text}`}>
              Breathing Exercises
            </h3>
            <div className="grid gap-4">
              {breathingExercises.map((exercise, index) => (
                <motion.div
                  key={index}
                  whileHover={{ scale: 1.02 }}
                  className={`p-4 rounded-lg ${themeColors[theme].accent}`}
                >
                  <h4 className="font-semibold">{exercise.name}</h4>
                  <p className="text-gray-600">{exercise.description}</p>
                  <p className="text-sm text-gray-500">Duration: {exercise.duration}</p>
                </motion.div>
              ))}
            </div>
          </div>
        );
      case 'meditation':
        return (
          <div className="space-y-6">
            <h3 className={`text-xl font-semibold ${themeColors[theme].text}`}>
              Meditation Exercises
            </h3>
            <div className="grid gap-4">
              {meditationExercises.map((exercise, index) => (
                <motion.div
                  key={index}
                  whileHover={{ scale: 1.02 }}
                  className={`p-4 rounded-lg ${themeColors[theme].accent}`}
                >
                  <h4 className="font-semibold">{exercise.name}</h4>
                  <p className="text-gray-600">{exercise.description}</p>
                  <p className="text-sm text-gray-500">Duration: {exercise.duration}</p>
                </motion.div>
              ))}
            </div>
          </div>
        );
      case 'video':
        return (
          <div className="space-y-6">
            <h3 className={`text-xl font-semibold ${themeColors[theme].text}`}>
              Guided Relaxation Video
            </h3>
            <div className="relative w-full" style={{ paddingBottom: '56.25%' }}>
              <iframe
                className="absolute top-0 left-0 w-full h-full rounded-lg"
                src={`https://www.youtube.com/embed/${youtubeVideoId}`}
                title="Guided Relaxation"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              ></iframe>
            </div>
            <p className="text-gray-600">
              Follow along with this guided relaxation session to help reduce stress and anxiety.
            </p>
          </div>
        );
      case 'history':
        return (
          <div className="space-y-6">
            <h3 className={`text-xl font-semibold ${themeColors[theme].text}`}>
              Stress Level History
            </h3>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
              <StressGraph history={stressHistory} theme={theme} />
            </div>
            <div className="mt-4">
              <h4 className={`text-lg font-medium ${themeColors[theme].text}`}>
                Recent Stress Levels
              </h4>
              <div className="mt-2 space-y-2">
                {stressHistory.map((entry, index) => (
                  <div key={index} className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
                    <span className={themeColors[theme].text}>
                      {new Date(entry.timestamp).toLocaleTimeString()}
                    </span>
                    <span className={`px-3 py-1 rounded-full ${
                      entry.stress_level === 'Low' ? 'bg-green-100 text-green-800' :
                      entry.stress_level === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {entry.stress_level}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      default:
        return null;
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
        Relaxation Toolkit
      </motion.h2>

      {audioError && (
        <motion.div 
          className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-4"
          role="alert"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
        >
          <p className="font-bold">Audio Files Missing</p>
          <p>Please add the following files to enable sound effects and music:</p>
          <ul className="list-disc list-inside mt-2">
            <li>/sounds/inhale.mp3</li>
            <li>/sounds/exhale.mp3</li>
            <li>/sounds/bell.mp3</li>
            <li>/music/calming1.mp3</li>
            <li>/music/calming2.mp3</li>
            <li>/music/calming3.mp3</li>
          </ul>
        </motion.div>
      )}

      {/* Theme Selector */}
      <motion.div 
        className="flex justify-center space-x-4 mb-6"
        variants={itemVariants}
      >
        {Object.keys(themeColors).map((themeName) => (
          <button
            key={themeName}
            onClick={() => setTheme(themeName)}
            className={`px-4 py-2 rounded-full capitalize ${
              theme === themeName 
                ? themeColors[themeName].primary + ' text-white'
                : themeColors[themeName].secondary + ' ' + themeColors[themeName].text
            }`}
          >
            {themeName}
          </button>
        ))}
      </motion.div>

      {/* Breathing Exercise */}
      <motion.div 
        className={`bg-white p-6 rounded-lg shadow-md ${themeColors[theme].secondary}`}
        variants={itemVariants}
      >
        <div className="flex justify-between items-center mb-4">
          <h3 className={`text-xl font-semibold ${themeColors[theme].text}`}>
            Breathing Exercise
          </h3>
          <motion.button
            onClick={() => setIsCustomizing(!isCustomizing)}
            className={`text-${theme}-500 hover:text-${theme}-600`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isCustomizing ? 'Hide Settings' : 'Customize Timing'}
          </motion.button>
        </div>

        <AnimatePresence>
          {isCustomizing && (
            <motion.div 
              className="mb-6 p-4 bg-white rounded-lg"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <h4 className="font-medium mb-2">Breathing Timing (seconds)</h4>
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(timing).map(([phase, value]) => (
                  <div key={phase}>
                    <label className="block text-sm text-gray-600 mb-1 capitalize">
                      {phase}
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={value}
                      onChange={(e) => handleTimingChange(phase, e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded-md"
                    />
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {!isBreathingActive ? (
          <motion.div 
            className="text-center"
            variants={itemVariants}
          >
            <motion.button
              onClick={startBreathingExercise}
              className={`w-full ${themeColors[theme].primary} text-white py-2 px-4 rounded-md hover:bg-opacity-90 transition-colors`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Start Breathing Exercise
            </motion.button>
            <div className="breathing-instructions mt-4">
              <p>This exercise will guide you through a calming breathing pattern:</p>
              <ul className="list-disc list-inside mt-2">
                <li>Breathe in for {timing.inhale} seconds</li>
                <li>Hold for {timing.hold} seconds</li>
                <li>Breathe out for {timing.exhale} seconds</li>
                <li>Rest for {timing.rest} seconds</li>
              </ul>
            </div>
          </motion.div>
        ) : (
          <motion.div 
            className="breathing-container"
            variants={itemVariants}
          >
            <motion.div 
              className={`breathing-circle ${breathingPhase} ${isBreathingActive ? 'active' : ''}`}
              animate={{
                scale: breathingPhase === 'inhale' ? 1.2 : 1,
                opacity: 1
              }}
              transition={{
                duration: breathingPhases[breathingPhase].duration / 1000,
                ease: "easeInOut"
              }}
            >
              <div className="breathing-text">{breathingPhases[breathingPhase].text}</div>
              <div className="breathing-count">Breath {breathingCount}</div>
            </motion.div>
            <motion.button
              onClick={stopBreathingExercise}
              className="w-full mt-8 bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Stop Exercise
            </motion.button>
          </motion.div>
        )}
      </motion.div>

      {/* Music Player */}
      <motion.div 
        className={`bg-white p-6 rounded-lg shadow-md ${themeColors[theme].secondary}`}
        variants={itemVariants}
      >
        <h3 className={`text-xl font-semibold mb-4 ${themeColors[theme].text}`}>
          Calming Music
        </h3>
        <audio ref={audioRef} src={musicTracks[currentTrack].src} />
        <div className="flex items-center justify-between">
          <motion.button
            onClick={prevTrack}
            className={`${themeColors[theme].accent} p-2 rounded-full hover:bg-opacity-80 transition-colors`}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            ⏮️
          </motion.button>
          <motion.button
            onClick={toggleMusic}
            className={`${themeColors[theme].primary} text-white py-2 px-4 rounded-md hover:bg-opacity-90 transition-colors`}
            disabled={audioError}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isMusicPlaying ? '⏸️ Pause' : '▶️ Play'}
          </motion.button>
          <motion.button
            onClick={nextTrack}
            className={`${themeColors[theme].accent} p-2 rounded-full hover:bg-opacity-80 transition-colors`}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            ⏭️
          </motion.button>
        </div>
        <motion.div 
          className="text-center mt-2"
          animate={{ opacity: [0.5, 1] }}
          transition={{ duration: 0.5, repeat: Infinity, repeatType: "reverse" }}
        >
          {musicTracks[currentTrack].title}
        </motion.div>
      </motion.div>

      {/* YouTube Meditation */}
      <motion.div 
        className={`bg-white p-6 rounded-lg shadow-md ${themeColors[theme].secondary}`}
        variants={itemVariants}
      >
        <h3 className={`text-xl font-semibold mb-4 ${themeColors[theme].text}`}>
          Guided Meditation
        </h3>
        <div className="relative w-full" style={{ paddingBottom: '56.25%' }}>
          <iframe
            src={`https://www.youtube.com/embed/${youtubeVideoId}`}
            title="Guided Meditation"
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            className="absolute top-0 left-0 w-full h-full rounded-lg"
          ></iframe>
        </div>
      </motion.div>

      {/* Tabs */}
      <div className="flex space-x-4 mb-6">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setActiveTab('breathing')}
          className={`px-4 py-2 rounded-md ${
            activeTab === 'breathing' ? themeColors[theme].primary : 'bg-gray-200'
          } text-white`}
        >
          Breathing
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setActiveTab('meditation')}
          className={`px-4 py-2 rounded-md ${
            activeTab === 'meditation' ? themeColors[theme].primary : 'bg-gray-200'
          } text-white`}
        >
          Meditation
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setActiveTab('video')}
          className={`px-4 py-2 rounded-md ${
            activeTab === 'video' ? themeColors[theme].primary : 'bg-gray-200'
          } text-white`}
        >
          Video
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setActiveTab('history')}
          className={`px-4 py-2 rounded-md ${
            activeTab === 'history' ? themeColors[theme].primary : 'bg-gray-200'
          } text-white`}
        >
          History
        </motion.button>
      </div>

      {error ? (
        <ErrorDisplay error={error} onRetry={() => setError(null)} theme={theme} />
      ) : (
        renderContent()
      )}
    </motion.div>
  );
};

export default RelaxationToolkit; 