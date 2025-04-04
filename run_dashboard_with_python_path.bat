@echo off
cd /d %~dp0
echo Launching GHG Dashboard using specific Python path...

"C:\ProgramData\anaconda3\python.exe" -m streamlit run dashboard.py

pause
