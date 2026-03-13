from collections import deque
import re


class MemoryEngine:
    """
    Stores recent conversation context for each user.
    Allows the bot to reference previous discussion.
    """

    MAX_HISTORY = 24

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
    def build_context_brief(user_id, max_items=6):

        history = list(MemoryEngine.get_history(user_id))
        if not history:
            return ""

        concise = []
        skip_exact = {
            "/start",
            "english",
            "hindi (roman)",
            "हिंदी",
            "1 haan",
            "1 yes",
            "1 मेरी कुंडली",
            "1 meri kundli",
            "1 my chart",
            "career",
            "finance",
            "health",
            "shaadi",
            "marriage",
            "job switch",
            "stress",
        }

        for msg in reversed(history):
            role = msg.get("role")
            content = " ".join(str(msg.get("content") or "").strip().split())
            lowered = content.lower()
            if not content:
                continue

            if role == "user":
                if lowered in skip_exact:
                    continue
                if len(re.findall(r"\w+", lowered)) <= 2 and not content.endswith("?"):
                    continue
                concise.append(f"User concern: {content}")
            else:
                if len(re.findall(r"\w+", lowered)) < 5:
                    continue
                concise.append(f"Astrologer replied: {content}")

            if len(concise) >= max_items:
                break

        return "\n".join(reversed(concise))

    @staticmethod
    def clear(user_id):

        MemoryEngine.memory[user_id] = deque(maxlen=MemoryEngine.MAX_HISTORY)
