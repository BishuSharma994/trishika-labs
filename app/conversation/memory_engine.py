import json
from collections import deque

class MemoryEngine:
    _storage = {}  # In-memory storage (dict of deques)
    MAX_HISTORY = 10  # Keep last 10 messages for context

    @classmethod
    def clear(cls, user_id):
        """Clear conversation history for a user."""
        cls._storage[user_id] = deque(maxlen=cls.MAX_HISTORY)

    @classmethod
    def add_user_message(cls, user_id, text):
        """Add a user message to history."""
        if user_id not in cls._storage:
            cls._storage[user_id] = deque(maxlen=cls.MAX_HISTORY)
        
        cls._storage[user_id].append({
            "role": "user", 
            "content": str(text).strip()
        })

    @classmethod
    def add_bot_message(cls, user_id, text):
        """Add a bot response to history."""
        if user_id not in cls._storage:
            cls._storage[user_id] = deque(maxlen=cls.MAX_HISTORY)
            
        cls._storage[user_id].append({
            "role": "assistant", 
            "content": str(text).strip()
        })

    @classmethod
    def get_conversation_context(cls, user_id):
        """Get recent conversation history as a list of dicts."""
        if user_id not in cls._storage:
            return []
        return list(cls._storage[user_id])
