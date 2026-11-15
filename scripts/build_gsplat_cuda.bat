@echo off
REM Build the gsplat CUDA rasteriser extension (JIT) on Windows.
REM
REM gsplat ships no prebuilt Windows binaries, so its CUDA kernels are
REM compiled on first use. That needs three things this script wires up:
REM   * nvcc            -- from a local CUDA toolkit (see scripts/fetch_cuda_toolkit.py)
REM   * cl.exe + ninja  -- from the Visual Studio Build Tools (vcvars64.bat)
REM   * a build cache   -- kept inside the repo so rebuilds are cheap
REM
REM Usage:  scripts\build_gsplat_cuda.bat
setlocal

set "REPO=%~dp0.."
set "VCVARS=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat"

if not exist "%VCVARS%" (
    echo [error] Visual Studio Build Tools not found at "%VCVARS%"
    echo         Install "Build Tools for Visual Studio" with the C++ workload.
    exit /b 1
)

call "%VCVARS%" >nul 2>&1
if errorlevel 1 (
    echo [error] vcvars64.bat failed
    exit /b 1
)

set "CUDA_HOME=%REPO%\.cuda-toolkit\cuda"
if not exist "%CUDA_HOME%\bin\nvcc.exe" (
    echo [error] CUDA toolkit not found at "%CUDA_HOME%"
    echo         Run: python scripts\fetch_cuda_toolkit.py
    exit /b 1
)

set "CUDA_PATH=%CUDA_HOME%"
REM nvcc shells out to cicc.exe, which lives in nvvm\bin rather than bin\.
set "PATH=%CUDA_HOME%\bin;%CUDA_HOME%\nvvm\bin;%REPO%\.venv\Scripts;%PATH%"
set "MAX_JOBS=4"
set "TORCH_CUDA_ARCH_LIST=8.9"
set "TORCH_EXTENSIONS_DIR=%REPO%\.torch-ext"
set "DISTUTILS_USE_SDK=1"

REM nvcc writes intermediate files to TMP; the default user temp dir is not
REM always writable from a build shell, so keep intermediates inside the repo.
if not exist "%REPO%\.build-tmp" mkdir "%REPO%\.build-tmp"
set "TMP=%REPO%\.build-tmp"
set "TEMP=%REPO%\.build-tmp"

"%REPO%\.venv\Scripts\python.exe" "%REPO%\scripts\check_gsplat_cuda.py"
exit /b %errorlevel%