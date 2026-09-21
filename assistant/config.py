import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")
LANGUAGE = os.getenv("LANGUAGE", "en-IN")
VOICE_RATE = os.getenv("VOICE_RATE", "185")
WAKE_WORD = os.getenv("WAKE_WORD", "nova").strip()
SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", os.path.join(BASE_DIR, "screenshots"))
NOTES_FILE = os.path.join(BASE_DIR, "notes.txt")