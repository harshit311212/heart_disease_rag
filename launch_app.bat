@echo off
echo Launching Heart Disease RAG Application...

:: Kill any existing processes on port 8000 to prevent stale code in memory
echo Cleaning up any stale backend processes on port 8000...
for /f "tokens=5" %%P in ('netstat -a -n -o 2^>nul ^| findstr ":8000 "') do (
    if not "%%P"=="0" (
        taskkill /F /PID %%P >nul 2>&1
    )
)
timeout /t 1 /nobreak >nul

:: Start Python FastAPI Backend in a new window (fresh process with latest code)
echo Starting Backend API...
start "Backend Server" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

:: Start React Vite Frontend in a new window
echo Starting Frontend React App...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

:: Wait for servers to boot, then open the browser
echo Waiting for servers to initialize (10s)...
timeout /t 10 /nobreak >nul

echo Opening browser...
start http://localhost:5173

echo Launch sequence complete!
