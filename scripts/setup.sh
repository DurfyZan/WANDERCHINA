#!/bin/bash

set -e

echo "Starting WanderChina Map Backend Setup..."

if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

echo "Installing dependencies..."
poetry install

echo "Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env file created. Please fill in your API keys."
fi

echo "Running database migrations..."
poetry run alembic upgrade head

echo "Setup complete!"
echo "Run 'poetry run uvicorn app.main:app --reload' to start the server."
