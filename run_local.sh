#!/bin/bash
# Script to run the backend locally without Docker

echo "==> 1. Setting up Python environment"
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt

echo "==> 2. Checking for MongoDB"
if ! nc -z localhost 27017 2>/dev/null; then
    echo "MongoDB is not running on localhost:27017."
    echo "Starting a local MongoDB container..."
    # Try to start mongo via docker
    docker start local-mongo || docker run -d -p 27017:27017 --name local-mongo mongo:6.0
else
    echo "MongoDB is already running."
fi

echo "==> 3. Checking for LaTeX"
if ! command -v pdflatex &> /dev/null; then
    echo "WARNING: pdflatex not found! PDF generation will fail."
    echo "Run: sudo apt-get install -y texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra"
    echo "Or press Ctrl+C to cancel and install it."
    sleep 3
fi

echo "==> 4. Starting the server..."
export NVIDIA_API_KEY="${NVIDIA_API_KEY:-nvapi-YOUR_KEY_HERE}"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
