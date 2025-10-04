@echo off
echo ========================================
echo   Starting Manufacturing Defects App
echo ========================================
echo.

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if activation was successful
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Make sure .venv exists in the current directory
    pause
    exit /b 1
)

echo [2/3] Virtual environment activated successfully!
echo.

REM Change to the cvicenie_L3 directory where the app is located
echo [3/3] Starting Streamlit application...
cd cvicenie_L3

REM Run streamlit application
streamlit run data_viz.py --server.port 8501 --server.address localhost

REM If streamlit fails, show error message
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start Streamlit application
    echo Make sure streamlit is installed: pip install streamlit
    pause
)

echo.
echo Application stopped.
pause