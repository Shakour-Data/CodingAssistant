import os
import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Install Python requirements"""
    print("Installing Python requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Requirements installed successfully!")

def create_directories():
    """Create necessary directories"""
    dirs = [
        'app/models',
        'app/models/downloads',
        'app/models/running',
        'app/static/css',
        'app/static/js',
        'app/templates'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")

def main():
    print("Setting up Code Assistant...")
    
    # Create directories
    create_directories()
    
    # Install requirements
    install_requirements()
    
    print("\nSetup completed successfully!")
    print("\nTo run the application:")
    print("1. Set environment variables (optional):")
    print("   set FLASK_DEBUG=True")
    print("   set PORT=5000")
    print("\n2. Run the application:")
    print("   python run.py")
    print("\n3. Open your browser and go to:")
    print("   http://localhost:5000")

if __name__ == "__main__":
    main()
