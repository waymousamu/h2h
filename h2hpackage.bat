@echo off
REM
REM h2hpackage.bat
REM packaging script for deployment
REM
REM Mahesh Devendran, WebSphere Support, PID Team
REM Copyright(c) 2009, Euroclear
REM
REM


echo ***************************
echo Starting Jython packager...
echo ***************************

java -Dpython.path="lib" -jar lib\jython.jar %cd%\scripts\H2HPackageEngine.py %*
