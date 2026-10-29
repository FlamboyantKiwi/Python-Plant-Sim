@echo off
TITLE Clean Project Cache

echo Scrubbing pycache directories...
FOR /d /r . %%d in (pycache) DO @IF EXIST "%%d" rd /s /q "%%d"

echo Scrubbing PyInstaller artifacts...
IF EXIST "build" rd /s /q "build"
IF EXIST "dist" rd /s /q "dist"
IF EXIST "PythonPlantSim.spec" del /q "PythonPlantSim.spec"

echo.
echo ==========================================
echo [SUCCESS] Workspace is clean!
echo ==========================================
pause