#!/bin/bash

echo ""
echo "========================================"
echo "   Eleutheria Desktop Trading App"
echo "========================================"
echo ""
echo "Starting Eleutheria Desktop Application..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Run the desktop application
python3 run_desktop.py

echo ""
echo "Application closed." 