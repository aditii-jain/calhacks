#!/bin/bash
set -e

echo "🔍 Python version check..."
python3 --version || python --version

echo "📦 Upgrading pip and installing dependencies..."
python3 -m pip install --upgrade pip setuptools wheel || python -m pip install --upgrade pip setuptools wheel

echo "📋 Installing requirements..."
python3 -m pip install -r requirements.txt || python -m pip install -r requirements.txt

echo "✅ Build complete!" 