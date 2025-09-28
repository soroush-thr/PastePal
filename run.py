"""
Quick start script for PastePal
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_pyqt6():
    """Check if PyQt6 is working"""
    try:
        from PyQt6.QtCore import QCoreApplication
        from PyQt6.QtWidgets import QApplication
        return True
    except ImportError as e:
        print(f"PyQt6 import error: {e}")
        return False

def fix_pyqt6():
    """Try to fix PyQt6 installation"""
    print("Attempting to fix PyQt6 installation...")
    import subprocess
    
    try:
        # Install the working version
        subprocess.run([sys.executable, "-m", "pip", "install", "PyQt6==6.9.1"], check=True)
        print("✓ PyQt6 6.9.1 installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install PyQt6: {e}")
        return False

if __name__ == "__main__":
    # Check PyQt6 first
    if not check_pyqt6():
        print("PyQt6 is not working. Attempting to fix...")
        if fix_pyqt6():
            print("PyQt6 fixed. Restarting...")
            # Restart the script
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            print("Could not fix PyQt6. Please run:")
            print("pip install PyQt6==6.9.1")
            sys.exit(1)
    
    try:
        from pastepal.main import main
        sys.exit(main())
    except ImportError as e:
        print(f"Error importing PastePal: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting PastePal: {e}")
        sys.exit(1)
