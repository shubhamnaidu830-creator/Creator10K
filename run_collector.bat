@echo off

echo =================================
echo Creator10K Subscriber Collector
echo =================================

cd /d "%~dp0"

echo.
echo Project folder:
cd

echo.
echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Running collector...
python collect_youtube.py

echo.
echo =================================
echo COLLECTOR FINISHED
echo =================================
echo.

pause