@echo off
REM Batch script to run the OCR PII Pipeline on Windows

echo ============================================================
echo OCR PII Extraction and Redaction Pipeline
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)

REM Default parameters
set INPUT_DIR=examples
set OUTPUT_DIR=out
set MIN_CONF=0.4
set REDACT_FLAG=

REM Parse command line arguments
:parse_args
if "%~1"=="" goto end_parse
if "%~1"=="--input" (
    set INPUT_DIR=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--output" (
    set OUTPUT_DIR=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--min_confidence" (
    set MIN_CONF=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--redact" (
    set REDACT_FLAG=--redact
    shift
    goto parse_args
)
if "%~1"=="--help" (
    goto show_help
)
shift
goto parse_args

:end_parse

echo Configuration:
echo   Input folder:  %INPUT_DIR%
echo   Output folder: %OUTPUT_DIR%
echo   Min confidence: %MIN_CONF%
echo   Redaction: %REDACT_FLAG%
echo.
echo Starting pipeline...
echo ============================================================
echo.

REM Run the pipeline
python run_pipeline.py --input %INPUT_DIR% --output %OUTPUT_DIR% --min_confidence %MIN_CONF% %REDACT_FLAG%

echo.
echo ============================================================
echo Pipeline completed!
echo Check output in: %OUTPUT_DIR%
echo ============================================================
pause
exit /b 0

:show_help
echo Usage: run_pipeline.bat [OPTIONS]
echo.
echo Options:
echo   --input DIR           Input folder with images (default: examples)
echo   --output DIR          Output folder for results (default: out)
echo   --min_confidence NUM  Confidence threshold 0.0-1.0 (default: 0.4)
echo   --redact             Enable image redaction
echo   --help               Show this help message
echo.
echo Examples:
echo   run_pipeline.bat
echo   run_pipeline.bat --input images --output results --redact
echo   run_pipeline.bat --min_confidence 0.6 --redact
pause
exit /b 0
