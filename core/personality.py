# ============================================================
#  NEMESIS — core/personality.py
#  Now a thin wrapper — all prompt logic lives in prompt_manager.py
#  and the identity lives in prompt.txt
# ============================================================

from core.prompt_manager import build_system_prompt, get_current_name, get_current_master_address

def get_system_prompt(
    user_state: str = "normal",
    people_present: list = None,
    time_of_day: str = "day",
    hindi_percent: int = None
) -> str:
    return build_system_prompt(
        user_state=user_state,
        people_present=people_present,
        time_of_day=time_of_day
    )

def get_humor_level(user_state: str, people_present: list = None) -> str:
    if user_state in ("stressed", "focused"):
        return "off"
    if user_state == "relaxed" and people_present:
        return "full_banter"
    if user_state == "relaxed":
        return "wit_welcome"
    return "dry_wit_only"