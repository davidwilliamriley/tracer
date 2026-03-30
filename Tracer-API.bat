@echo off
setlocal

set SERVER_HOST=127.0.0.1
set SERVER_PORT=8000
set DOCS_URL=http://%SERVER_HOST%:%SERVER_PORT%/docs

REM Run from the API folder so module imports resolve correctly
cd /d "%~dp0graph-api"

echo.
echo API docs:
echo %DOCS_URL%
echo.

REM Prefer project virtual environment Python if present
if exist "..\.venv\Scripts\python.exe" (
    "..\.venv\Scripts\python.exe" -m uvicorn main:app --reload --host %SERVER_HOST% --port %SERVER_PORT%
) else (
    python -m uvicorn main:app --reload --host %SERVER_HOST% --port %SERVER_PORT%
)

endlocal
