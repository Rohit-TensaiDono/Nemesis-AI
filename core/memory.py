# ============================================================
#  NEMESIS — core/memory.py
#  Conversation memory + persistence
#  Phase 1: in-memory + JSON file
#  Phase 4 will upgrade to FAISS + Qdrant
# ============================================================

import json
import os
from datetime import datetime
from config import MAX_HISTORY, MEMORY_FILE


class NemesisMemory:
    def __init__(self):
        self.conversation: list[dict] = []   # current session
        self.session_start = datetime.now().isoformat()
        self._load_persistent()

    # ── Conversation history ──────────────────────────────────

    def add_turn(self, role: str, content: str):
        """Add a turn. role: 'user' | 'assistant'"""
        self.conversation.append({
            "role":    role,
            "content": content,
            "time":    datetime.now().isoformat()
        })
        # Trim to MAX_HISTORY turns
        if len(self.conversation) > MAX_HISTORY * 2:
            self.conversation = self.conversation[-(MAX_HISTORY * 2):]

    def get_history(self) -> list[dict]:
        """Returns history formatted for llama.cpp context."""
        return [{"role": t["role"], "content": t["content"]}
                for t in self.conversation]

    def clear_session(self):
        self.conversation = []
        print("[Nemesis] Session memory cleared.")

    # ── Persistent memory ─────────────────────────────────────
    # Stores notable facts, preferences, people, tasks
    # Later phases will embed these into a vector store

    def _load_persistent(self):
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.facts      = data.get("facts", [])
                self.people     = data.get("people", {})
                self.tasks      = data.get("tasks", [])
                self.preferences = data.get("preferences", {})
        else:
            self.facts       = []
            self.people      = {}
            self.tasks       = []
            self.preferences = {}

    def save(self):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "facts":       self.facts,
                "people":      self.people,
                "tasks":       self.tasks,
                "preferences": self.preferences,
                "last_saved":  datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

    # ── People / relationship graph ───────────────────────────

    def remember_person(self, name: str, relationship: str,
                        access_level: str = "limited", notes: str = ""):
        self.people[name.lower()] = {
            "name":         name,
            "relationship": relationship,
            "access_level": access_level,
            "notes":        notes,
            "first_seen":   datetime.now().isoformat()
        }
        self.save()
        print(f"[Nemesis] Remembered: {name} — {relationship}.")

    def get_person(self, name: str) -> dict | None:
        return self.people.get(name.lower())

    def get_all_people(self) -> dict:
        return self.people

    # ── Facts ─────────────────────────────────────────────────

    def remember_fact(self, fact: str, category: str = "general"):
        self.facts.append({
            "fact":     fact,
            "category": category,
            "time":     datetime.now().isoformat()
        })
        self.save()

    def get_facts_summary(self) -> str:
        if not self.facts:
            return ""
        lines = [f"- {f['fact']}" for f in self.facts[-20:]]
        return "Known facts about the master:\n" + "\n".join(lines)

    # ── Preferences ───────────────────────────────────────────

    def set_preference(self, key: str, value):
        self.preferences[key] = value
        self.save()

    def get_preference(self, key: str, default=None):
        return self.preferences.get(key, default)

    # ── Tasks / watchers ──────────────────────────────────────
    # Phase 4 will actually execute these via server agents.
    # For now, we store them so Nemesis can reference them.

    def add_task(self, description: str, task_type: str = "reminder"):
        self.tasks.append({
            "description": description,
            "type":        task_type,
            "status":      "pending",
            "created":     datetime.now().isoformat()
        })
        self.save()

    def get_pending_tasks(self) -> list:
        return [t for t in self.tasks if t["status"] == "pending"]

    # ── Context builder ───────────────────────────────────────
    # Builds the memory context string injected into prompts

    def build_context_string(self) -> str:
        parts = []
        if self.facts:
            parts.append(self.get_facts_summary())
        if self.people:
            people_list = [
                f"  - {p['name']}: {p['relationship']} (access: {p['access_level']})"
                for p in self.people.values()
            ]
            parts.append("Known people:\n" + "\n".join(people_list))
        pending = self.get_pending_tasks()
        if pending:
            task_list = [f"  - {t['description']}" for t in pending[:5]]
            parts.append("Pending tasks:\n" + "\n".join(task_list))
        return "\n\n".join(parts) if parts else ""

    def __repr__(self):
        return (f"<NemesisMemory turns={len(self.conversation)} "
                f"facts={len(self.facts)} people={len(self.people)} "
                f"tasks={len(self.tasks)}>")