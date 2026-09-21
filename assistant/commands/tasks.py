import datetime
import re
import threading

from .. import config
from .base import Command


def parse_duration(text):
    lowered = text.lower()
    total = 0
    patterns = [
        (r"(\d+)\s*(?:hours?|hrs?|h)\b", 3600),
        (r"(\d+)\s*(?:minutes?|mins?|min)\b", 60),
        (r"(\d+)\s*(?:seconds?|secs?|sec)\b", 1),
    ]
    for pattern, multiplier in patterns:
        for match in re.finditer(pattern, lowered):
            total += int(match.group(1)) * multiplier
    return total


def format_duration(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    parts = []
    if hours:
        parts.append(str(hours) + " hour" + ("s" if hours != 1 else ""))
    if minutes:
        parts.append(str(minutes) + " minute" + ("s" if minutes != 1 else ""))
    if secs:
        parts.append(str(secs) + " second" + ("s" if secs != 1 else ""))
    return " and ".join(parts) if parts else "0 seconds"


def extract_reminder_message(text):
    lowered = text.lower()
    message = text
    for lead in [
        "remind me to",
        "remind me",
        "set a reminder for",
        "set a reminder to",
        "set a reminder",
        "set a timer for",
        "set a timer",
        "remember to",
        "remind",
    ]:
        if lowered.startswith(lead):
            message = text[len(lead):]
            break
    for pattern in [r"\s+in\s+\d+[^,.]*$", r"\s+after\s+\d+[^,.]*$"]:
        message = re.sub(pattern, "", message)
    message = message.strip(" :.,-")
    if message.lower().startswith("to "):
        message = message[3:]
    if re.fullmatch(r"\d+\s*\w+", message.strip()):
        return ""
    return message.strip().capitalize()


class ReminderCommand(Command):
    name = "set_reminder"
    tool_name = "set_reminder"
    description = "Set a reminder or timer that speaks after a delay"
    keywords = ["remind me", "reminder", "set a timer", "remind", "timer", "in "]
    parameters = {
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "What to remind the user about"},
            "seconds": {"type": "integer", "description": "Delay in seconds"},
        },
        "required": ["message", "seconds"],
    }

    def run_keyword(self, text, ctx):
        seconds = parse_duration(text)
        message = extract_reminder_message(text)
        return self._set(message or "Your reminder is due", seconds, ctx)

    def run_tool(self, args, ctx):
        seconds = int(args.get("seconds", 0))
        message = args.get("message") or "Your reminder is due"
        return self._set(message, seconds, ctx)

    def _set(self, message, seconds, ctx):
        if not seconds or seconds <= 0:
            return "Please include a duration, like remind me to stretch in 5 minutes."
        delay = format_duration(seconds)

        def ring():
            ctx.voice.say(message)
            ctx.voice.say("That was your reminder.")

        timer = threading.Timer(seconds, ring)
        timer.daemon = True
        timer.start()
        return f"Okay, I'll remind you in {delay}: {message}."


class NoteCommand(Command):
    name = "add_note"
    tool_name = "add_note"
    description = "Save a note to notes.txt"
    keywords = ["note down", "take a note", "take note", "remember this", "save a note", "write down", "note "]
    parameters = {
        "type": "object",
        "properties": {
            "note": {"type": "string", "description": "The text to save as a note"}
        },
        "required": ["note"],
    }

    def run_keyword(self, text, ctx):
        stripped = text
        for lead in ["note down", "take a note", "take note", "remember this", "save a note", "write down"]:
            if stripped.lower().startswith(lead):
                stripped = stripped[len(lead):]
                break
        stripped = stripped.strip(" :.,-")
        if stripped.lower().startswith("that "):
            stripped = stripped[5:]
        return self._save(stripped)

    def run_tool(self, args, ctx):
        return self._save(args.get("note"))

    def _save(self, note):
        if not note:
            return "What should I note down?"
        try:
            with open(config.NOTES_FILE, "a", encoding="utf-8") as handle:
                handle.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M}] {note}\n")
            return f"Noted: {note}."
        except Exception as exc:
            return f"Could not save the note: {exc}."