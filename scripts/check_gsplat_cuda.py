"""Verify (and if needed build) the gsplat CUDA rasteriser extension.

gsplat ships no prebuilt Windows binaries, so its CUDA kernels are compiled on
first use. That JIT build needs a CUDA toolkit (``nvcc``), MSVC (``cl.exe``) and
``ninja`` on PATH, plus a writable build cache. Run this module through
``scripts/build_gsplat_cuda.bat``, which sets all of that up.
"""

from __future__ import annotations

import sys
import time


def main() -> int:
    """Import the gsplat CUDA backend, building it if necessary.

    Returns:
        Process exit code: 0 on success, 1 when the extension is unavailable.
    """
    start = time.time()
    try:
        from gsplat.cuda import _backend
    except Exception as exc:
        print(f"[error] gsplat CUDA extension failed to build: {exc}")
        return 1

    if _backend._C is None:
        print("[error] gsplat CUDA extension unavailable (toolkit not detected)")
        return 1

    elapsed = time.time() - start
    print(f"[ok] gsplat CUDA extension ready in {elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
