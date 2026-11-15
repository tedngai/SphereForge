"""Assemble a local CUDA toolkit from conda packages (no admin rights needed).

gsplat has no prebuilt Windows binaries: its CUDA kernels are JIT-compiled on
first use, which requires ``nvcc`` plus the CUDA headers and NVVM libraries.
The official NVIDIA installer needs elevation, so this script instead downloads
the individual conda packages from the ``nvidia`` channel and lays them out as a
standard ``CUDA_HOME`` that ``scripts/build_gsplat_cuda.bat`` can use.

The layout produced is::

    .cuda-toolkit/cuda/
        bin/            nvcc.exe, ptxas.exe, cudafe++.exe, cudart DLLs
        nvvm/bin/       cicc.exe (nvcc shells out to this; must be on PATH)
        nvvm/libdevice/ libdevice.10.bc
        include/        cuda_runtime.h, crt/, nv/, thrust/, cub/
        lib/x64/        nvrtc.lib

Usage:
    python scripts/fetch_cuda_toolkit.py [--dest PATH] [--cuda-version 12.6]
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import tarfile
import urllib.request
from pathlib import Path

CHANNEL = "nvidia"
# (label, subdir, package filename). Versions are pinned so the headers, nvcc
# and NVVM compiler all come from one CUDA release. The label varies because
# NVIDIA did not publish every package under every 12.6.x label.
DEFAULT_PACKAGES: tuple[tuple[str, str, str], ...] = (
    # nvcc driver + host compiler front-end
    ("cuda-12.6.0", "win-64", "cuda-nvcc-tools-12.6.20-0.tar.bz2"),
    ("cuda-12.6.0", "noarch", "cuda-nvcc-dev_win-64-12.6.20-0.tar.bz2"),
    # NVVM back-end (cicc) and libdevice bitcode
    ("cuda-12.6.0", "win-64", "cuda-nvvm-tools-12.6.20-0.tar.bz2"),
    ("cuda-12.6.0", "win-64", "cuda-nvvm-impl-12.6.20-0.tar.bz2"),
    ("cuda-12.6.0", "win-64", "cuda-crt-tools-12.6.20-0.tar.bz2"),
    # headers
    ("cuda-12.6.0", "win-64", "cuda-crt-12.6.20-0.tar.bz2"),
    ("cuda-12.6.0", "noarch", "cuda-crt-dev_win-64-12.6.20-0.tar.bz2"),
    ("cuda-12.6.0", "noarch", "cuda-cudart-dev_win-64-12.6.37-0.tar.bz2"),
    ("cuda-12.6.0", "win-64", "cuda-cudart-12.6.37-0.tar.bz2"),
    ("cuda-12.6.0", "win-64", "cuda-cudart-static-12.6.37-0.tar.bz2"),
    # CCCL (nv/target, thrust, cub) -- required by cuda_fp16.h and torch.
    # Only published under the cuda-12.6.1 label.
    ("cuda-12.6.1", "noarch", "cuda-cccl_win-64-12.6.37-0.tar.bz2"),
    # NVRTC
    ("cuda-12.6.0", "win-64", "cuda-nvrtc-12.6.20-0.tar.bz2"),
    ("cuda-12.6.0", "win-64", "cuda-nvrtc-dev-12.6.20-0.tar.bz2"),
)

CUDA_VERSION = "12.6.20"


def _download(url: str, timeout: int = 900) -> bytes:
    """Fetch *url* and return the raw bytes."""
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read()


def _extract(data: bytes, dest: Path) -> None:
    """Extract a ``.tar.bz2`` conda package into *dest*."""
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:bz2") as archive:
        archive.extractall(dest, filter="data")


def _assemble_layout(staging: Path, cuda_home: Path) -> None:
    """Turn the extracted conda tree into a standard ``CUDA_HOME`` layout."""
    library = staging / "Library"
    for sub in ("bin", "include", "lib/x64", "nvvm/bin", "nvvm/libdevice"):
        (cuda_home / sub).mkdir(parents=True, exist_ok=True)

    # Executables and runtime DLLs.
    for pattern in ("*.exe", "*.dll"):
        for src in (library / "bin").glob(pattern):
            (cuda_home / "bin" / src.name).write_bytes(src.read_bytes())

    # Headers: the CCCL packages nest their headers under targets/x64/.
    for src in (library / "include").glob("*"):
        target = cuda_home / "include" / src.name
        if src.is_dir():
            _copy_tree(src, target)
        else:
            target.write_bytes(src.read_bytes())
    targets = library / "include" / "targets" / "x64"
    if targets.is_dir():
        for src in targets.glob("*"):
            target = cuda_home / "include" / src.name
            if src.is_dir():
                _copy_tree(src, target)
            else:
                target.write_bytes(src.read_bytes())

    # NVVM back-end: nvcc invokes cicc from nvvm/bin.
    for src in (library / "nvvm" / "bin").glob("*"):
        (cuda_home / "nvvm" / "bin" / src.name).write_bytes(src.read_bytes())
    for src in (library / "nvvm" / "libdevice").glob("*"):
        (cuda_home / "nvvm" / "libdevice" / src.name).write_bytes(src.read_bytes())

    # Import libraries.
    for src in (library / "lib").glob("*.lib"):
        (cuda_home / "lib" / "x64" / src.name).write_bytes(src.read_bytes())

    # gsplat's toolkit detection reads version.json.
    (cuda_home / "version.json").write_text(
        json.dumps({"cuda": {"version": CUDA_VERSION}}), encoding="utf-8"
    )


def _copy_tree(src: Path, dst: Path) -> None:
    """Recursively copy *src* into *dst*."""
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            _copy_tree(item, target)
        else:
            target.write_bytes(item.read_bytes())


def main() -> int:
    """Download the CUDA packages and assemble a local toolkit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path(__file__).resolve().parent.parent / ".cuda-toolkit",
        help="Directory to build the toolkit in (default: <repo>/.cuda-toolkit)",
    )
    args = parser.parse_args()

    staging = args.dest / "_staging"
    cuda_home = args.dest / "cuda"
    staging.mkdir(parents=True, exist_ok=True)

    for label, subdir, filename in DEFAULT_PACKAGES:
        url = f"https://conda.anaconda.org/{CHANNEL}/label/{label}/{subdir}/{filename}"
        sys.stdout.write(f"  {filename} ... ")
        sys.stdout.flush()
        try:
            data = _download(url)
        except OSError as exc:
            print(f"FAILED ({exc})")
            return 1
        _extract(data, staging)
        print(f"ok ({len(data) // 1024} KB)")

    _assemble_layout(staging, cuda_home)

    nvcc = cuda_home / "bin" / "nvcc.exe"
    cicc = cuda_home / "nvvm" / "bin" / "cicc.exe"
    if not nvcc.exists() or not cicc.exists():
        print(f"[error] toolkit incomplete: nvcc={nvcc.exists()} cicc={cicc.exists()}")
        return 1

    print(f"\nCUDA toolkit ready at {cuda_home}")
    print("Next: scripts\\build_gsplat_cuda.bat")
    return 0


if __name__ == "__main__":
    sys.exit(main())
