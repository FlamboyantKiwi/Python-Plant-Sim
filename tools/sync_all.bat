@echo off
TITLE Master Project Sync

:: Force the terminal to the project root, regardless of where this is clicked from
cd /d "%~dp0.."

echo [1/2] Running Master Build Pipeline (Enums, Ghosts, UMLs, and Diagrams)...
python tools\base_generator.py

echo.
echo [2/2] Syncing to Wiki...
python tools\update_wiki.py ..\Python-Plant-Sim.wiki

echo.
echo ==========================================
echo [SUCCESS] Entire project is synced and ready for commit!
pause