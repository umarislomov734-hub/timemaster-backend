@echo off
cd /d C:\Users\user\Desktop\xolmurod\timemaster
uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
