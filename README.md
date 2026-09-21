# Nova - AI Voice Assistant 🤖🎙️

A modular, extensible voice assistant for Windows that executes **voice commands**, **automates system tasks**, and improves **user productivity** through natural language interaction.

Built with Python, speech recognition, text-to-speech, and the OpenAI API. Nova understands what you say, decides which capability to use (via OpenAI function calling), performs the action, and replies out loud.

## Features

- **Voice interaction** - speak to Nova and it replies out loud (SpeechRecognition + pyttsx3)
- **AI conversation** - OpenAI function calling routes your intent to the right capability; falls back to smart keyword matching when no API key is set
- **Web search** - searches the web (DuckDuckGo), opens results in the browser, and reads back the top answer
- **Knowledge lookup** - short Wikipedia summaries, with a DuckDuckGo fallback if Wikipedia is unreachable
- **Application launching** - opens local apps, websites, and web apps, or closes running programs
- **Music playback** - plays any song on YouTube from a spoken request
- **System automation**
  - Volume: set a level, turn up/down, mute/unmute
  - Battery status
  - Screenshots
  - Lock screen, sleep, restart, and shutdown
  - List and kill running processes
  - Current time and date
- **Productivity helpers**
  - Reminders / timers ("remind me to stretch in 5 minutes")
  - Quick notes saved to `notes.txt`
- **Modular & extensible architecture** - every capability is a `Command` class registered in a `CommandRegistry`. Adding a new command automatically exposes it to the AI as a callable tool.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Language | Python 3.9+ |
| Understanding | OpenAI API (function calling) |
| Speech input | SpeechRecognition + PyAudio |
| Speech output | pyttsx3 (offline SAPI5 voice) |
| System info | psutil |
| Volume control | pycaw |
| Screenshots | PyAutoGUI |
| Web data | requests + DuckDuckGo API, wikipedia |

## Project Structure

```
AI-Chat-Assistant/
├── main.py                        # entry point (voice / text / single-task modes)
├── requirements.txt
├── .env.example                   # copy to .env and add your key
├── assistant/
│   ├── core.py                    # Assistant: orchestrates voice + brain + commands
│   ├── voice.py                   # speech recognition + text-to-speech
│   ├── brain.py                   # OpenAI function-calling interface
│   ├── config.py                  # settings loaded from environment / .env
│   └── commands/
│       ├── base.py                # Command base class + CommandRegistry + helpers
│       ├── apps.py                # open / close applications
│       ├── web.py                 # web search + Wikipedia
│       ├── music.py               # YouTube playback
│       ├── system.py              # volume, battery, screenshot, locks, processes...
│       ├── tasks.py               # reminders, notes
│       └── misc.py                # help, quit
```

## Installation

```bash
git clone https://github.com/Prkr49/AI-Chat-Assistant.git
cd AI-Chat-Assistant
pip install -r requirements.txt
```

> On Windows, `pyaudio` ships a prebuilt wheel on PyPI, so a plain `pip install` usually works. If it fails, install it from [PyAudio wheels](https://pypi.org/project/PyAudio/#files).

## Configuration

Copy `.env.example` to `.env` and adjust:

```bash
copy .env.example .env
```

| Variable | Default | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | *(empty)* | Your OpenAI API key. Without it, Nova runs in built-in command mode. |
| `AI_MODEL` | `gpt-4o-mini` | Model used for understanding and conversation. |
| `LANGUAGE` | `en-IN` | Speech recognition locale (e.g. `en-US`, `hi-IN`). |
| `VOICE_RATE` | `185` | Speaking speed in words per minute. |
| `WAKE_WORD` | `nova` | Word to say before a command. Set empty to listen continuously. |
| `SCREENSHOT_DIR` | `./screenshots` | Where screenshots are saved. |

## How to Run

```bash
python main.py                          # voice mode (requires a microphone)
python main.py --text                   # type your commands instead of speaking
python main.py --task "what time is it" # run one command and exit
```

If no microphone is detected, Nova automatically falls back to typed input.

### Example voice commands

> "Nova, open notepad"
> "Nova, play shape of you"
> "Nova, search the web for python tutorials"
> "Nova, tell me about black holes"
> "Nova, set volume to 40"
> "Nova, turn the volume up"
> "Nova, remind me to drink water in 10 minutes"
> "Nova, note down buy milk"
> "Nova, take a screenshot"
> "Nova, what's my battery"
> "Nova, what's running"
> "Nova, lock the screen"

## Command Reference

| Capability | Tool / command | Example |
| --- | --- | --- |
| Open app / site | `open_application` | open chrome, open gmail |
| Close app | `close_application` | close notepad |
| Web search | `web_search` | search the web for AI news |
| Wikipedia | `wikipedia` | tell me about quantum computing |
| Play music | `play_music` | play believer |
| Set volume | `set_volume` | set volume to 30 |
| Adjust volume | `adjust_volume` | volume up, volume down |
| Mute / unmute | `mute_volume` / `unmute_volume` | mute |
| Battery | `get_battery` | what's my battery |
| Screenshot | `take_screenshot` | take a screenshot |
| Lock screen | `lock_screen` | lock the computer |
| Sleep | `sleep_computer` | put the computer to sleep |
| Restart | `restart_computer` | restart the computer |
| Shutdown | `shutdown_computer` | shut down the computer |
| List processes | `list_processes` | what apps are running |
| Kill process | `kill_process` | kill process chrome |
| Reminder | `set_reminder` | remind me to call mom in 20 minutes |
| Note | `add_note` | note down buy milk |
| Time / date | `get_time` / `get_date` | what time is it |
| Help | *(local)* | help |

## How the AI Routing Works

1. `main.py` starts the `Assistant`.
2. `voice.py` captures speech (or typed text) and converts it to a string.
3. If an API key is set, `brain.py` sends the text plus all registered tool schemas to OpenAI. The model either replies conversationally or returns a tool call.
4. `core.py` dispatches the tool call to the matching `Command`, which performs the action and returns a spoken response.
5. Without an API key, `core.py` uses keyword matching (`CommandRegistry.find`) instead.

## Adding a New Command

Create a class in `assistant/commands/` that subclasses `Command` and register it in `assistant/core.py`:

```python
from .base import Command


class GreetCommand(Command):
    name = "greet"
    tool_name = "greet"
    description = "Say hello back to the user"
    keywords = ["hello", "hi", "hey"]
    parameters = {"type": "object", "properties": {}}

    def run_keyword(self, text, ctx):
        return "Hello to you too!"

    def run_tool(self, args, ctx):
        return "Hello to you too!"
```

Then add `GreetCommand()` to the list in `Assistant._build_registry`. Because `tool_name`, `description`, and `parameters` live on the class, the command is automatically exposed to the AI as a callable tool - no other wiring needed.

## Troubleshooting

- **No microphone / recognition errors** - check Windows microphone permissions, then run `python main.py --text` to use typed input.
- **`pyaudio` install fails** - install the matching wheel from [PyAudio wheels](https://pypi.org/project/PyAudio/#files).
- **Volume commands say unavailable** - ensure `pycaw` is installed and an audio output device is active.
- **No AI conversation, only commands** - set `OPENAI_API_KEY` in `.env`.
- **Wikipedia lookup times out** - Nova automatically falls back to a DuckDuckGo answer.

## Disclaimer

Nova can control your computer (shutdown, restart, kill processes, lock screen). Use it at your own risk.

## License

MIT
