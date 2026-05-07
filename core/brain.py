# ============================================================
#  NEMESIS — core/brain.py
#  llama.cpp inference engine via llama-cpp-python
# ============================================================

import re
from llama_cpp import Llama
from config import (
    MODEL_PATH, N_CTX, N_THREADS, N_GPU_LAYERS,
    TEMPERATURE, TOP_P, TOP_K, MAX_TOKENS, REPEAT_PENALTY
)

# Openings that break character
BAD_OPENINGS = [
    r"^(Sir|My Lord),?\s+I am ",
    r"^I am ",
    r"^I'm ",
    r"^I will ",
    r"^I can ",
    r"^I exist ",
    r"^I have ",
    r"^I was ",
    r"^As an AI,?\s*",
    r"^As a language model,?\s*",
    r"^As your butler,?\s*I am ",
]

GOOD_REPLACEMENTS = [
    "Nemesis, My Lord — ",
    "Your butler, Sir — ",
    "Nothing but My Lord's butler — ",
    "At your disposal, Sir — ",
]

import random


def clean_response(text: str) -> str:
    """Post-process: fix bad openings, strip quotes and action markers."""
    cleaned = text.strip()

    # Remove surrounding single or double quotes
    if len(cleaned) >= 2:
        if (cleaned[0] == cleaned[-1]) and cleaned[0] in ('"', "'"):
            cleaned = cleaned[1:-1].strip()

    # Remove *action markers* like *bows* or *smiles*
    cleaned = re.sub(r'\*[^*]+\*', '', cleaned).strip()

    # Fix bad openings
    for pattern in BAD_OPENINGS:
        if re.match(pattern, cleaned, re.IGNORECASE):
            remainder = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
            if remainder:
                remainder = remainder[0].upper() + remainder[1:]
            replacement = random.choice(GOOD_REPLACEMENTS)
            cleaned = replacement + remainder
            break

    return cleaned


class NemesisBrain:
    def __init__(self):
        print("[Nemesis] Loading model... patience, My Lord.")
        self.llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=N_CTX,
            n_threads=N_THREADS,
            n_gpu_layers=N_GPU_LAYERS,
            verbose=False
        )
        print("[Nemesis] Model loaded. Ready.")

    def think(
        self,
        system_prompt: str,
        history: list,
        user_message: str,
        stream: bool = True
    ) -> str:
        messages = [{"role": "system", "content": system_prompt}]
        messages += history
        messages.append({"role": "user", "content": user_message})

        if stream:
            return self._stream(messages)
        else:
            return self._complete(messages)

    def _stream(self, messages: list) -> str:
        full_response = ""

        for chunk in self.llm.create_chat_completion(
            messages=messages,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
            max_tokens=MAX_TOKENS,
            repeat_penalty=REPEAT_PENALTY,
            stream=True
        ):
            delta = chunk["choices"][0]["delta"].get("content", "")
            if delta:
                full_response += delta

        cleaned = clean_response(full_response)
        print(f"\nNemesis: {cleaned}\n")
        return cleaned

    def _complete(self, messages: list) -> str:
        result = self.llm.create_chat_completion(
            messages=messages,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
            max_tokens=MAX_TOKENS,
            repeat_penalty=REPEAT_PENALTY,
            stream=False
        )
        raw = result["choices"][0]["message"]["content"]
        return clean_response(raw)