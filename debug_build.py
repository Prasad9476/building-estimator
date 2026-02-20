import subprocess
import sys
import os

os.chdir(r"c:\Users\prasa\OneDrive\Desktop\kaushik mini")

print("=" * 50)
print("Building BuildingEstimator.exe")
print("=" * 50)
print()

cmd = [
    sys.executable,
    "-m", "PyInstaller",
    "--onefile",
    "--add-data", "templates;templates",
    "--name", "BuildingEstimator",
    "--hidden-import=flask",
    "--hidden-import=werkzeug",
    "--hidden-import=jinja2",
    "app_exe.py"
]

print("Running:", " ".join(cmd))
print()

result = subprocess.run(cmd, capture_output=True, text=True)

if result.stdout:
    print("STDOUT:")
    print(result.stdout)
    
if result.stderr:
    print("STDERR:")
    print(result.stderr)

print()
print("Return code:", result.returncode)

if os.path.exists("dist/BuildingEstimator.exe"):
    print()
    print("=" * 50)
    print("SUCCESS! buildingEstimator.exe created!")
    print("=" * 50)
    print("Location: dist/BuildingEstimator.exe")
    size = os.path.getsize("dist/BuildingEstimator.exe")
    print(f"Size: {size / 1024 / 1024:.2f} MB")
else:
    print()
    print("ERROR: exe not created")
    if os.path.exists("dist"):
        print("dist folder contents:")
        print(os.listdir("dist"))
