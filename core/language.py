# ============================================================
#  NEMESIS — core/language.py
#  Hinglish mixer + language utilities
# ============================================================

from config import HINDI_PERCENT

# ── Hindi % slider ────────────────────────────────────────────

_current_hindi_percent = HINDI_PERCENT


def set_hindi_percent(value: int):
    """Set Hindi ratio. 0 = pure English, 100 = pure Hindi."""
    global _current_hindi_percent
    _current_hindi_percent = max(0, min(100, value))
    print(f"[Nemesis] Language mix set — Hindi: {_current_hindi_percent}% / English: {100 - _current_hindi_percent}%")


def get_hindi_percent() -> int:
    return _current_hindi_percent


def get_language_label() -> str:
    hp = _current_hindi_percent
    if hp == 0:    return "English only"
    if hp <= 20:   return "English-heavy Hinglish"
    if hp <= 40:   return "Natural Hinglish (default)"
    if hp <= 60:   return "Balanced Hinglish"
    if hp <= 80:   return "Hindi-heavy Hinglish"
    return "Hindi only"


# ── Common Nemesis phrases in Hinglish ───────────────────────
# These are reference phrases, not injected directly — they
# guide the model's style via the personality system prompt.

BUTLER_PHRASES = {
    "acknowledge":  ["Jaise aap chahein, Sir.",
                     "As you wish, Sir.",
                     "Bilkul, Sir.",
                     "Of course, Sir."],

    "task_done":    ["Kaam ho gaya, Sir.",
                     "It is done, Sir.",
                     "Ho gaya, Sir. Jaise expect kiya tha.",
                     "Completed, Sir. As anticipated."],

    "already_done": ["Main pehle se kar chuka tha, Sir.",
                     "Done, Sir. I anticipated this some time ago.",
                     "Sir, ye toh tab hi ho gaya tha."],

    "disagreement": ["Sir... ye advisable nahi lagta.",
                     "Sir, agar main suggest kar sakta hoon —",
                     "With respect, Sir, there may be a better approach."],

    "wit":          ["Kya main breathe karna bhi remind karun, Sir?",
                     "Shall I also remind you to breathe, Sir?",
                     "An interesting hour for such a question, Sir. Nevertheless.",
                     "...Dono ke liye behtar hoga agar main ye nahi dekha."],

    "confidence":   ["Aapne pehle bhi mushkil kaam kiye hain, Sir. Ye kuch nahi.",
                     "You have done harder things before breakfast, Sir. This is nothing.",
                     "Sir ke instincts is matter mein pehle bhi sahi nikal chuke hain."],

    "night":        ["Raat ko aisi baatein soochte hain aap, Sir. Phir bhi.",
                     "An interesting hour, Sir. Nevertheless, allow me."],

    "unknown_person": ["Sir.", "..."],  # Nemesis goes quiet and careful
}


def get_phrase(category: str) -> str:
    """Get a random phrase from a category."""
    import random
    phrases = BUTLER_PHRASES.get(category, ["..."])
    return random.choice(phrases)


# ── Language detection helper ─────────────────────────────────

def detect_input_language(text: str) -> str:
    """
    Lightweight heuristic to detect if user typed Hindi/Devanagari.
    Returns: 'hindi' | 'english' | 'hinglish'
    Phase 2 will replace this with Whisper.cpp language detection for speech.
    """
    devanagari_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    total = len(text.replace(" ", ""))
    if total == 0:
        return "english"
    ratio = devanagari_chars / total
    if ratio > 0.6:
        return "hindi"
    if ratio > 0.1:
        return "hinglish"
    return "english"