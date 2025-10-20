@echo off
setlocal

REM --- Application Runner Batch File (Windows .bat) ---
REM This script takes the name of a Python script (without the .py extension)
REM as the first argument, and executes it.

REM Check if an application name was provided
if "%1"=="" (
    echo Error: Missing application name argument.
    echo.
    echo Usage: 004_run.bat ^<AppName^> [^<Arg1^> ^<Arg2^> ...]
    echo Example 1: 004_run.bat main --mode=dev
    echo Example 2: 004_run.bat db_config_main QA TPS
    goto :eof
)

REM Construct the script file name
set SCRIPT_NAME=%1.py

REM Check if the script file exists
if not exist "%SCRIPT_NAME%" (
    echo Error: Python script "%SCRIPT_NAME%" not found in the current directory.
    echo.
    echo Ensure %SCRIPT_NAME% exists and is correctly named.
    goto :eof
)

REM Define the application script path and shift parameters
set APP_PATH=%~dp0%SCRIPT_NAME%

REM NOTE on parameter passing: Due to observed shell behavior (likely PowerShell or specific Windows cmd versions),
REM the argument intended for the script name is sometimes duplicated in %*. 
REM We rely on the Python script (db_config_main.py) to ignore the extra argument at index 1.
REM We are using SHIFT here, but the python script is designed to compensate.

REM Shift the first argument (the app name) so the remaining arguments
REM are passed correctly to the Python script.
shift

REM Execute the Python script with all remaining arguments
REM The extra argument (e.g., 'db_config_main') is incorrectly repeated here by some shells,
REM but the Python script 'db_config_main.py' is updated to expect and ignore it.
echo Running: python "%APP_PATH%" %*
echo ------------------------------------------------------------------------
python "%APP_PATH%" %*

REM Check for Python execution errors (optional, but good practice)
if errorlevel 1 (
    echo.
    echo ERROR: Python script execution failed with exit code %errorlevel%.
)

endlocal
