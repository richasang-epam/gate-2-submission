@echo off
echo.
echo  Apex ETA Agent - Demo Dashboard
echo  ================================
echo  Gate 2 - Richa Sang - 2026-05-06
echo.
cd /d "%~dp0"
pip install -r requirements.txt -q
echo  Starting server on http://localhost:5000
echo  Press Ctrl+C to stop.
echo.
python run.py
