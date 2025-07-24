@echo off
echo Starting NYC Taxi Fare Predictor Frontend...
cd /d "%~dp0frontend"
set PATH=%PATH%;C:\Program Files\nodejs
npm run dev
pause
