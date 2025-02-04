@echo off
SETLOCAL

:: Change to project root directory
cd /d %~dp0\..

:: Clean previous builds
echo Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

:: Install dependencies if needed
poetry install

:: Create single file executable
echo Building executable...
poetry run pyinstaller src/cli.py ^
    --name nimbasms ^
    --onefile ^
    --clean ^
    --add-data "src/core;core" ^
    --add-data "src/commands;commands" ^
    --add-data "src/config;config" ^
    --add-data "src/utils;utils" ^
    --hidden-import typer ^
    --hidden-import rich ^
    --hidden-import httpx

:: Check if build was successful
if exist dist\nimbasms.exe (
    echo Build successful!
    echo Executable created at: dist\nimbasms.exe
) else (
    echo Build failed!
    exit /b 1
)