@echo off
REM Multi-Agent Framework Setup Script for Windows

echo Setting up Multi-Agent Framework...

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -e ".[dev]"

REM Setup pre-commit hooks
echo Setting up pre-commit hooks...
pre-commit install

REM Copy environment file
if not exist ".env" (
    echo Creating environment file...
    copy .env.example .env
    echo Please edit .env with your API keys
)

REM Create initial directories
echo Creating additional directories...
mkdir logs 2>nul
mkdir cache 2>nul
mkdir screenshots 2>nul

REM Run initial tests
echo Running initial tests...
pytest tests/unit --verbose

echo Setup complete!
echo.
echo Next steps:
echo 1. Edit .env with your API keys
echo 2. Run: venv\Scripts\activate.bat
echo 3. Test: python -m src.cli list-agents
echo 4. Start building your agents!
