@echo off
echo ============================================
echo   NEMESIS — Environment Setup
echo ============================================
echo.
echo Choose setup method:
echo   1. Local (venv + conda)
echo   2. Docker
echo.
set /p choice="Enter 1 or 2: "

if "%choice%"=="2" goto docker

:local
echo.
echo [LOCAL SETUP]
cd /d E:\Projects\Nemesis

echo [1/4] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/4] Installing llama-cpp-python (CUDA 12.4 pre-built, works on 12.6)...
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124

echo [3/4] Installing other dependencies...
pip install colorama==0.4.6

echo [4/4] Verifying...
python -c "from llama_cpp import Llama; print('[OK] llama-cpp-python loaded')"

echo.
echo ============================================
echo   Done. Run: python main.py
echo ============================================
goto end

:docker
echo.
echo [DOCKER SETUP]
echo Prerequisites:
echo   - Docker Desktop installed and running
echo   - NVIDIA Container Toolkit installed
echo   - Model file in: core\model\
echo.
echo Building image...
docker build -t nemesis-ai .
echo.
echo Running Nemesis...
docker compose up

:end
pauseaaaaa