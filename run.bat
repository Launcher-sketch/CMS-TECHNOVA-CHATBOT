
@echo off
title CMS TECHNOVA 2026

cd /d "%~dp0"

echo =====================================
echo       CMS TECHNOVA 2026
echo       EVENTS ASSISTANT
echo =====================================

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing requirements...
python -m pip install -r requirements.txt

echo.
echo Starting CMS Events Assistant...
echo Open http://127.0.0.1:5000 in your browser.
echo.

python app.py

pause
