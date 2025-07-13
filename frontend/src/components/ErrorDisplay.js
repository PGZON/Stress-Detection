import React from 'react';
import { motion } from 'framer-motion';

const ErrorDisplay = ({ error, onRetry, theme }) => {
  // Error state GIFs
  const errorGifs = {
    noFace: "https://media.giphy.com/media/3o7bu3XilJ5BOiSGic/giphy.gif", // No face detected
    poorLighting: "https://media.giphy.com/media/3o7bu3XilJ5BOiSGic/giphy.gif", // Poor lighting
    tooClose: "https://media.giphy.com/media/3o7bu3XilJ5BOiSGic/giphy.gif", // Too close to camera
    tooFar: "https://media.giphy.com/media/3o7bu3XilJ5BOiSGic/giphy.gif", // Too far from camera
    notCentered: "https://media.giphy.com/media/3o7bu3XilJ5BOiSGic/giphy.gif", // Face not centered
    default: "https://media.giphy.com/media/3o7bu3XilJ5BOiSGic/giphy.gif" // Default error
  };

  let gifUrl = errorGifs.default;
  let message = "An error occurred. Please try again.";

  if (error.includes("No face detected")) {
    gifUrl = errorGifs.noFace;
    message = "No face detected. Please ensure your face is visible in the camera.";
  } else if (error.includes("Poor lighting")) {
    gifUrl = errorGifs.poorLighting;
    message = "Poor lighting detected. Please ensure your face is well-lit.";
  } else if (error.includes("too close")) {
    gifUrl = errorGifs.tooClose;
    message = "You're too close to the camera. Please move back.";
  } else if (error.includes("too far")) {
    gifUrl = errorGifs.tooFar;
    message = "You're too far from the camera. Please move closer.";
  } else if (error.includes("center")) {
    gifUrl = errorGifs.notCentered;
    message = "Please center your face in the frame.";
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="flex flex-col items-center justify-center p-6 space-y-4"
    >
      <motion.img
        src={gifUrl}
        alt="Error Animation"
        className="w-48 h-48 rounded-lg"
        initial={{ scale: 0.8 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.3 }}
      />
      <motion.p
        className={`text-center text-lg font-medium ${theme === 'dark' ? 'text-white' : 'text-gray-800'}`}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        {message}
      </motion.p>
      <motion.button
        onClick={onRetry}
        className={`bg-blue-500 text-white px-6 py-2 rounded-full hover:bg-opacity-90 transition-colors`}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        Try Again
      </motion.button>
    </motion.div>
  );
};

export default ErrorDisplay; 