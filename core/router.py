# ============================================================
#  NEMESIS — core/router.py
#  Decision engine: scores complexity, chooses execution path
#  Phase 1: local only, CoT skeleton
#  Phase 4 will add server routing and agent swarm
# ============================================================

import re
from config import (
    COMPLEXITY_SIMPLE, COMPLEXITY_MEDIUM, COMPLEXITY_COMPLEX
)


# ── Complexity signals ────────────────────────────────────────

COMPLEX_KEYWORDS = [
    "compare", "analyse", "analyze", "research", "explain in detail",
    "design", "architecture", "implement", "build", "create a plan",
    "step by step", "in depth", "comprehensive", "multiple", "list all",
    "pros and cons", "difference between", "how does", "why does",
    "calculate", "solve", "debug", "optimize", "review my"
]

SIMPLE_KEYWORDS = [
    "what is", "kya hai", "tell me", "bata", "define", "who is",
    "when", "where", "yes", "no", "ok", "thanks", "shukriya",
    "hello", "hi", "haan", "nahi", "acha", "theek"
]

TASK_KEYWORDS = [
    "remind", "track", "watch", "monitor", "search for", "find",
    "download", "open", "run", "execute", "schedule", "set alarm"
]


def score_complexity(user_input: str) -> int:
    """
    Returns complexity score 1-10.
    1-3: simple, direct response
    4-6: needs some reasoning (CoT light)
    7-8: deep reasoning needed
    9-10: agent swarm territory (Phase 4)
    """
    text = user_input.lower()
    score = 3  # default: simple

    # Length is a signal
    word_count = len(text.split())
    if word_count > 50:  score += 2
    elif word_count > 25: score += 1

    # Complex keyword hits
    complex_hits = sum(1 for kw in COMPLEX_KEYWORDS if kw in text)
    score += min(complex_hits * 2, 4)

    # Simple keywords pull score down
    simple_hits = sum(1 for kw in SIMPLE_KEYWORDS if kw in text)
    score -= min(simple_hits * 2, 3)

    # Question marks (multiple = more complex)
    q_marks = text.count("?")
    if q_marks > 2: score += 1

    # Code/technical signals
    if any(s in text for s in ["code", "function", "class", "script",
                                "algorithm", "circuit", "equation"]):
        score += 1

    # Task/action signals → medium complexity
    if any(kw in text for kw in TASK_KEYWORDS):
        score = max(score, 5)

    return max(1, min(10, score))


def classify_intent(user_input: str) -> str:
    """
    Returns intent type for routing.
    conversation | question | task | technical | creative | system
    """
    text = user_input.lower()

    if any(kw in text for kw in TASK_KEYWORDS):
        return "task"

    if any(kw in text for kw in ["code", "script", "function", "debug",
                                   "circuit", "design", "implement"]):
        return "technical"

    if any(kw in text for kw in ["write", "story", "poem", "create",
                                   "generate", "draft", "compose"]):
        return "creative"

    if any(kw in text for kw in ["open", "close", "run", "system",
                                   "install", "file", "folder"]):
        return "system"

    if "?" in text or any(kw in text for kw in ["what", "how", "why",
                                                  "when", "where", "kya",
                                                  "kaise", "kyun"]):
        return "question"

    return "conversation"


def route(user_input: str, local_load: float = 0.3) -> dict:
    """
    Main routing decision.
    Returns dict with: mode, complexity, intent, cot_depth, use_server
    
    local_load: 0.0-1.0 (current CPU/GPU usage estimate)
    Phase 4 will read this from actual system metrics.
    """
    complexity = score_complexity(user_input)
    intent     = classify_intent(user_input)

    # Default: local only
    decision = {
        "complexity": complexity,
        "intent":     intent,
        "mode":       "direct",
        "cot_depth":  0,
        "use_server": False,
        "agents":     []
    }

    if complexity <= COMPLEXITY_SIMPLE:
        decision["mode"]      = "direct"
        decision["cot_depth"] = 0

    elif complexity <= COMPLEXITY_MEDIUM:
        decision["mode"]      = "cot"
        decision["cot_depth"] = 3

        # If local is loaded, note it — Phase 4 will actually offload
        if local_load > 0.7:
            decision["use_server"] = True

    elif complexity <= COMPLEXITY_COMPLEX:
        decision["mode"]      = "deep_cot"
        decision["cot_depth"] = 6
        decision["use_server"] = local_load > 0.5

    else:
        # 9-10: swarm territory
        decision["mode"]       = "swarm"
        decision["cot_depth"]  = 8
        decision["use_server"] = True
        decision["agents"]     = ["research", "reasoning", "synthesis"]

    return decision


def build_cot_prompt(user_input: str, depth: int) -> str:
    """
    Wraps user input with chain-of-thought instruction.
    Depth controls how thorough the reasoning should be.
    """
    if depth == 0:
        return user_input

    if depth <= 3:
        return (
            f"{user_input}\n\n"
            f"[Think step by step before responding. "
            f"Keep reasoning brief and internal.]"
        )
    elif depth <= 6:
        return (
            f"{user_input}\n\n"
            f"[Reason through this carefully before responding: "
            f"consider the problem from multiple angles, "
            f"identify the best approach, then give your answer.]"
        )
    else:
        return (
            f"{user_input}\n\n"
            f"[This requires deep reasoning. "
            f"Think through: (1) what exactly is being asked, "
            f"(2) what knowledge is relevant, "
            f"(3) what approaches exist, "
            f"(4) which is optimal and why. "
            f"Then respond with full precision.]"
        )


def format_routing_info(decision: dict) -> str:
    """Debug display of routing decision."""
    mode_labels = {
        "direct":   "direct →",
        "cot":      "CoT (depth {cot_depth}) →",
        "deep_cot": "Deep CoT (depth {cot_depth}) →",
        "swarm":    "Agent swarm →"
    }
    label = mode_labels.get(decision["mode"], decision["mode"])
    label = label.format(**decision)
    server = " [+server]" if decision["use_server"] else " [local]"
    return f"[{label} complexity:{decision['complexity']}/10 intent:{decision['intent']}{server}]"