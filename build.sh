#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing project dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

echo "Build script execution complete!"
