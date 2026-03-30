@echo off
setlocal

set UI_PORT=3000
set UI_URL=http://localhost:%UI_PORT%

REM Run from the UI folder
cd /d "%~dp0tracer-ui"

echo.
echo UI: %UI_URL%
echo.

REM Install packages if node_modules is missing
if not exist "node_modules" (
    echo Installing npm packages...
    npm install
)

npm run dev

endlocal
