@echo off
rem Teach the local assistant a rule or fact. Nothing is sent anywhere; see TEACH.md.
cd /d "%~dp0"
"..\runtimes\cpython-3.12.16-20261110\python\python.exe" -B teach_store.py add
echo.
"..\runtimes\cpython-3.12.16-20261110\python\python.exe" -B teach_store.py list
pause
