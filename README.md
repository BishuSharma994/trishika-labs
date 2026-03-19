## Trishika Labs Astrology Bot

Telegram astrology bot with a strict onboarding flow and a deterministic consultation engine.

### Live Runtime Path

`app/main.py` -> `app/conversation/dialog_engine.py` -> `app/conversation/consultation_engine.py`

This is the only shipped conversation path in the repo.

### Product Rules

- Onboarding order is fixed.
- Supported languages are English and Roman Hindi.
- First consultation reply gives full astrology structure.
- Follow-up replies adapt to user intent instead of repeating the same template.

### Local Run

1. Install dependencies from `requirements.txt`.
2. Set `.env` with Telegram and AI keys if needed.
3. Run the FastAPI app that serves the Telegram webhook.

### Conversation Simulation

Run:

```bash
python3 scripts/simulate_conversation.py
```

This exercises the real `DialogEngine` path with deterministic in-memory stubs and prints an overall conversation rating.
