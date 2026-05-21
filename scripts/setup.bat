@echo off

echo Starting WanderChina Map Backend Setup...

echo Installing dependencies...
poetry install

echo Creating .env file...
if not exist .env copy .env.example .env

echo Setup complete!
echo Run 'poetry run uvicorn app.main:app --reload' to start the server.

pause
