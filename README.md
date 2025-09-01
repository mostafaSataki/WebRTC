# WebRTC Face Detection System

A real-time face detection system that processes video files and streams the results via WebSocket with face region drawing.

## Architecture

- **Backend**: Python FastAPI with WebSocket support for video processing and face detection
- **Frontend**: Next.js React application with WebSocket client and canvas-based video display
- **Face Detection**: OpenCV DNN with pre-trained Caffe model

## Features

- 🎥 Video file processing with real-time streaming
- 👤 Real-time face detection using OpenCV DNN
- 📹 WebSocket-based video streaming (frames sent as base64)
- 🎯 Face region drawing with confidence scores
- 🚀 Start/Stop controls
- 📊 Live face detection statistics
- 📥 Automatic model file download (deploy.prototxt & caffemodel)
- 🔄 Progress tracking for large file downloads

## Setup

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment and install dependencies:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

3. Start backend server (model files will be downloaded automatically if missing):
```bash
python server.py
```
Backend will run on http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start frontend development server:
```bash
npm run dev
```
Frontend will run on http://localhost:3000

## Quick Start

### Windows Users
- Run `start_backend.bat` to start the backend
- Run `start_frontend.bat` to start the frontend

### Usage

1. Open http://localhost:3000 in your browser
2. Enter the full path to a video file (e.g., `D:\Videos\sample.mp4`)
3. Click "Start Processing" to begin face detection
4. View real-time video stream with face detection boxes
5. Monitor face detection data in the right panel
6. Click "Stop" to end processing

## API Endpoints

### WebSocket Endpoints

#### `/ws` - Main WebSocket Connection
- **Purpose**: Handles video processing and streaming
- **Messages**:
  - `{'type': 'start_video', 'video_path': 'path/to/video.mp4'}` - Start processing
  - `{'type': 'stop_video'}` - Stop processing
- **Responses**:
  - `{'type': 'frame', 'data': {...}}` - Video frame with face data
  - `{'type': 'error', 'message': '...'}` - Error message
  - `{'type': 'stopped'}` - Processing stopped

## Technical Details

### Backend (Python)
- **Framework**: FastAPI with WebSocket support
- **Face Detection**: OpenCV DNN with SSD MobileNet
- **Video Processing**: OpenCV VideoCapture
- **Streaming**: Base64 encoded JPEG frames via WebSocket
- **Threading**: Background frame processing with queue management

### Frontend (React/Next.js)
- **Framework**: Next.js with TypeScript
- **Styling**: Tailwind CSS
- **WebSocket**: Native WebSocket API
- **Canvas**: HTML5 Canvas for video display and face drawing
- **Real-time Updates**: React state management with WebSocket events

### Face Detection Model
- **Model**: SSD MobileNet (300x300)
- **Framework**: Caffe
- **Input**: Preprocessed 300x300 BGR image
- **Output**: Bounding boxes with confidence scores
- **Threshold**: 0.5 confidence minimum

## File Structure

```
WebRTC/
├── backend/
│   ├── server.py              # Main FastAPI server
│   ├── test.py               # Original face detection script
│   ├── requirements.txt      # Python dependencies
│   ├── deploy.prototxt       # Model architecture
│   └── res10_300x300_ssd_iter_140000.caffemodel  # Model weights
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx      # Main application component
│   │   │   └── layout.tsx    # App layout
│   │   └── components/
│   │       ├── VideoPlayer.tsx      # Video display with face drawing
│   │       └── FaceDataDisplay.tsx  # Face detection statistics
│   ├── package.json          # Node.js dependencies
│   └── ...
├── start_backend.bat         # Windows backend startup
├── start_frontend.bat        # Windows frontend startup
└── README.md
```

## Performance Notes

- Frame rate: ~30 FPS (adjustable in backend)
- Face detection: Real-time processing
- WebSocket: Efficient binary frame transmission
- Memory: Queue-based frame management to prevent memory leaks

## Troubleshooting

1. **Backend won't start**: 
   - Check Python version (3.7+)
   - Ensure OpenCV is properly installed
   - Verify model files are present

2. **Frontend connection issues**:
   - Ensure backend is running on port 8000
   - Check browser console for WebSocket errors
   - Verify CORS settings

3. **Video not loading**:
   - Check video file path is absolute and correct
   - Ensure video format is supported by OpenCV
   - Verify file permissions

4. **Performance issues**:
   - Reduce video resolution
   - Adjust frame rate in backend
   - Check system resources