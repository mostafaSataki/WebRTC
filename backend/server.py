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

class FaceDetector:
    def __init__(self):
        # Paths to model files
        self.prototxt_path = "deploy.prototxt"
        self.model_path = "res10_300x300_ssd_iter_140000.caffemodel"
        
        # Load the pre-trained model
        self.net = cv2.dnn.readNetFromCaffe(self.prototxt_path, self.model_path)
    
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
        self.face_detector = FaceDetector()
        
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
    uvicorn.run(app, host="0.0.0.0", port=8000)