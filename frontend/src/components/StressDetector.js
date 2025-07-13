import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import Webcam from 'react-webcam';
import StressGraph from './StressGraph';
import ErrorDisplay from './ErrorDisplay';

const StressDetector = ({ theme, themeColors }) => {
  const [isScanning, setIsScanning] = useState(false);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [stressLevel, setStressLevel] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [error, setError] = useState(null);
  const [faceQuality, setFaceQuality] = useState(null);
  const [stressHistory, setStressHistory] = useState([]);

  const webcamRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    fetchStressHistory();
    setError(null);
  }, []);

  useEffect(() => {
    return () => {
      if (webcamRef.current && webcamRef.current.video && webcamRef.current.video.srcObject) {
        const stream = webcamRef.current.video.srcObject;
        stream.getTracks().forEach(track => {
          if (track.kind === 'video') {
            track.stop();
            console.log("Camera track stopped on unmount.");
          }
        });
        webcamRef.current.video.srcObject = null;
      }
    };
  }, []);

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

  const performStressAnalysis = async () => {
    if (!isCameraActive) {
      setError("Please start the camera first to analyze stress.");
      return;
    }

    setIsScanning(true);
    setStressLevel(null);
    setSuggestions([]);
    setError(null);
    setFaceQuality(null);

    try {
      const video = webcamRef.current.video;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      const tempCanvas = document.createElement('canvas');
      tempCanvas.width = video.videoWidth;
      tempCanvas.height = video.videoHeight;
      const tempContext = tempCanvas.getContext('2d');

      tempContext.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
      const imageSrc = tempCanvas.toDataURL('image/jpeg', 0.8);
      console.log("Generated imageSrc length:", imageSrc.length);

      if (!imageSrc || imageSrc.length < 100) {
        console.warn("Image data seems invalid or too small. Skipping analysis.");
        throw new Error("Failed to capture valid image data from canvas.");
      }

      const base64Image = imageSrc.split(',')[1];
      console.log("Sending request with base64 image length:", base64Image.length);

      const response = await fetch('http://localhost:8000/predict-stress', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          image: base64Image,
          timestamp: new Date().toISOString()
        }),
      });

      console.log("Received response status:", response.status);
      const data = await response.json();
      console.log("Received response data:", data);

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to analyze stress level');
      }

      setStressLevel(data.stress_level);
      setSuggestions(data.suggestions || []);
      setFaceQuality(data.face_quality);

      if (data.face_coords) {
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.strokeStyle = '#00ff00';
        context.lineWidth = 2;
        const [x, y, w, h] = data.face_coords;
        context.strokeRect(x, y, w, h);
        console.log("Drew face rectangle at:", data.face_coords);
      } else {
        context.clearRect(0, 0, canvas.width, canvas.height);
        console.log("No face coordinates received for this analysis.");
      }

      fetchStressHistory();

    } catch (err) {
      console.error('Error during stress analysis:', err);
      setError(err.message);
      if (canvasRef.current) {
        const context = canvasRef.current.getContext('2d');
        context.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
      }
    } finally {
      setIsScanning(false);
    }
  };

  useEffect(() => {
    let animationFrameId;
    
    const updateCanvas = () => {
      if (isCameraActive && webcamRef.current && canvasRef.current) {
        const video = webcamRef.current.video;
        const canvas = canvasRef.current;
        const context = canvas.getContext('2d');
        
        context.clearRect(0, 0, canvas.width, canvas.height);
        
        if (faceQuality && faceQuality.face_coords) {
          context.strokeStyle = '#00ff00';
          context.lineWidth = 2;
          const [x, y, w, h] = faceQuality.face_coords;
          context.strokeRect(x, y, w, h);
        }
        
        animationFrameId = requestAnimationFrame(updateCanvas);
      }
    };

    if (isCameraActive) {
      updateCanvas();
    }

    return () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
    };
  }, [isCameraActive, faceQuality]);

  const getStressLevelColor = (level) => {
    switch (level) {
      case 'Low':
        return 'text-green-600';
      case 'Medium':
        return 'text-yellow-600';
      case 'High':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  if (error) {
    return <ErrorDisplay error={error} onRetry={() => setError(null)} theme={theme} themeColors={themeColors} />;
  }

  return (
    <div className="max-w-6xl mx-auto p-4">
      <div className="bg-white rounded-lg shadow-lg p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="flex flex-col items-center space-y-4">
          <h2 className={`text-2xl font-bold ${themeColors[theme].text}`}>Live Stress Detection</h2>
          <div className="relative w-full aspect-video rounded-lg overflow-hidden border border-gray-300">
            {isCameraActive ? (
              <>
                <Webcam
                  ref={webcamRef}
                  audio={false}
                  screenshotFormat="image/jpeg"
                  className="w-full h-full object-cover"
                  videoConstraints={{
                    width: 640,
                    height: 480,
                    facingMode: "user"
                  }}
                  onUserMedia={(stream) => {
                    if (webcamRef.current && canvasRef.current) {
                      const video = webcamRef.current.video;
                      const canvas = canvasRef.current;
                      canvas.width = video.videoWidth;
                      canvas.height = video.videoHeight;
                      console.log("Webcam ready, canvas dimensions set.");
                    }
                    console.log("Camera started by Webcam component.");
                  }}
                  onUserMediaError={(error) => {
                    console.error("Webcam user media error:", error);
                    setError("Failed to access camera. Please ensure camera permissions are granted.");
                    setIsCameraActive(false);
                  }}
                />
                <canvas ref={canvasRef} className="absolute top-0 left-0 w-full h-full"></canvas>
              </>
            ) : (
              <div className="w-full aspect-video bg-gray-200 rounded-lg flex items-center justify-center">
                <p className="text-gray-500">Camera is off. Click "Start Camera" to activate.</p>
              </div>
            )}
          </div>

          <div className="mt-4 flex justify-center space-x-4">
            {!isCameraActive ? (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsCameraActive(true)}
                className={`px-6 py-3 rounded-md text-white ${themeColors[theme].primary} hover:opacity-90`}
              >
                Start Camera
              </motion.button>
            ) : (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsCameraActive(false)}
                className="px-6 py-3 rounded-md bg-red-500 text-white hover:opacity-90"
              >
                Stop Camera
              </motion.button>
            )}
            {isCameraActive && !isScanning && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={performStressAnalysis}
                className={`px-6 py-3 rounded-md text-white ${themeColors[theme].primary} hover:opacity-90`}
              >
                Analyze Stress
              </motion.button>
            )}
          </div>
          {isScanning && (
            <div className="text-center text-gray-600">
              <div className="flex flex-col items-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
                <p>Analyzing your stress level...</p>
              </div>
            </div>
          )}
        </div>

        <div className="space-y-6 flex flex-col">
          <div className={`p-6 rounded-lg ${themeColors[theme].secondary} flex-grow`}>
            <h3 className={`text-xl font-semibold mb-4 ${themeColors[theme].text}`}>
              Your Stress Level
            </h3>
            {stressLevel !== null ? (
              <div className={`text-4xl font-bold mb-4 ${getStressLevelColor(stressLevel)}`}>
                {stressLevel}
              </div>
            ) : (
              <div className="text-gray-600">Click "Analyze Stress" to see your stress level.</div>
            )}
            <div className="space-y-4">
              <h4 className={`font-semibold ${themeColors[theme].text}`}>Suggestions:</h4>
              <ul className="list-disc list-inside space-y-2">
                {suggestions.map((suggestion, index) => (
                  <li key={index} className="text-gray-700">
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className={`p-6 rounded-lg ${themeColors[theme].secondary} flex-grow`}>
            <h3 className={`text-xl font-semibold mb-4 ${themeColors[theme].text}`}>
              Stress Level History
            </h3>
            <div className="w-full h-64 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
              <StressGraph history={stressHistory} theme={theme} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StressDetector; 