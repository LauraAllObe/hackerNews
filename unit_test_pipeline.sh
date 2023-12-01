#!/bin/bash

#go to project directory
cd /home/lauraallobe/hackerNews

# Activate the virtual environment
source venv/bin/activate

# Run pylint on your project files
pylint run.py hackernews/models.py hackernews/routes.py hackernews/__init__.py hackernews/test_models.py hackernews/test_routes.py

# Run pytest with coverage
coverage run --source=hackernews -m pytest test_models.py test_routes.py
coverage report
