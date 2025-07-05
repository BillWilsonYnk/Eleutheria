#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Launcher for Eleutheria Airbnb-Style Desktop Trading App
"""

import sys
import os
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_tkinter():
    """Check if tkinter is available"""
    try:
        import tkinter
        print("✅ Tkinter is available")
        return True
    except ImportError:
        print("❌ Tkinter is not available")
        print("   On macOS, install with: brew install python-tk")
        print("   On Ubuntu/Debian: sudo apt-get install python3-tk")
        print("   On Windows: Tkinter should be included with Python")
        return False

def check_pillow():
    """Check if Pillow is available"""
    try:
        import PIL
        print("✅ Pillow is available")
        return True
    except ImportError:
        print("❌ Pillow is not available")
        print("   Install with: pip install Pillow")
        return False

def check_requests():
    """Check if requests is available"""
    try:
        import requests
        print("✅ Requests is available")
        return True
    except ImportError:
        print("❌ Requests is not available")
        print("   Install with: pip install requests")
        return False

def check_config():
    """Check if config file exists and API keys are configured"""
    try:
        from config import API_KEY, API_SECRET, API_PASSPHRASE
        if API_KEY == "VOTRE_API_KEY" or API_SECRET == "VOTRE_API_SECRET" or API_PASSPHRASE == "VOTRE_API_PASSPHRASE":
            print("⚠️  API keys not configured in config.py")
            print("   Please edit config.py and add your Coinbase API credentials")
            print("📝 API keys not configured - running in DEMO MODE")
            print("   The app will show the interface but won't perform real trading")
            print("   To enable real trading, edit config.py with your API credentials")
            return True
        else:
            print("✅ API keys are configured")
            return True
    except ImportError:
        print("⚠️  config.py not found - running in DEMO MODE")
        print("   Create config.py with your Coinbase API credentials for real trading")
        return True

def check_dependencies():
    """Check all required dependencies"""
    print("🔍 Checking dependencies...")
    
    checks = [
        check_python_version(),
        check_tkinter(),
        check_pillow(),
        check_requests(),
        check_config()
    ]
    
    return all(checks)

def run_app():
    """Run the Airbnb-style desktop app"""
    try:
        print("🎯 Starting Eleutheria Airbnb-Style Desktop App...")
        
        # Import and run the app
        from eleutheria_airbnb_style import main
        main()
        
    except ImportError as e:
        print(f"❌ Error importing Airbnb-style desktop app: {e}")
        print("Make sure eleutheria_airbnb_style.py exists in the current directory")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Error running Airbnb-style desktop app: {e}")
        input("Press Enter to exit...")

def main():
    """Main launcher function"""
    print("🚀 Eleutheria Airbnb-Style Desktop Trading App")
    print("=" * 50)
    print("🎨 Airbnb-Inspired Design")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Some dependencies are missing. Please install them and try again.")
        input("Press Enter to exit...")
        return
    
    print("\n✅ All checks passed!")
    
    # Run the app
    run_app()

if __name__ == "__main__":
    main() 