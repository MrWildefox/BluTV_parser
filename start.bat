@echo off
setlocal enabledelayedexpansion

:: Scan current directory for .csv files
set /a index=0
for %%f in (*.csv) do (
    set /a index+=1
    set "file[!index!]=%%f"
)

:: Display menu
echo Please select a CSV file to process:
for /l %%i in (1,1,%index%) do (
    echo %%i. !file[%%i]!
)

:: Get user selection
set /p choice=Enter the number of the file you want to process: 

:: Validate user selection
if !choice! gtr %index% (
    echo Invalid selection.
    exit /b
)

:: Run the command with the selected file
set "selected_file=!file[%choice%]!"
echo Running command: python start.py %selected_file%
python start.py %selected_file%

endlocal
pause