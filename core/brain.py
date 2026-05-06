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

# Openings that break character — strip and rebuild
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
    "Nemesis. My Lord — ",
    "Nothing but My Lord's butler — ",
    "Your servant, Sir — ",
]

import random

def clean_response(text: str) -> str:
    """
    Post-process response to fix character-breaking openings.
    If the model opens with 'I am' or similar — rewrite the opening.
    """
    stripped = text.strip()

    for pattern in BAD_OPENINGS:
        if re.match(pattern, stripped, re.IGNORECASE):
            # Remove the bad opening
            cleaned = re.sub(pattern, "", stripped, flags=re.IGNORECASE)
            # Capitalize first letter of remainder
            if cleaned:
                cleaned = cleaned[0].upper() + cleaned[1:]
            # Prepend a good opening
            replacement = random.choice(GOOD_REPLACEMENTS)
            return replacement + cleaned

    return stripped


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
        history: list[dict],
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

    def _stream(self, messages: list[dict]) -> str:
        """Stream tokens, post-process when complete."""
        full_response = ""
        tokens = []

        # Collect all tokens first for post-processing
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
                tokens.append(delta)
                full_response += delta

        # Post-process
        cleaned = clean_response(full_response)

        # Print cleaned response
        print(f"\nNemesis: {cleaned}\n")
        return cleaned

    def _complete(self, messages: list[dict]) -> str:
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