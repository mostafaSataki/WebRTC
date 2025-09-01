import asyncio
import json
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import base64
import threading
import queue
import time
import os
import urllib.request
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
current_video_path = None
video_processor = None
face_detector = None

def show_progress(count, block_size, total_size):
    """Progress callback for urllib.request.urlretrieve"""
    percent = int(count * block_size * 100 / total_size)
    print(f"\rProgress: {percent}% ({count * block_size}/{total_size} bytes)", end='', flush=True)

def download_model_files():
    """Download required model files if they don't exist"""
    model_dir = Path(__file__).parent
    prototxt_path = model_dir / "deploy.prototxt"
    model_path = model_dir / "res10_300x300_ssd_iter_140000.caffemodel"
    
    # URLs for model files
    prototxt_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
    model_url = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"
    
    try:
        # Download prototxt file if not exists
        if not prototxt_path.exists():
            print("📥 Downloading deploy.prototxt...")
            urllib.request.urlretrieve(prototxt_url, prototxt_path, show_progress)
            print("\n✓ deploy.prototxt downloaded successfully")
        else:
            print("✓ deploy.prototxt already exists")
        
        # Download model file if not exists
        if not model_path.exists():
            print("📥 Downloading res10_300x300_ssd_iter_140000.caffemodel...")
            print("⏳ This may take a few minutes (file size: ~10MB)...")
            urllib.request.urlretrieve(model_url, model_path, show_progress)
            print("\n✓ res10_300x300_ssd_iter_140000.caffemodel downloaded successfully")
        else:
            print("✓ res10_300x300_ssd_iter_140000.caffemodel already exists")
            
        return str(prototxt_path), str(model_path)
        
    except Exception as e:
        print(f"\n❌ Error downloading model files: {e}")
        print("📋 Please download the files manually:")
        print(f"1. {prototxt_url}")
        print(f"2. {model_url}")
        raise

class FaceDetector:
    def __init__(self):
        # Download model files if they don't exist
        print("Checking for required model files...")
        self.prototxt_path, self.model_path = download_model_files()
        
        # Load the pre-trained model
        print("Loading face detection model...")
        try:
            self.net = cv2.dnn.readNetFromCaffe(self.prototxt_path, self.model_path)
            print("✓ Face detection model loaded successfully")
        except Exception as e:
            print(f"Error loading face detection model: {e}")
            raise
    
    def detect_faces(self, frame):
        """Detect faces in a frame and return face regions"""
        (h, w) = frame.shape[:2]
        
        # Preprocess: resize to 300x300 and normalize
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            1.0,
            (300, 300),
            (104.0, 177.0, 123.0)
        )
        
        # Set input and perform forward pass
        self.net.setInput(blob)
        detections = self.net.forward()
        
        faces = []
        # Loop over detections
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            # Confidence threshold
            if confidence > 0.5:
                # Get bounding box coordinates
                box = detections[0, 0, i, 3:7] * [w, h, w, h]
                (startX, startY, endX, endY) = box.astype("int")
                
                faces.append({
                    'x': int(startX),
                    'y': int(startY),
                    'width': int(endX - startX),
                    'height': int(endY - startY),
                    'confidence': float(confidence)
                })
        
        return faces

class VideoProcessor:
    def __init__(self, video_path, websocket):
        self.video_path = video_path
        self.websocket = websocket
        self.cap = None
        self.is_running = False
        self.frame_queue = queue.Queue(maxsize=10)
        # Use global face detector to avoid reloading models
        global face_detector
        if face_detector is None:
            face_detector = FaceDetector()
        self.face_detector = face_detector
        
    async def start_processing(self):
        """Start video processing in a separate thread"""
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            await self.websocket.send_text(json.dumps({
                'type': 'error',
                'message': f'Could not open video file: {self.video_path}'
            }))
            return
            
        self.is_running = True
        
        # Start frame processing thread
        threading.Thread(target=self._process_frames, daemon=True).start()
        
        # Start streaming thread
        await self._stream_frames()
    
    def _process_frames(self):
        """Process frames in background thread"""
        while self.is_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
                
            # Detect faces
            faces = self.face_detector.detect_faces(frame)
            
            # Convert frame to base64
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            frame_data = {
                'frame': frame_base64,
                'faces': faces,
                'timestamp': time.time()
            }
            
            # Add to queue (non-blocking)
            try:
                self.frame_queue.put(frame_data, timeout=0.1)
            except queue.Full:
                # Skip frame if queue is full
                continue
                
            # Control frame rate (approximately 30 FPS)
            time.sleep(1/30)
    
    async def _stream_frames(self):
        """Stream frames via WebSocket"""
        while self.is_running:
            try:
                # Get frame data from queue
                frame_data = self.frame_queue.get(timeout=1.0)
                
                # Send frame and face data via WebSocket
                await self.websocket.send_text(json.dumps({
                    'type': 'frame',
                    'data': frame_data
                }))
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error streaming frame: {e}")
                break
    
    def stop_processing(self):
        """Stop video processing"""
        self.is_running = False
        if self.cap:
            self.cap.release()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message['type'] == 'start_video':
                video_path = message['video_path']
                
                # Stop previous video if running
                global video_processor
                if video_processor:
                    video_processor.stop_processing()
                
                # Start new video processing
                video_processor = VideoProcessor(video_path, websocket)
                await video_processor.start_processing()
                
            elif message['type'] == 'stop_video':
                if video_processor:
                    video_processor.stop_processing()
                    video_processor = None
                
                await websocket.send_text(json.dumps({
                    'type': 'stopped'
                }))
                
    except WebSocketDisconnect:
        if video_processor:
            video_processor.stop_processing()
            video_processor = None

@app.get("/")
async def root():
    return {"message": "WebRTC Face Detection Server"}

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting WebRTC Face Detection Server")
    print("=" * 60)
    
    # Initialize face detector on startup to download models if needed
    try:
        face_detector = FaceDetector()
        print("✓ Server initialization complete")
        print("📡 Server will be available at: http://localhost:8000")
        print("🌐 WebSocket endpoint: ws://localhost:8000/ws")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Failed to initialize server: {e}")
        exit(1)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)