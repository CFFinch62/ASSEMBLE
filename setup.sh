#!/bin/bash
VENV_DIR="venv"
echo "Setting up ASSEMBLE..."
python3 -m venv "$VENV_DIR"
[ $? -ne 0 ] && echo "Error: Failed to create virtual environment." && exit 1
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
[ $? -ne 0 ] && echo "Error: Failed to install requirements." && exit 1
echo "Setup complete. Run './run.sh' to start ASSEMBLE."
