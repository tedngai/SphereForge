# SphereForge — Reproducible Docker environment
# CUDA 12.8 + PyTorch 2.6 + COLMAP + Python 3.11
#
# Build:
#   docker build -t sphereforge:latest .
#
# Run (with GPU):
#   docker run --gpus all -it -v $(pwd)/data:/data sphereforge:latest
#
# Run CLI:
#   docker run --gpus all -v $(pwd)/data:/data sphereforge:latest \
#       sphereforge process /data/raw/video.mp4 --output /data/export

FROM nvidia/cuda:12.8.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# ---------------------------------------------------------------------------
# System dependencies
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    wget \
    ffmpeg \
    libopencv-dev \
    libboost-all-dev \
    libeigen3-dev \
    libflann-dev \
    libglew-dev \
    libgl1-mesa-dev \
    libqt5widgets5 \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# COLMAP (build from source for CUDA support)
# ---------------------------------------------------------------------------
RUN git clone --branch 3.10 --depth 1 https://github.com/colmap/colmap.git /tmp/colmap \
    && mkdir -p /tmp/colmap/build && cd /tmp/colmap/build \
    && cmake .. -GNinja -DCMAKE_CUDA_ARCHITECTURES="all" \
    && ninja -j$(nproc) \
    && ninja install \
    && rm -rf /tmp/colmap

# ---------------------------------------------------------------------------
# Python environment
# ---------------------------------------------------------------------------
RUN python3.11 -m pip install --upgrade pip setuptools wheel

# PyTorch with CUDA 12.8
RUN python3.11 -m pip install \
    torch==2.6.0 torchvision --index-url https://download.pytorch.org/whl/cu128

# ---------------------------------------------------------------------------
# SphereForge installation
# ---------------------------------------------------------------------------
WORKDIR /opt/sphereforge
COPY . .

# Install SphereForge with all extras
RUN python3.11 -m pip install -e ".[all,dev]"

# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------
ENTRYPOINT ["sphereforge"]
CMD ["--help"]
