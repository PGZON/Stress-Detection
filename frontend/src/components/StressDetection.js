import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import StressGraph from './StressGraph';
import ErrorDisplay from './ErrorDisplay';

const StressDetection = ({ theme }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [error, setError] = useState(null);
  const [stressLevel, setStressLevel] = useState(null);
  const [stressHistory, setStressHistory] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setIsCameraOn(true);
      setError(null);
    } catch (err) {
      setError('Failed to access camera. Please ensure you have granted camera permissions.');
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsCameraOn(false);
  };

  const toggleCamera = () => {
    if (isCameraOn) {
      stopCamera();
    } else {
      startCamera();
    }
  };

  const processFrame = async () => {
    if (!isCameraOn || !videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw the current video frame
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    try {
      setIsProcessing(true);
      const response = await fetch('http://localhost:8000/predict-stress', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: canvas.toDataURL('image/jpeg').split(',')[1], // Send base64 without prefix
          timestamp: new Date().toISOString()
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to process frame');
      }

      const data = await response.json();
      
      // Update stress level
      setStressLevel(data.stress_level);
      
      // Fetch the updated history after a successful prediction
      fetchStressHistory();
      
      // Draw face rectangle if available (DeepFace doesn't return landmarks directly)
      if (data.face_coords) {
        context.strokeStyle = '#00ff00';
        context.lineWidth = 2;
        const [x, y, w, h] = data.face_coords;
        context.strokeRect(x, y, w, h);
      }

    } catch (error) {
      console.error('Error processing frame:', error);
      setError(error.message || 'Failed to process frame. Please try again.');
    } finally {
      setIsProcessing(false);
    }

    // Continue processing frames
    requestAnimationFrame(processFrame);
  };

  const fetchStressHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/stress-history');
      if (response.ok) {
        const data = await response.json();
        setStressHistory(data);
      } else {
        console.error('Failed to fetch stress history');
      }
    } catch (error) {
      console.error('Error fetching stress history:', error);
    }
  };

  useEffect(() => {
    if (isCameraOn) {
      videoRef.current.addEventListener('loadedmetadata', processFrame);
    }

    // Fetch history on component mount
    fetchStressHistory();

    return () => {
      if (videoRef.current) {
        videoRef.current.removeEventListener('loadedmetadata', processFrame);
      }
      stopCamera();
    };
  }, [isCameraOn]);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Video Feed Section */}
        <div className="space-y-4">
          <div className="relative">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full h-auto rounded-lg"
              style={{ display: isCameraOn ? 'block' : 'none' }}
            />
            <canvas
              ref={canvasRef}
              className="absolute top-0 left-0 w-full h-full"
              style={{ display: isCameraOn ? 'block' : 'none' }}
            />
            {!isCameraOn && (
              <div className="w-full aspect-video bg-gray-200 rounded-lg flex items-center justify-center">
                <p className="text-gray-500">Camera is off</p>
              </div>
            )}
          </div>

          <div className="flex justify-center space-x-4">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={toggleCamera}
              className={`px-6 py-2 rounded-full ${
                isCameraOn ? 'bg-red-500' : 'bg-blue-500'
              } text-white`}
            >
              {isCameraOn ? 'Stop Camera' : 'Start Camera'}
            </motion.button>
          </div>
        </div>

        {/* Stress Graph Section */}
        <div className="space-y-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
            <h3 className={`text-xl font-semibold mb-4 ${theme === 'dark' ? 'text-white' : 'text-gray-800'}`}>
              Stress Level History
            </h3>
            <StressGraph history={stressHistory} theme={theme} />
          </div>

          {/* Current Stress Level */}
          {stressLevel && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
              <h3 className={`text-xl font-semibold mb-2 ${theme === 'dark' ? 'text-white' : 'text-gray-800'}`}>
                Current Stress Level
              </h3>
              <div className={`text-2xl font-bold ${
                stressLevel === 'Low' ? 'text-green-500' :
                stressLevel === 'Medium' ? 'text-yellow-500' :
                'text-red-500'
              }`}>
                {stressLevel}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <ErrorDisplay error={error} onRetry={() => setError(null)} theme={theme} />
      )}

      {/* Processing Indicator */}
      {isProcessing && (
        <div className="fixed top-4 right-4 bg-blue-500 text-white px-4 py-2 rounded-full shadow-lg">
          Processing...
        </div>
      )}
    </div>
  );
};

export default StressDetection; 