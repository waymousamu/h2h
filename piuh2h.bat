@echo off
REM
REM piuh2h.bat
REM packaging script for deployment
REM
REM Mahesh Devendran, WebSphere Support, PID Team
REM Copyright(c) 2009, Euroclear
REM
REM
java -Dpython.path="lib" -jar lib\jython.jar %cd%\scripts\H2HRelease.py  %*
