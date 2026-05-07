# ============================================================
#  NEMESIS — main.py
#  CLI entry point. Talk to Nemesis.
# ============================================================

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.brain          import NemesisBrain
from core.memory         import NemesisMemory
from core.prompt_manager import (
    build_system_prompt, detect_and_apply_edit,
    get_current_name, get_current_master_address, get_hindi_percent
)
from core.router         import route, build_cot_prompt, format_routing_info
from core.language       import detect_input_language


DEBUG_MODE = False


def get_time_of_day() -> str:
    h = datetime.now().hour
    if 5  <= h < 12: return "morning"
    if 12 <= h < 18: return "day"
    if 18 <= h < 22: return "evening"
    return "night"


def handle_command(text: str, memory: NemesisMemory) -> bool:
    cmd = text.strip().lower()

    if cmd in ("/exit", "/quit", "/bye"):
        memory.save()
        name = get_current_master_address()
        print(f"\nNemesis: Until next time, {name}.")
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
            from core.prompt_manager import save_field
            pct = int(cmd.split("/hindi ")[1].strip())
            save_field("LANGUAGE", "hindi_percent", str(pct))
            print(f"[Language] Hindi set to {pct}%")
        except ValueError:
            print("[Language] Usage: /hindi 0-100")
        return True

    if cmd.startswith("/remember "):
        fact = text[len("/remember "):].strip()
        memory.remember_fact(fact)
        print(f"[Memory] Noted: {fact}")
        return True

    if cmd.startswith("/meet "):
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
        global DEBUG_MODE
        DEBUG_MODE = not DEBUG_MODE
        print(f"[Debug] {'ON' if DEBUG_MODE else 'OFF'}")
        return True

    if cmd == "/prompt":
        # Show current prompt.txt
        prompt_path = os.path.join(os.path.dirname(__file__), "prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            print(f.read())
        return True

    if cmd == "/help":
        print("""
  Commands:
    /hindi 0-100       set Hindi percentage
    /remember <fact>   store a fact about yourself
    /meet <name> <rel> introduce someone
    /track <task>      add a watcher task
    /memory            show memory state
    /tasks             show pending tasks
    /people            show known people
    /prompt            show current prompt.txt
    /clear             clear session memory
    /debug             toggle routing debug info
    /help              this menu
    /exit              goodbye

  Identity commands (say naturally, no slash needed):
    "call me [name]"
    "your name is [name]"
    "be more gentle / formal / casual"
    "set hindi to 60%"
    "speak more hindi / more english"
        """)
        return True

    return False


def main():
    nemesis_name = get_current_name()
    master_addr  = get_current_master_address()

    print(f"""
╔══════════════════════════════════════════╗
║           N E M E S I S                  ║
║     Your butler awaits, {master_addr:<16}║
╚══════════════════════════════════════════╝
    """)

    memory = NemesisMemory()
    brain  = NemesisBrain()

    print(f"[Language] Hindi {get_hindi_percent()}% / English {100 - get_hindi_percent()}%")
    print(f"[Memory]   {memory}")
    print()

    while True:
        try:
            user_input = input("Lord: ").strip()
        except (KeyboardInterrupt, EOFError):
            memory.save()
            print(f"\n{nemesis_name}: Until next time, {master_addr}.")
            break

        if not user_input:
            continue

        # CLI commands
        if user_input.startswith("/"):
            handle_command(user_input, memory)
            continue

        # ── Check for identity edit commands ──────────────
        edit_result = detect_and_apply_edit(user_input)
        if edit_result:
            print(edit_result)
            # Reload name/address after edit
            nemesis_name = get_current_name()
            master_addr  = get_current_master_address()
            # Still let Nemesis respond naturally to the command
            # (don't continue — fall through to response)

        # ── Route ─────────────────────────────────────────
        decision    = route(user_input, local_load=0.3)
        prompt_text = build_cot_prompt(user_input, decision["cot_depth"])

        if DEBUG_MODE:
            print(format_routing_info(decision))

        # ── Build context ──────────────────────────────────
        time_of_day    = get_time_of_day()
        memory_context = memory.build_context_string()
        system_prompt  = build_system_prompt(
            user_state="normal",
            people_present=None,
            time_of_day=time_of_day
        )

        if memory_context:
            system_prompt += f"\n\nCONTEXT FROM MEMORY:\n{memory_context}"

        # ── Think ──────────────────────────────────────────
        history  = memory.get_history()
        response = brain.think(
            system_prompt=system_prompt,
            history=history,
            user_message=prompt_text
        )

        # ── Store ──────────────────────────────────────────
        memory.add_turn("user",      user_input)
        memory.add_turn("assistant", response)

        if len(memory.conversation) % 10 == 0:
            memory.save()


if __name__ == "__main__":
    main()