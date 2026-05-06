import traceback
import os
import sys

print("Current working directory:", os.getcwd())
try:
    from src.phase_4_ui.server import app
    print("App imported successfully!")
except Exception as e:
    print("Error importing app:")
    traceback.print_exc()
