#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Eleutheria Modern Desktop App Launcher
Launcher for the Material Design version of the Eleutheria trading desktop application
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['requests', 'PIL']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Installing dependencies...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please run:")
            print("   pip install -r requirements.txt")
            return False
    
    return True

def check_tkinter():
    """Check if tkinter is available"""
    try:
        import tkinter
        print("✅ Tkinter is available")
        return True
    except ImportError:
        print("❌ Tkinter is not available")
        print("   On macOS, install it with: brew install python-tk")
        return False

def main():
    """Main launcher function"""
    print("🚀 Eleutheria Modern Desktop Trading App")
    print("=" * 50)
    print("🎨 Material Design Interface")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        return
    
    # Check tkinter
    if not check_tkinter():
        input("Press Enter to exit...")
        return
    
    print("✅ All checks passed!")
    print("🎯 Starting Eleutheria Modern Desktop App...")
    print()
    
    # Import and run the modern desktop app
    try:
        from eleutheria_desktop_modern import main as run_app
        run_app()
    except ImportError as e:
        print(f"❌ Error importing modern desktop app: {e}")
        print("Make sure eleutheria_desktop_modern.py exists in the current directory")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Error running modern desktop app: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main() 