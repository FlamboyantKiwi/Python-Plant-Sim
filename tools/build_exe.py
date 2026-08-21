import os
import shutil
import PyInstaller.__main__

def build_game():
    print("Building Python Plant Sim...")
    
    # Run PyInstaller programmatically
    PyInstaller.__main__.run([
        'main.py',
        '--name=PythonPlantSim',
        '--onefile',
        '--console', ### or --noconsole to remove debug text!
        '--add-data=assets;assets',
        '--clean', # Tells PyInstaller to clean its internal cache
    ])

    # Clean up the local workspace
    print("\nCleaning up workspace...")
    
    # Remove the 'build' directory
    if os.path.exists("build"):
        shutil.rmtree("build")
        
    # Remove the .spec file
    if os.path.exists("PythonPlantSim.spec"):
        os.remove("PythonPlantSim.spec")

    print("\nSuccess! PythonPlantSim.exe is ready in the 'dist' folder.")

if __name__ == "__main__":
    build_game()