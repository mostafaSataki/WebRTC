'use client'

import { useEffect, useRef, useState } from 'react'

interface Face {
  x: number
  y: number
  width: number
  height: number
  confidence: number
}

interface VideoPlayerProps {
  currentFrame: string | null
  faceData: Face[] | null
  isProcessing: boolean
}

export default function VideoPlayer({ currentFrame, faceData, isProcessing }: VideoPlayerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const imageRef = useRef<HTMLImageElement>(null)
  
  useEffect(() => {
    if (currentFrame && canvasRef.current) {
      drawFrameWithFaces()
    }
  }, [currentFrame, faceData])

  const drawFrameWithFaces = () => {
    const canvas = canvasRef.current
    const image = imageRef.current
    
    if (!canvas || !image || !currentFrame) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    image.onload = () => {
      // Set canvas size to match image
      canvas.width = image.naturalWidth
      canvas.height = image.naturalHeight
      
      // Draw the image
      ctx.drawImage(image, 0, 0)
      
      // Draw face detection boxes
      if (faceData && faceData.length > 0) {
        ctx.strokeStyle = '#00ff00'
        ctx.lineWidth = 3
        ctx.font = '16px Arial'
        ctx.fillStyle = '#00ff00'
        
        faceData.forEach((face) => {
          // Draw rectangle
          ctx.strokeRect(face.x, face.y, face.width, face.height)
          
          // Draw confidence text
          const confidence = `${(face.confidence * 100).toFixed(1)}%`
          const textY = face.y > 20 ? face.y - 5 : face.y + face.height + 20
          ctx.fillText(confidence, face.x, textY)
        })
      }
    }
    
    image.src = currentFrame
  }

  return (
    <div className="space-y-4">
      <div className="relative bg-black rounded-lg overflow-hidden" style={{ paddingBottom: '56.25%' }}>
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full object-contain"
        />
        
        <img
          ref={imageRef}
          style={{ display: 'none' }}
          alt=""
        />
        
        {!isProcessing && (
          <div className="absolute inset-0 flex items-center justify-center text-white bg-gray-800">
            <div className="text-center">
              <div className="text-6xl mb-4">📹</div>
              <div className="text-lg">Video will appear here when processing starts</div>
            </div>
          </div>
        )}

        {isProcessing && !currentFrame && (
          <div className="absolute inset-0 flex items-center justify-center text-white bg-gray-800">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
              <div className="text-lg">Connecting to video stream...</div>
            </div>
          </div>
        )}
      </div>

      <div className="flex items-center gap-2 text-sm">
        <div className={`w-2 h-2 rounded-full ${
          currentFrame ? 'bg-green-500' : 'bg-red-500'
        }`}></div>
        <span className={currentFrame ? 'text-green-600' : 'text-red-600'}>
          {currentFrame ? 'Video Stream Active' : 'No Video Stream'}
        </span>
        {faceData && faceData.length > 0 && (
          <span className="text-blue-600 ml-4">
            {faceData.length} face{faceData.length !== 1 ? 's' : ''} detected
          </span>
        )}
      </div>
    </div>
  )
}