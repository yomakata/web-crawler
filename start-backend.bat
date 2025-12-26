@echo off
cd /d c:\Projects\web-crawler\backend
call venv\Scripts\activate.bat
set FLASK_APP=api/app.py
set FLASK_ENV=development
python -m flask run --port=3000 --host=0.0.0.0
