@echo off
REM Run a SphereForge command with the CUDA build environment configured.
REM
REM gsplat's CUDA kernels are compiled on first use and need nvcc (from the
REM local toolkit fetched by scripts/fetch_cuda_toolkit.py), cl.exe and ninja
REM (from Visual Studio Build Tools). This wrapper puts all of them on PATH so
REM that ``sphereforge`` commands can render with the real rasteriser.
REM
REM Usage:  scripts\sphereforge_env.bat python -m sphereforge.cli process ...
setlocal

set "REPO=%~dp0.."
set "VCVARS=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat"

if exist "%VCVARS%" (
    call "%VCVARS%" >nul 2>&1
) else (
    echo [warn] vcvars64.bat not found; gsplat JIT builds will fail. >nul
)

set "CUDA_HOME=%REPO%\.cuda-toolkit\cuda"
if exist "%CUDA_HOME%\bin\nvcc.exe" (
    set "CUDA_PATH=%CUDA_HOME%"
    set "PATH=%CUDA_HOME%\bin;%CUDA_HOME%\nvvm\bin;%PATH%"
)

if not exist "%REPO%\.build-tmp" mkdir "%REPO%\.build-tmp"
set "TMP=%REPO%\.build-tmp"
set "TEMP=%REPO%\.build-tmp"
set "TORCH_EXTENSIONS_DIR=%REPO%\.torch-ext"
set "TORCH_CUDA_ARCH_LIST=8.9"
set "DISTUTILS_USE_SDK=1"
set "MAX_JOBS=4"
set "PATH=%REPO%\.venv\Scripts;%PATH%"
set "PYTHONPATH=%REPO%\src;%PYTHONPATH%"

if "%1"=="" (
    echo Usage: scripts\sphereforge_env.bat ^<command^> [args...]
    exit /b 2
)

%*
exit /b %errorlevel%