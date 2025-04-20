@echo off
echo Setting up virtual environment for QA System using Gemini Pro API...

:: Create virtual environment
python -m venv venv
if %ERRORLEVEL% neq 0 (
    echo Failed to create virtual environment.
    exit /b %ERRORLEVEL%
)

:: Activate virtual environment
call venv\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment.
    exit /b %ERRORLEVEL%
)

:: Install dependencies
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install dependencies.
    exit /b %ERRORLEVEL%
)

:: Create .env file from example if it doesn't exist
if not exist .env (
    copy .env.example .env
    echo Created .env file from .env.example. Please edit it to add your API key.
) else (
    echo .env file already exists. Make sure it contains your API key.
)

echo.
echo Setup completed successfully!
echo.
echo To run the application:
echo 1. Make sure your virtual environment is activated (you should see (venv) at the beginning of your command prompt)
echo 2. Run: streamlit run app.py
echo.
echo To deactivate the virtual environment when done, run: deactivate
echo.
