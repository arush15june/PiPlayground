#!/usr/bin/env bash
if ! [ -d env/ ]; then
    echo  "Creating Virtual Environment"
    python3 -m venv env
    echo "Installing Libraries"
    env/bin/pip install -r src/requirements.txt
    echo "Activate environment with 'source env/bin/activate'"
fi
