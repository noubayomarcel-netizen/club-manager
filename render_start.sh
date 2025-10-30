#!/usr/bin/env bash

# Run migrations before starting the app
flask db upgrade

# Start the app
gunicorn app:app
