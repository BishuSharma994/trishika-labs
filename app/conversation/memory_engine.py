from collections import deque


class MemoryEngine:
    """
    Stores recent conversation context for each user.
    Allows the bot to reference previous discussion.
    """

    MAX_HISTORY = 10

    memory = {}

    @staticmethod
    def get_history(user_id):

        if user_id not in MemoryEngine.memory:
            MemoryEngine.memory[user_id] = deque(maxlen=MemoryEngine.MAX_HISTORY)

        return MemoryEngine.memory[user_id]

    @staticmethod
    def add_user_message(user_id, message):

        history = MemoryEngine.get_history(user_id)

        history.append({
            "role": "user",
            "content": message
        })

    @staticmethod
    def add_bot_message(user_id, message):

        history = MemoryEngine.get_history(user_id)

        history.append({
            "role": "assistant",
            "content": message
        })

    @staticmethod
    def build_context(user_id):

        history = MemoryEngine.get_history(user_id)

        if not history:
            return ""

        lines = []

        for msg in history:

            if msg["role"] == "user":
                lines.append(f"User: {msg['content']}")
            else:
                lines.append(f"Astrologer: {msg['content']}")

        return "\n".join(lines)

    @staticmethod
    def clear(user_id):

        MemoryEngine.memory[user_id] = deque(maxlen=MemoryEngine.MAX_HISTORY)