@echo off
setlocal

if "%~1"=="" exit /b 2
if "%~2"=="" exit /b 3

set "SESSION=%~1"
set "URL=%~2"

npx.cmd --yes agent-browser --session "%SESSION%" open "%URL%"
