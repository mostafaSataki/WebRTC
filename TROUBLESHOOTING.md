# Troubleshooting Guide

## Frontend Issues

### Internal Server Error (localhost:3000)

The frontend has been fixed to handle common issues:

1. **Server-Side Rendering (SSR) Issues**: VideoPlayer component is now dynamically imported with `ssr: false` to avoid canvas-related errors during server-side rendering.

2. **Port Conflicts**: If port 3000 is in use, Next.js will automatically use the next available port (3001, 3002, etc.).

3. **Canvas Errors**: Added client-side checks to ensure canvas operations only run in the browser.

### Current Server Status

- **Frontend**: Running on http://localhost:3003 (or next available port)
- **Backend**: Should run on http://localhost:8000

### Quick Fix Steps

1. **Kill any conflicting processes**:
   ```bash
   # Check what's using port 3000
   netstat -ano | findstr :3000
   
   # Kill the process (replace PID with actual process ID)
   taskkill /PID <PID> /F
   ```

2. **Start fresh servers**:
   ```bash
   # Backend
   cd backend
   python server.py
   
   # Frontend (in new terminal)
   cd frontend
   npm run dev
   ```

3. **Check the correct URL**: The frontend will show the correct URL when it starts (might be 3001, 3002, etc.)

### Fixed Issues

✅ **Canvas SSR Error**: Fixed with dynamic imports and client-side checks
✅ **Component Loading**: Added loading states and error boundaries
✅ **Error Handling**: Added comprehensive error boundaries
✅ **Video Size**: Increased video display size (2/3 of screen width)

### Testing

1. Open the frontend URL shown in the terminal (e.g., http://localhost:3003)
2. You should see the WebRTC Face Detection interface
3. Enter a video file path to test functionality

### Error Boundaries

The app now includes error boundaries that will:
- Catch and display errors gracefully
- Provide "Try Again" buttons
- Log errors to console for debugging

### Common Solutions

- **Blank/Loading Screen**: Check browser console for errors
- **Port Issues**: Use the port shown in terminal output
- **Canvas Errors**: Cleared with SSR fixes
- **WebSocket Issues**: Ensure backend is running on port 8000