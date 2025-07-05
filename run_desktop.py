#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Eleutheria Desktop App Launcher
Simple launcher for the Eleutheria trading desktop application
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

def check_config():
    """Check if the configuration file exists and is properly set up"""
    if not os.path.exists("config.py"):
        print("⚠️  Configuration file not found. Creating default config.py...")
        create_default_config()
    
    # Check if API keys are configured
    try:
        from config import API_KEY, API_SECRET, API_PASSPHRASE
        if (API_KEY == "VOTRE_API_KEY" or 
            API_SECRET == "VOTRE_API_SECRET" or 
            API_PASSPHRASE == "VOTRE_API_PASSPHRASE"):
            print("⚠️  API keys not configured in config.py")
            print("   Please edit config.py and add your Coinbase API credentials")
            return False
    except ImportError:
        print("❌ Error importing configuration")
        return False
    
    return True

def create_default_config():
    """Create a default configuration file"""
    config_content = '''# -*- coding: utf-8 -*-

"""
Configuration file for Eleutheria Trading Bot
Replace the placeholder values with your actual Coinbase API credentials
"""

# Coinbase API Configuration
API_KEY = "VOTRE_API_KEY"  # Replace with your Coinbase API key
API_SECRET = "VOTRE_API_SECRET"  # Replace with your Coinbase API secret
API_PASSPHRASE = "VOTRE_API_PASSPHRASE"  # Replace with your Coinbase API passphrase

# API URL
API_URL = "https://api.exchange.coinbase.com"

# Trading pair
HBAR_SYMBOL = "HBAR-USD"

# Trading Strategy Configuration
ZONES_ACHAT = [
    {"prix_max": 0.13, "prix_min": 0.12, "montant": 500, "pourcentage_capital": 0.10},
    {"prix_max": 0.12, "prix_min": 0.11, "montant": 750, "pourcentage_capital": 0.15},
    {"prix_max": 0.11, "prix_min": 0.10, "montant": 1000, "pourcentage_capital": 0.20},
    {"prix_max": 0.10, "prix_min": 0.09, "montant": 1500, "pourcentage_capital": 0.25},
    {"prix_max": 0.09, "prix_min": 0.00, "montant": 2000, "pourcentage_capital": 0.30}
]

ZONES_VENTE = [
    {"prix_min": 0.14, "pourcentage_benefices": 0.20},
    {"prix_min": 0.15, "pourcentage_benefices": 0.30},
    {"prix_min": 0.16, "pourcentage_benefices": 0.50},
    {"prix_min": 0.18, "pourcentage_benefices": 0.70},
    {"prix_min": 0.20, "pourcentage_benefices": 0.90}
]

STOP_LOSS_POURCENTAGE = 0.15
INTERVALLE_VERIFICATION_NORMAL = 1800
INTERVALLE_VERIFICATION_OPPORTUNITE = 300
UI_THEME = "dark"
UI_REFRESH_RATE = 30
'''
    
    with open("config.py", "w") as f:
        f.write(config_content)
    
    print("✅ Default config.py created")

def main():
    """Main launcher function"""
    print("🚀 Eleutheria Desktop Trading App")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        return
    
    # Check configuration
    if not check_config():
        print("\n📝 API keys not configured - running in DEMO MODE")
        print("   The app will show the interface but won't perform real trading")
        print("   To enable real trading, edit config.py with your API credentials")
        print()
    
    print("✅ All checks passed!")
    print("🎯 Starting Eleutheria Desktop App...")
    print()
    
    print("✅ All checks passed!")
    print("🎯 Starting Eleutheria Desktop App...")
    print()
    
    # Import and run the desktop app
    try:
        from eleutheria_desktop import main as run_app
        run_app()
    except ImportError as e:
        print(f"❌ Error importing desktop app: {e}")
        print("Make sure eleutheria_desktop.py exists in the current directory")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Error running desktop app: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main() 