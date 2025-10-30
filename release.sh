#!/bin/bash

# Exit on error
set -e

echo "Running migrations..."
python manage.py migrate --no-input

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Release tasks completed!"