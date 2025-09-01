@echo off
echo Starting WebRTC Face Detection Backend...
cd backend

call .venv\Scripts\activate.bat

python server.py