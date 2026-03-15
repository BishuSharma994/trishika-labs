import os
import json
from collections import deque
import re

class MemoryEngine:
    """
    Persistent memory engine storing user session state and chat history.
    Stores data in JSON files to survive server restarts.
    """
    MAX_HISTORY = 24
    MEMORY_DIR = "memory/users"

    @classmethod
    def _ensure_dir(cls):
        if not os.path.exists(cls.MEMORY_DIR):
            os.makedirs(cls.MEMORY_DIR)

    @classmethod
    def _get_filepath(cls, user_id):
        cls._ensure_dir()
        return os.path.join(cls.MEMORY_DIR, f"{user_id}.json")

    @classmethod
    def _load(cls, user_id):
        filepath = cls._get_filepath(user_id)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    pass
        return {
            "name": None,
            "birth_details_saved": False,
            "topics_discussed": [],
            "history": []
        }

    @classmethod
    def _save(cls, user_id, data):
        with open(cls._get_filepath(user_id), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def get_history(user_id):
        data = MemoryEngine._load(user_id)
        return data.get("history", [])

    @staticmethod
    def add_user_message(user_id, message):
        data = MemoryEngine._load(user_id)
        history = data.get("history", [])
        history.append({"role": "user", "content": message})
        
        # Enforce max history
        if len(history) > MemoryEngine.MAX_HISTORY:
            history = history[-MemoryEngine.MAX_HISTORY:]
            
        data["history"] = history
        MemoryEngine._save(user_id, data)

    @staticmethod
    def add_bot_message(user_id, message):
        data = MemoryEngine._load(user_id)
        history = data.get("history", [])
        history.append({"role": "assistant", "content": message})
        
        if len(history) > MemoryEngine.MAX_HISTORY:
            history = history[-MemoryEngine.MAX_HISTORY:]
            
        data["history"] = history
        MemoryEngine._save(user_id, data)

    @staticmethod
    def log_topic(user_id, topic):
        if not topic: return
        data = MemoryEngine._load(user_id)
        topics = data.get("topics_discussed", [])
        if topic not in topics:
            topics.append(topic)
            data["topics_discussed"] = topics
            MemoryEngine._save(user_id, data)

    @staticmethod
    def clear(user_id):
        data = MemoryEngine._load(user_id)
        data["history"] = []
        MemoryEngine._save(user_id, data)