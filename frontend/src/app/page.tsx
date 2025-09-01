'use client'

import { useState, useRef, useEffect } from 'react'
import dynamic from 'next/dynamic'
import FaceDataDisplay from '@/components/FaceDataDisplay'
import ErrorBoundary from '@/components/ErrorBoundary'

// Dynamically import VideoPlayer to avoid SSR issues
const VideoPlayer = dynamic(() => import('@/components/VideoPlayer'), {
  ssr: false,
  loading: () => <div className="animate-pulse bg-gray-200 rounded-lg h-64 flex items-center justify-center">Loading video player...</div>
})

export default function Home() {
  const [videoPath, setVideoPath] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [faceData, setFaceData] = useState<any>(null)
  const [currentFrame, setCurrentFrame] = useState<string | null>(null)
  const websocketRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Cleanup WebSocket on unmount
    return () => {
      if (websocketRef.current) {
        websocketRef.current.close()
      }
    }
  }, [])

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket('ws://localhost:8000/ws')
      
      ws.onopen = () => {
        console.log('WebSocket connected')
      }
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        
        if (data.type === 'frame') {
          setCurrentFrame(`data:image/jpeg;base64,${data.data.frame}`)
          setFaceData(data.data.faces)
        } else if (data.type === 'error') {
          console.error('Backend error:', data.message)
          alert(`Error: ${data.message}`)
          setIsProcessing(false)
        } else if (data.type === 'stopped') {
          console.log('Video processing stopped')
        }
      }
      
      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setIsProcessing(false)
        setCurrentFrame(null)
        setFaceData(null)
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsProcessing(false)
      }
      
      websocketRef.current = ws
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      alert('Failed to connect to backend server')
    }
  }

  const handleStartProcessing = () => {
    if (!videoPath.trim()) {
      alert('Please enter a video file path')
      return
    }

    setIsProcessing(true)
    connectWebSocket()

    // Wait for connection before sending message
    setTimeout(() => {
      if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
        websocketRef.current.send(JSON.stringify({
          type: 'start_video',
          video_path: videoPath
        }))
      }
    }, 500)
  }

  const handleStopProcessing = () => {
    if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
      websocketRef.current.send(JSON.stringify({
        type: 'stop_video'
      }))
    }
    
    if (websocketRef.current) {
      websocketRef.current.close()
    }
    
    setIsProcessing(false)
    setCurrentFrame(null)
    setFaceData(null)
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8">
          WebRTC Video Face Detection
        </h1>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex gap-4 items-center mb-4">
            <input
              type="text"
              value={videoPath}
              onChange={(e) => setVideoPath(e.target.value)}
              placeholder="Enter video file path (e.g., /path/to/video.mp4)"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={isProcessing ? handleStopProcessing : handleStartProcessing}
              className={`px-6 py-2 rounded-md text-white font-medium ${
                isProcessing
                  ? 'bg-red-500 hover:bg-red-600'
                  : 'bg-blue-500 hover:bg-blue-600'
              }`}
            >
              {isProcessing ? 'Stop' : 'Start Processing'}
            </button>
          </div>

          {isProcessing && (
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-green-600 font-medium">Processing video...</span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2 bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Video Stream</h2>
            <ErrorBoundary>
              <VideoPlayer 
                currentFrame={currentFrame}
                faceData={faceData}
                isProcessing={isProcessing}
              />
            </ErrorBoundary>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Face Detection Data</h2>
            <ErrorBoundary>
              <FaceDataDisplay 
                faceData={faceData}
                onFaceDataUpdate={setFaceData}
                isProcessing={isProcessing}
              />
            </ErrorBoundary>
          </div>
        </div>
      </div>
    </div>
  )
}