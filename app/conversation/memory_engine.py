import json
from collections import deque

class MemoryEngine:
    _store = {}
    LIMIT = 10

    @classmethod
    def clear(cls, user_id):
        cls._store[user_id] = []

    @classmethod
    def add_user_message(cls, user_id, text):
        if user_id not in cls._store:
            cls._store[user_id] = []
        cls._store[user_id].append({"role": "user", "content": text})
        cls._store[user_id] = cls._store[user_id][-cls.LIMIT:]

    @classmethod
    def add_bot_message(cls, user_id, text):
        if user_id not in cls._store:
            cls._store[user_id] = []
        cls._store[user_id].append({"role": "assistant", "content": text})
        cls._store[user_id] = cls._store[user_id][-cls.LIMIT:]

    @classmethod
    def get_context(cls, user_id):
        return cls._store.get(user_id, [])