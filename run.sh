#!/bin/bash
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Running setup..."
    chmod +x ./setup.sh && ./setup.sh
    [ $? -ne 0 ] && echo "Setup failed." && exit 1
fi
source "$VENV_DIR/bin/activate"
python3 -m assemble.main
