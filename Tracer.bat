@echo off
setlocal

set SERVER_HOST=127.0.0.1
set SERVER_PORT=8000
set UI_PORT=3000

echo.
echo Starting Tracer...
echo   API:  http://%SERVER_HOST%:%SERVER_PORT%/docs
echo   UI:   http://localhost:%UI_PORT%
echo.

REM Launch backend in a new window
start "Tracer Backend" cmd /k ""%~dp0Tracer-Backend.bat""

REM Small delay so the API has time to start before the UI connects
timeout /t 3 /nobreak >nul

REM Launch frontend in a new window
start "Tracer Frontend" cmd /k ""%~dp0Tracer-Frontend.bat""

endlocal
