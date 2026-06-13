#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing project dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

echo "Pre-downloading PaddleOCR models to prevent timeout on first scan..."
python -c "from paddleocr import PaddleOCR; PaddleOCR(lang='en', show_log=False)"

echo "Build script execution complete!"
