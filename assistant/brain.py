import json

from . import config

SYSTEM_PROMPT = (
    "You are Nova, a friendly voice assistant running on the user's Windows computer. "
    "When the user asks you to do something you can perform - opening apps, searching the "
    "web, playing music, controlling the system, setting reminders, taking notes, or "
    "reporting time, date or battery status - call the appropriate tool with the needed "
    "arguments. Otherwise reply to the user conversationally. Always reply as if speaking "
    "aloud: concise, natural, no markdown and no emojis, at most two sentences."
)


class Brain:
    def __init__(self):
        self.model = config.AI_MODEL
        self.enabled = bool(config.OPENAI_API_KEY)
        self.history = []
        self.client = None
        if self.enabled:
            try:
                from openai import OpenAI

                self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            except Exception as exc:
                print("[brain] OpenAI unavailable, falling back to keyword commands:", exc)
                self.enabled = False

    def reset(self):
        self.history = []

    def ask(self, text, tools):
        self.history.append({"role": "user", "content": text})
        if len(self.history) > 24:
            self.history = self.history[-24:]
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + self.history,
                tools=tools,
                tool_choice="auto",
            )
        except Exception as exc:
            print("[brain] API error:", exc)
            return "", []
        message = response.choices[0].message
        if getattr(message, "tool_calls", None):
            calls = []
            for call in message.tool_calls:
                args = {}
                try:
                    args = json.loads(call.function.arguments or "{}")
                except Exception:
                    args = {}
                calls.append((call.function.name, args))
            return "", calls
        content = (message.content or "").strip()
        if content:
            self.history.append({"role": "assistant", "content": content})
        return content, []