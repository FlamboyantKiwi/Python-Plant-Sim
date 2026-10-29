@echo off
TITLE Master Project Sync
echo [1/3] Running Base Generators (Enums, Ghosts, UML)...
python tools\base_generator.py

echo.
echo [2/3] Generating Architecture Diagrams...
call tools\update_diagrams.bat

echo.
echo [3/3] Syncing to Wiki...
call tools\update_wiki.bat

echo.
echo ==========================================
echo [SUCCESS] Entire project is synced and ready for commit!
pause