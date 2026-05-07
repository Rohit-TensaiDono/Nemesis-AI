# ============================================================
#  NEMESIS — Dockerfile
#  CUDA 12.6 + Python 3.12 + llama-cpp-python
#  Model is mounted as a volume — not baked in
# ============================================================

FROM nvidia/cuda:12.6.0-cudnn-devel-ubuntu22.04

# ── System dependencies ──────────────────────────────────────
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-dev \
    python3-pip \
    python3.12-venv \
    git \
    curl \
    build-essential \
    cmake \
    ninja-build \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Make python3.12 the default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1 \
    && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# ── Working directory ────────────────────────────────────────
WORKDIR /nemesis

# ── Install llama-cpp-python with CUDA support ───────────────
# Build from source inside container — CUDA headers available here
ENV CMAKE_ARGS="-DGGML_CUDA=on"
ENV FORCE_CMAKE=1

RUN pip install --upgrade pip setuptools wheel
RUN pip install llama-cpp-python==0.3.22 --no-cache-dir

# ── Install other dependencies ───────────────────────────────
RUN pip install colorama==0.4.6

# ── Copy project files ───────────────────────────────────────
COPY config.py .
COPY main.py .
COPY requirements.txt .
COPY core/ ./core/

# ── Model volume mount point ─────────────────────────────────
# Mount your model folder here at runtime:
# docker run -v E:\Projects\Nemesis\core\model:/nemesis/core/model nemesis
RUN mkdir -p core/model

# ── Environment ──────────────────────────────────────────────
ENV NEMESIS_MODEL_PATH=/nemesis/core/model/dolphin-2.9.2-qwen2-7b-Q3_K_M.gguf
ENV PYTHONUNBUFFERED=1

# ── Entry point ──────────────────────────────────────────────
CMD ["python", "main.py"]