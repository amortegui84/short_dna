@echo off
rem Starts the shorts-factory desktop app (needs: cd app && npm install once)
cd /d "%~dp0app"
npx electron .
