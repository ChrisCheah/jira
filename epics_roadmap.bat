@echo off
set activatepython=%~dp0\env\Scripts\activate.bat
set deactivatepython=%~dp0\env\Scripts\deactivate.bat
set python=%~dp0\env\Scripts\python.exe
set epics_script=%python% %~dp0\epics_roadmap.py
echo %epics_script%
@REM %activatepython%
%epics_script%
@REM %deactivatepython%
