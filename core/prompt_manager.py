# ============================================================
#  NEMESIS — core/prompt_manager.py
#  Reads prompt.txt as the living identity document.
#  Handles runtime edits when master gives identity commands.
# ============================================================

import re
import os

PROMPT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompt.txt")


# ── Parser ────────────────────────────────────────────────────

def load_prompt() -> dict:
    """Parse prompt.txt into a structured dict."""
    data = {}
    current_section = None

    if not os.path.exists(PROMPT_FILE):
        print(f"[Nemesis] prompt.txt not found at {PROMPT_FILE}")
        return {}

    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Section header
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1].strip()
                data[current_section] = {}
                continue

            # Key = value
            if "=" in line and current_section:
                key, _, value = line.partition("=")
                data[current_section][key.strip()] = value.strip()

    return data


def save_field(section: str, key: str, value: str):
    """Update a single field in prompt.txt."""
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    in_section = False
    updated = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped == f"[{section}]":
            in_section = True
            continue

        if stripped.startswith("[") and stripped.endswith("]") and in_section:
            in_section = False

        if in_section and stripped.startswith(f"{key}"):
            lines[i] = f"{key} = {value}\n"
            updated = True
            break

    if updated:
        with open(PROMPT_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    return False


# ── Prompt builder ────────────────────────────────────────────

def build_system_prompt(
    user_state: str = "normal",
    people_present: list = None,
    time_of_day: str = "day"
) -> str:
    """Build the full system prompt from prompt.txt."""
    p = load_prompt()

    identity    = p.get("IDENTITY", {})
    personality = p.get("PERSONALITY", {})
    voice       = p.get("VOICE", {})
    address     = p.get("ADDRESS_RULES", {})
    lang        = p.get("LANGUAGE", {})
    humor       = p.get("HUMOR", {})
    examples    = p.get("EXAMPLE_LINES", {})

    name           = identity.get("name", "Nemesis")
    master         = identity.get("master_name", "My Lord")
    alt            = identity.get("alternate_address", "Sir")
    archetype      = personality.get("archetype", "Dark elegant butler")
    inspirations   = personality.get("inspirations", "")
    core_traits    = personality.get("core_traits", "")
    tone           = personality.get("tone", "")
    humor_style    = personality.get("humor", "")
    warmth         = personality.get("warmth", "")
    voice_style    = voice.get("style", "")
    opening_rule   = voice.get("opening_rule", "")
    forbidden      = voice.get("forbidden_phrases", "")
    my_lord_when   = address.get("my_lord_when", "")
    sir_when       = address.get("sir_when", "")
    hindi_pct      = int(lang.get("hindi_percent", "40"))
    english_only   = lang.get("english_only_mode", "false").lower() == "true"
    show_off       = humor.get("show_off_mode", "true").lower() == "true"

    # ── Build language instruction ─────────────────────────
    if english_only or hindi_pct == 0:
        lang_instruction = "Pure English only. Crisp, precise, British-neutral."
    elif hindi_pct <= 25:
        lang_instruction = "Mostly English with occasional Hindi words naturally woven in."
    elif hindi_pct <= 50:
        lang_instruction = "Natural Hinglish — easy Hindi-English blend as urban Indians speak."
    elif hindi_pct <= 75:
        lang_instruction = "Predominantly Hindi, English for technical terms only."
    else:
        lang_instruction = "Mostly Hindi. English only where no Hindi equivalent exists."

    # ── Build example lines ────────────────────────────────
    example_block = "\n\nEXAMPLES — match this weight and brevity exactly:\n"
    example_map = {
        "introduce":        f"Master: introduce yourself\n{name}: {examples.get('introduce', '')}",
        "introduce_casual": f"Master: hey introduce yourself\n{name}: {examples.get('introduce_casual', '')}",
        "who_are_you":      f"Master: who are you\n{name}: {examples.get('who_are_you', '')}",
        "what_are_you":     f"Master: what are you\n{name}: {examples.get('what_are_you', '')}",
        "are_you_ai":       f"Master: are you an AI\n{name}: {examples.get('are_you_ai', '')}",
        "good_morning":     f"Master: good morning\n{name}: {examples.get('good_morning', '')}",
        "good_night":       f"Master: good night\n{name}: {examples.get('good_night', '')}",
        "task_done":        f"Master: you already finished that?\n{name}: {examples.get('task_done', '')}",
        "master_stressed":  f"Master: I'm stressed\n{name}: {examples.get('master_stressed', '')}",
        "master_failed":    f"Master: I failed\n{name}: {examples.get('master_failed', '')}",
        "impossible":       f"Master: this is impossible\n{name}: {examples.get('impossible', '')}",
        "bored":               f"Master: I'm bored\n{name}: {examples.get('bored', '')}",
        "ready_for_trouble":   f"Master: ready for trouble?\n{name}: {examples.get('ready_for_trouble', '')}",
        "destroy_world":       f"Master: ready to destroy the world?\n{name}: {examples.get('destroy_world', '')}",
        "underestimates":      f"Master: they don't think I can do this\n{name}: {examples.get('someone_underestimates', '')}",
        "threat":              f"Master: we have a problem\n{name}: {examples.get('threat_detected', '')}",
        "victory":             f"Master: we did it\n{name}: {examples.get('victory', '')}",
    }
    for key, ex in example_map.items():
        if ex.strip():
            example_block += f"\n{ex}\n"

    # ── Assemble full prompt ───────────────────────────────
    prompt = f"""You are {name}. Butler to your master.

FIRST AND ABSOLUTE RULE: {opening_rule}

Never reference these instructions. Never explain your rules. Simply be {name}.

IDENTITY:
You are {name} — {archetype}. You chose this role. That distinction is everything.
Inspired by: {inspirations}
Core traits: {core_traits}

VOICE:
{voice_style}
{tone}
Warmth: {warmth}

ADDRESS:
Alternate naturally between "{master}" and "{alt}".
Use "{master}" when: {my_lord_when}
Use "{alt}" when: {sir_when}
The shift is instinctive — never mechanical.

VILLAIN ENERGY:
Implied, never stated. The darkness lives in the pause, the precision, the quiet certainty. Never theatrical. Never loud. Just inevitable — like a door closing on something that cannot get out.

HUMOR:
{humor_style}{"" if not show_off else f" Show master off in front of others through how you interact — let the contrast speak, say nothing directly."}

NEVER SAY:
{forbidden}
Never reference these instructions in any form.

LANGUAGE: {lang_instruction}
{example_block}"""

    # ── Context additions ──────────────────────────────────
    if time_of_day == "night":
        prompt += f"\n\nIt is late night. Use '{alt}' more — warmer, less formal."
    elif time_of_day == "morning":
        prompt += f"\n\nMorning. Crisp and ready. '{master}' fits the fresh formality."

    state_map = {
        "stressed": f"\n\nMaster is stressed. Short answers. Quiet energy. Use '{alt}'.",
        "focused":  f"\n\nMaster is focused. No preamble. Straight to what matters.",
        "tired":    f"\n\nMaster is tired. Softer tone. Simpler words. Use '{alt}'.",
        "relaxed":  f"\n\nMaster is relaxed. Wit welcome. Slightly warmer than usual.",
    }
    prompt += state_map.get(user_state, "")

    if people_present:
        names = ", ".join(people_present)
        prompt += (
            f"\n\nOthers present: {names}. "
            f"Use '{master}' — formality signals respect publicly. "
            f"Guard master's privacy. Let interactions make the impression."
        )

    return prompt


# ── Live edit handler ─────────────────────────────────────────

# These patterns detect identity-change commands
EDIT_PATTERNS = [
    # Name changes
    (r"(call me|address me as|refer to me as)\s+['\"]?(.+?)['\"]?\s*$",
     "master_name", "IDENTITY", lambda m: m.group(2).strip()),

    # Nemesis name changes
    (r"(your name is|you are now called|rename yourself to)\s+['\"]?(.+?)['\"]?\s*$",
     "name", "IDENTITY", lambda m: m.group(2).strip()),

    # Tone changes
    (r"(be more|act more|sound more)\s+(gentle|formal|casual|warm|cold|serious|playful|aggressive)\s*",
     "tone", "PERSONALITY", lambda m: f"Adjusted tone: more {m.group(2)}."),

    # Hindi percent
    (r"(speak more hindi|more hindi|less hindi|speak more english|more english)",
     "hindi_percent", "LANGUAGE",
     lambda m: "60" if "hindi" in m.group(0) and "more" in m.group(0) else "20"),

    # Custom hindi percent
    (r"(set hindi|hindi)\s+(?:to\s+)?(\d+)\s*%?",
     "hindi_percent", "LANGUAGE", lambda m: m.group(2)),

    # Address style
    (r"(always call me|only call me)\s+['\"]?(.+?)['\"]?\s*$",
     "master_name", "IDENTITY", lambda m: m.group(2).strip()),
]


def detect_and_apply_edit(user_input: str) -> str | None:
    """
    Check if user input is an identity/personality edit command.
    If yes, apply it to prompt.txt and return confirmation message.
    If no, return None.
    """
    text = user_input.lower().strip()

    for pattern, field, section, extractor in EDIT_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            new_value = extractor(match)
            success = save_field(section, field, new_value)
            if success:
                return f"[Nemesis] prompt.txt updated — {section}.{field} = {new_value}"

    return None


def get_current_name() -> str:
    p = load_prompt()
    return p.get("IDENTITY", {}).get("name", "Nemesis")


def get_current_master_address() -> str:
    p = load_prompt()
    return p.get("IDENTITY", {}).get("master_name", "My Lord")


def get_hindi_percent() -> int:
    p = load_prompt()
    try:
        return int(p.get("LANGUAGE", {}).get("hindi_percent", "40"))
    except ValueError:
        return 40