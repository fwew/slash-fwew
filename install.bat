@echo off

REM create python3 virtual environment
python -m venv venv

REM activate environment
venv\Scripts\activate

REM install dependencies
pip install -r requirements.txt
