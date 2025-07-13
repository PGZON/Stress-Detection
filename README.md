# StressSense - Real-Time Stress Detection System

StressSense is a web application that uses your device's camera to analyze facial expressions and predict stress levels in real-time. It provides personalized suggestions to help manage stress effectively.

## Features

- Real-time facial expression analysis
- Stress level classification (Low, Medium, High)
- Personalized stress management suggestions
- Clean and intuitive user interface
- Webcam integration
- Responsive design

## Tech Stack

### Backend
- FastAPI
- OpenCV
- DeepFace
- TensorFlow
- Python 3.8+

### Frontend
- React.js
- React Webcam
- Axios
- TailwindCSS

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
cd backend
uvicorn app:app --reload
```

The backend server will run on `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## Usage

1. Open the application in your web browser
2. Click "Start Stress Scan" to begin
3. Allow camera access when prompted
4. Click "Capture & Analyze" to analyze your current stress level
5. View your stress level and personalized suggestions
6. Click "Stop Scan" to end the session

## API Endpoints

- `POST /predict-stress`: Analyzes an image and returns stress level prediction
- `GET /suggestions/{level}`: Returns personalized suggestions based on stress level

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details. 