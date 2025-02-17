#!/bin/bash

# Navigate to the directory containing the API server code
cd "$(dirname "$0")/src"

# Activate the virtual environment if needed
if [ -d "../venv" ]; then
  source ../venv/bin/activate
fi

# Start the API server
exec python3 main.py