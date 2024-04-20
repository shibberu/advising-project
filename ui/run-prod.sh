#!/bin/bash

source .env
source venv/bin/activate

if [ "$(lsof -t -i:5000)" ]; then
    echo "Port 5000 is in use. Killing process..."
    kill -9 $(lsof -t -i:5000)
fi

# Run in the background
nohup python ui.py prod > log-prod.txt 2>&1 &
