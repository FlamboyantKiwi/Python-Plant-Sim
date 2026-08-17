@echo off
:: ========================================================
:: Plant Sim Diagram Automation Script
:: This batch file acts as a shortcut wrapper to run the 
:: Python diagram generator located in the tools folder.
:: ========================================================

:: Step 1: Navigate from the 'tools' folder up to the main project root
cd ..

:: Step 2: Execute the all-in-one Python generation and cleanup script
python tools\generate_diagrams.py

:: Step 3: Print a visual separator and pause so the user can see the success message
echo.
echo ========================================================
pause