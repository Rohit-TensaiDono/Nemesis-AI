# ============================================================
#  NEMESIS — main.py
#  CLI entry point. Talk to Nemesis.
# ============================================================

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.brain       import NemesisBrain
from core.memory      import NemesisMemory
from core.personality import get_system_prompt
from core.router      import route, build_cot_prompt, format_routing_info
from core.language    import set_hindi_percent, get_language_label, detect_input_language
from config           import MASTER_NAME, NEMESIS_NAME


# ── Helpers ───────────────────────────────────────────────────

def get_time_of_day() -> str:
    h = datetime.now().hour
    if 5  <= h < 12: return "morning"
    if 12 <= h < 18: return "day"
    if 18 <= h < 22: return "evening"
    return "night"


def handle_command(text: str, memory: NemesisMemory) -> bool:
    """
    Handle special CLI commands. Returns True if handled.
    These won't be needed in the GUI — just for CLI phase.
    """
    cmd = text.strip().lower()

    if cmd in ("/exit", "/quit", "/bye"):
        memory.save()
        print(f"\nNemesis: Until next time, {MASTER_NAME}.")
        sys.exit(0)

    if cmd == "/clear":
        memory.clear_session()
        return True

    if cmd == "/memory":
        print(f"\n[Memory] {memory}")
        ctx = memory.build_context_string()
        print(ctx if ctx else "[Memory] Nothing stored yet.")
        return True

    if cmd == "/tasks":
        tasks = memory.get_pending_tasks()
        if tasks:
            for t in tasks:
                print(f"  - [{t['type']}] {t['description']}")
        else:
            print("[Tasks] None pending.")
        return True

    if cmd == "/people":
        people = memory.get_all_people()
        if people:
            for p in people.values():
                print(f"  - {p['name']}: {p['relationship']} ({p['access_level']})")
        else:
            print("[People] No one registered yet.")
        return True

    if cmd.startswith("/hindi "):
        try:
            pct = int(cmd.split("/hindi ")[1].strip())
            set_hindi_percent(pct)
            print(f"[Language] Now: {get_language_label()}")
        except ValueError:
            print("[Language] Usage: /hindi 0-100")
        return True

    if cmd.startswith("/remember "):
        fact = text[len("/remember "):].strip()
        memory.remember_fact(fact)
        print(f"[Memory] Noted: {fact}")
        return True

    if cmd.startswith("/meet "):
        # Usage: /meet Aryan friend
        parts = cmd[len("/meet "):].strip().split()
        if len(parts) >= 2:
            name = parts[0].capitalize()
            rel  = " ".join(parts[1:])
            memory.remember_person(name, rel)
            print(f"[Memory] {name} remembered as: {rel}")
        else:
            print("[Memory] Usage: /meet <name> <relationship>")
        return True

    if cmd.startswith("/track "):
        task = text[len("/track "):].strip()
        memory.add_task(task, task_type="watcher")
        print(f"[Tasks] Tracking: {task}")
        return True

    if cmd == "/debug":
        # Toggle debug mode
        global DEBUG_MODE
        DEBUG_MODE = not DEBUG_MODE
        print(f"[Debug] {'ON' if DEBUG_MODE else 'OFF'}")
        return True

    if cmd == "/help":
        print("""
  Commands:
    /hindi 0-100     set Hindi percentage (0=English, 100=Hindi)
    /remember <fact> store a fact about yourself
    /meet <name> <rel> introduce someone to Nemesis
    /track <task>    add a tracking task
    /memory          show memory state
    /tasks           show pending tasks
    /people          show known people
    /clear           clear session memory
    /debug           toggle routing debug info
    /help            this menu
    /exit            goodbye
        """)
        return True

    return False


# ── Main loop ─────────────────────────────────────────────────

DEBUG_MODE = False


def main():
    print(f"""
╔══════════════════════════════════════════╗
║           N E M E S I S                  ║
║        Your butler awaits, My Lord.      ║
║     Type /help for commands.             ║
╚══════════════════════════════════════════╝
    """)

    # Boot up
    memory = NemesisMemory()
    brain  = NemesisBrain()

    print(f"[Language] {get_language_label()}")
    print(f"[Memory]   {memory}")
    print()

    while True:
        try:
            user_input = input("Lord: ").strip()
        except (KeyboardInterrupt, EOFError):
            memory.save()
            print(f"\nNemesis: Until next time, {MASTER_NAME}.")
            break

        if not user_input:
            continue

        # Handle CLI commands
        if user_input.startswith("/"):
            handle_command(user_input, memory)
            continue

        # ── Route the request ──────────────────────────────
        decision  = route(user_input, local_load=0.3)

        if DEBUG_MODE:
            print(format_routing_info(decision))

        # Wrap with CoT if needed
        prompt_text = build_cot_prompt(user_input, decision["cot_depth"])

        # ── Build context ──────────────────────────────────
        time_of_day   = get_time_of_day()
        memory_context = memory.build_context_string()

        # Detect input language to inform response
        input_lang = detect_input_language(user_input)

        system_prompt = get_system_prompt(
            user_state="normal",      # Phase 3 will feed real mood here
            people_present=None,      # Phase 3 will feed cam data here
            time_of_day=time_of_day
        )

        # Inject memory context into system prompt if available
        if memory_context:
            system_prompt += f"\n\nCONTEXT FROM MEMORY:\n{memory_context}"

        # ── Think ──────────────────────────────────────────
        history  = memory.get_history()
        response = brain.think(
            system_prompt=system_prompt,
            history=history,
            user_message=prompt_text
        )

        # ── Store in memory ────────────────────────────────
        memory.add_turn("user",      user_input)   # store original, not CoT-wrapped
        memory.add_turn("assistant", response)

        # Auto-save every 5 turns
        if len(memory.conversation) % 10 == 0:
            memory.save()


if __name__ == "__main__":
    main()