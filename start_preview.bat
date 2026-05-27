@echo off
echo Starting preview server...
start http://localhost:3000
python -m http.server 3000
pause