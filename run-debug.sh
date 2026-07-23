#!/bin/bash
# KosDWM startup script with debug output to terminal

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Run KosDWM with output to both terminal and file
echo "Starting KosDWM at $(date)" | tee run.out
python run.py 2>&1 | tee -a run.out
