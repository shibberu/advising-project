#!/bin/bash

source .env
source venv/bin/activate

if [ "$(lsof -t -i:5001)" ]; then
    echo "Port 5001 is in use. Killing process..."
    kill -9 $(lsof -t -i:5001)
fi

# Run in the background
nohup python ui.py test > log-test.txt 2>&1 &