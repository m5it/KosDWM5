#!/bin/bash
# KosDWM startup script with debug output

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Run KosDWM and redirect all output to run.out
echo "Starting KosDWM at $(date)" > run.out
python run.py >> run.out 2>&1 &

echo "KosDWM started. Output logged to run.out"
echo "To view output: tail -f run.out"
