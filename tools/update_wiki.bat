@echo off
TITLE Sync Wiki Diagrams

:: Navigates two levels up to find the parallel wiki folder
set WIKI_PATH=..\..\Python-Plant-Sim.wiki

echo [INFO] Running Wiki Diagram Sync...
python update_wiki.py %WIKI_PATH%

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Wiki sync failed!
    pause
    exit /b %errorlevel%
)

echo.
echo [SUCCESS] Wiki sync completed successfully!
pause