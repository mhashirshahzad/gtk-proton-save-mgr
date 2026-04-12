#!/bin/bash
# run.sh - Simple launcher

if [ ! -d "venv" ]; then
    echo "First time setup: Running make setup..."
    make setup
fi

source venv/bin/activate
python src/save-manager.py
