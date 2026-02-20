import PyInstaller.__main__
import sys
import os

os.chdir(r"c:\Users\prasa\OneDrive\Desktop\kaushik mini")

print("Building BuildingEstimator.exe...")
print("This may take 2-3 minutes...")
print()

try:
    PyInstaller.__main__.run([
        'app.py',
        '--onefile',
        '--hidden-import=flask',
        '--add-data=templates;templates',
        '--name=BuildingEstimator',
        '--distpath=dist',
        '--buildpath=build',
        '--specpath=specs'
    ])
    
    if os.path.exists(r"dist\BuildingEstimator.exe"):
        print("\n" + "="*50)
        print("SUCCESS! BuildingEstimator.exe created")
        print("="*50)
        print()
        print("Location: dist/BuildingEstimator.exe")
        print()
        print("You can now:")
        print("1. Copy BuildingEstimator.exe to other systems")
        print("2. Double-click to run (no installation needed)")
        print("3. Share via email or USB")
    else:
        print("Build completed but exe not found")
except Exception as e:
    print(f"Error: {e}")
