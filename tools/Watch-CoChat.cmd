@echo off
rem Watches the shared co-chat log and shows a Windows notification on every new reply.
rem Fetch only: it never pulls, commits, pushes or talks to a model. Ctrl+C stops it.
cd /d "%~dp0.."
python -B tools\watch_cochat.py --toast --interval 60
pause
