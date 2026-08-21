@echo off
echo Building Python Plant Sim...

:: 1. Run PyInstaller (with a custom name for the exe)
pyinstaller --noconsole --onefile --add-data "assets;assets" --name "PythonPlantSim" main.py

:: 2. Clean up the messy leftovers
echo Cleaning up build folders...
rmdir /s /q build
del PythonPlantSim.spec

echo.
echo Build complete! Your game is inside the 'dist' folder.
pause