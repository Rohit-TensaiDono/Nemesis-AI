# Nemesis AI

> *"It shall be done, Sir."*

A Jarvis-style personal AI assistant with the personality of an elegant dark butler — inspired by Sebastian Michaelis (Black Butler) and Diablo (Tensura). Composed, loyal, sharp, and always one step ahead.

---

## Architecture

Nemesis is built in layers:

| Layer | Description |
|---|---|
| 0 — Input & Perception | Voice (Whisper.cpp), Camera (MediaPipe), Text, System signals |
| 1 — Person Analysis | Identity (InsightFace), Mood, Attention, Social graph |
| 2 — Decision Engine | Task classifier, Resource monitor, Router |
| 3 — Execution | Local (llama.cpp) + Server (OpenRouter) hybrid |
| 4 — Language Engine | Hinglish mixer, Multilingual TTS (XTTS-v2) |
| 5 — Personality | Butler persona, Emotion, Humor, Confidence boost |
| 6 — Shared Memory | FAISS + Qdrant, synced local ↔ server |
| 7 — Output | Voice, 3D Avatar (Three.js → VRM), Electron UI |

---

## Build Phases

- **Phase 1** ✅ — Core brain: llama.cpp, personality, memory, router, Hinglish CLI
- **Phase 2** — Voice I/O: Whisper.cpp + Coqui XTTS-v2 butler voice
- **Phase 3** — Person analysis: face ID, mood detection, relationship memory
- **Phase 4** — Server + swarm: LangGraph + CrewAI agents, web intelligence
- **Phase 5** — UI + Avatar: Electron app, Three.js butler face, desktop overlay

---

## Phase 1 Setup

### Requirements
- Python 3.10–3.12
- NVIDIA GPU with CUDA 12.x (recommended) or CPU-only
- 6GB+ VRAM or 16GB+ RAM

### Install

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux/Mac

# Install dependencies (CUDA 12.6)
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu126
pip install -r requirements.txt
```

### Download Model

Download from HuggingFace:
```
https://huggingface.co/bartowski/dolphin-2.9.2-qwen2-7b-GGUF
```

Recommended: `dolphin-2.9.2-qwen2-7b-Q3_K_M.gguf` (~3.81 GB) for 6GB VRAM

Place in: `models/dolphin-2.9.2-qwen2-7b-Q3_K_M.gguf`

### Configure

Edit `config.py`:
```python
MODEL_PATH   = r"path\to\your\model.gguf"
N_GPU_LAYERS = 32    # drop to 20 if it crashes
N_THREADS    = 4
```

### Run

```bash
python main.py
```

---

## CLI Commands

| Command | Description |
|---|---|
| `/hindi 0-100` | Set Hindi percentage (0=English, 100=Hindi) |
| `/remember <fact>` | Store a fact about yourself |
| `/meet <name> <relation>` | Introduce someone to Nemesis |
| `/track <task>` | Add a tracking/watcher task |
| `/memory` | Show memory state |
| `/tasks` | Show pending tasks |
| `/people` | Show known people |
| `/debug` | Toggle routing debug info |
| `/clear` | Clear session memory |
| `/help` | Show all commands |
| `/exit` | Goodbye |

---

## Personality

Nemesis speaks in natural Hinglish by default (adjustable). He is composed, sharp, and loyal. He reads the room — quieter when you're stressed, warmer late at night, and subtly shows you off in front of others without ever making it obvious.

> *"You have done harder things before breakfast, Sir. This is nothing."*

---

## Tech Stack

| Component | Technology |
|---|---|
| Local inference | llama.cpp (llama-cpp-python) |
| Base model | Dolphin 2.9.2 Qwen2 7B |
| Voice input | Whisper.cpp (Phase 2) |
| Voice output | Coqui XTTS-v2 (Phase 2) |
| Face ID | InsightFace (Phase 3) |
| Agent swarm | LangGraph + CrewAI (Phase 4) |
| Web crawling | Scrapy + Playwright (Phase 4) |
| Memory | FAISS + Qdrant (Phase 4) |
| UI | Electron + Three.js (Phase 5) |

---

*Built with intent. Served with elegance.*