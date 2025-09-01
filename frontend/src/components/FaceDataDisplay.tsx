'use client'

interface Face {
  x: number
  y: number
  width: number
  height: number
  confidence: number
}

interface FaceDataDisplayProps {
  faceData: Face[] | null
  onFaceDataUpdate: (data: Face[]) => void
  isProcessing: boolean
}

export default function FaceDataDisplay({ 
  faceData, 
  onFaceDataUpdate, 
  isProcessing 
}: FaceDataDisplayProps) {

  if (!isProcessing) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <div className="text-4xl mb-4">👤</div>
          <div>Face detection data will appear here when processing starts</div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Face Detection Data */}
      {!faceData && (
        <div className="flex items-center justify-center h-48 text-gray-500">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-400 mx-auto mb-4"></div>
            <div>Waiting for face detection data...</div>
          </div>
        </div>
      )}

      {faceData && (
        <div className="space-y-4">
          {/* Summary */}
          <div className="bg-gray-50 p-3 rounded">
            <div className="font-semibold">Faces Detected</div>
            <div className="text-lg">{faceData.length}</div>
          </div>

          {/* Face Details */}
          {faceData.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-semibold">Detected Faces:</h3>
              {faceData.map((face, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-3 text-sm">
                  <div className="font-medium mb-2">Face {index + 1}</div>
                  
                  <div className="grid grid-cols-2 gap-2 mb-2">
                    <div>
                      <span className="font-semibold">Confidence:</span> 
                      <span className="ml-1">{(face.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div>
                      <span className="font-semibold">Size:</span> 
                      <span className="ml-1">{face.width}x{face.height}</span>
                    </div>
                  </div>

                  <div className="text-xs text-gray-600">
                    <div><strong>Position:</strong></div>
                    <div>
                      x: {face.x}, y: {face.y}, 
                      w: {face.width}, h: {face.height}
                    </div>
                  </div>

                  {/* Confidence Bar */}
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${face.confidence * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* No Faces Detected */}
          {faceData.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <div className="text-3xl mb-2">😐</div>
              <div>No faces detected in current frame</div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}