# ============================================================
#  NEMESIS — config.py
#  All settings in one place. Edit this to tune Nemesis.
# ============================================================

import os

# ── Model ────────────────────────────────────────────────────
MODEL_PATH = os.getenv(
    "NEMESIS_MODEL_PATH",
    r"E:\Projects\Nemesis\core\model\dolphin-2.9.2-qwen2-7b-Q3_K_M.gguf"
)
N_CTX        = 8192     # context window (model supports 131072, 8192 is practical sweet spot)
N_THREADS    = 4        # less CPU pressure since GPU handles inference
N_GPU_LAYERS = 32       # full model on GPU — drop to 20 if it crashes
TEMPERATURE  = 0.85  # slightly higher — more creative phrasing
TOP_P        = 0.92
TOP_K        = 40
MAX_TOKENS   = 120   # short and sharp — butler does not ramble
REPEAT_PENALTY = 1.1

# ── Language ─────────────────────────────────────────────────
# Hindi percentage in text output (0 = pure English, 100 = pure Hindi)
HINDI_PERCENT = 0       # forced English until Dolphin model — Qwen breaks Hinglish

# ── Memory ───────────────────────────────────────────────────
MAX_HISTORY  = 20       # conversation turns to keep in context
MEMORY_FILE  = "nemesis_memory.json"

# ── Personality ──────────────────────────────────────────────
MASTER_NAME  = "Lord"  # primary address — alternates with "Sir" based on context
NEMESIS_NAME = "Nemesis"

# ── Router thresholds ────────────────────────────────────────
COMPLEXITY_SIMPLE   = 3   # 1-3  → direct response, no CoT
COMPLEXITY_MEDIUM   = 6   # 4-6  → chain of thought
COMPLEXITY_COMPLEX  = 8   # 7-8  → deep reasoning
                          # 9-10 → agent swarm (Phase 4)