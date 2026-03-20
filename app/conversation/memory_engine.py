from collections import deque

class MemoryEngine:
    _storage = {}  # In-memory storage
    MAX_HISTORY = 10

    @classmethod
    def clear(cls, user_id):
        cls._storage[user_id] = deque(maxlen=cls.MAX_HISTORY)

    @classmethod
    def add_user_message(cls, user_id, text):
        if user_id not in cls._storage:
            cls._storage[user_id] = deque(maxlen=cls.MAX_HISTORY)
        cls._storage[user_id].append({"role": "user", "content": str(text).strip()})

    @classmethod
    def add_bot_message(cls, user_id, text):
        if user_id not in cls._storage:
            cls._storage[user_id] = deque(maxlen=cls.MAX_HISTORY)
        cls._storage[user_id].append({"role": "assistant", "content": str(text).strip()})

    @classmethod
    def get_context(cls, user_id):
        """Get recent conversation history."""
        if user_id not in cls._storage:
            return []
        return list(cls._storage[user_id])