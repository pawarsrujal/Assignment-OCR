@echo off
REM Batch script to run the Streamlit OCR PII Pipeline app

echo ============================================================
echo Starting OCR PII Pipeline Web App
echo ============================================================
echo.
echo Opening in browser...
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Run streamlit app
streamlit run app.py

pause
