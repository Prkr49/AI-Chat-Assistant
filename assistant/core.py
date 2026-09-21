from .brain import Brain
from .commands import (
    BatteryCommand,
    CloseAppCommand,
    DateCommand,
    HelpCommand,
    KillProcessCommand,
    LockScreenCommand,
    MusicCommand,
    MuteCommand,
    NoteCommand,
    OpenAppCommand,
    ProcessListCommand,
    QuitCommand,
    ReminderCommand,
    RestartCommand,
    ScreenshotCommand,
    ShutdownCommand,
    SleepCommand,
    TimeCommand,
    UnmuteCommand,
    VolumeAdjustCommand,
    VolumeSetCommand,
    WebSearchCommand,
    WikiCommand,
)
from .commands.base import CommandRegistry, normalize
from .voice import Voice


class Assistant:
    def _build_registry(self):
        registry = CommandRegistry()
        for command in [
            TimeCommand(),
            DateCommand(),
            OpenAppCommand(),
            CloseAppCommand(),
            WebSearchCommand(),
            WikiCommand(),
            MusicCommand(),
            VolumeSetCommand(),
            VolumeAdjustCommand(),
            MuteCommand(),
            UnmuteCommand(),
            BatteryCommand(),
            ScreenshotCommand(),
            LockScreenCommand(),
            SleepCommand(),
            RestartCommand(),
            ShutdownCommand(),
            ProcessListCommand(),
            KillProcessCommand(),
            ReminderCommand(),
            NoteCommand(),
            HelpCommand(),
            QuitCommand(),
        ]:
            registry.register(command)
        return registry

    def __init__(self, text_mode=False):
        self.voice = Voice(text_mode=text_mode)
        self.brain = Brain()
        self.registry = self._build_registry()
        self.should_exit = False

    def tool_schemas(self):
        schemas = []
        for command in self.registry.all():
            if not command.tool_name:
                continue
            schemas.append(
                {
                    "type": "function",
                    "function": {
                        "name": command.tool_name,
                        "description": command.description,
                        "parameters": command.parameters or {"type": "object", "properties": {}},
                    },
                }
            )
        return schemas

    def _handle_tool(self, name, args):
        command = self.registry.get_by_tool(name)
        if command is None:
            self.voice.say(f"I'm not sure how to {name} yet.")
            return
        result = command.run_tool(args, self)
        self.voice.say(result)

    def _fallback(self, text):
        normalized = normalize(text)
        command = self.registry.find(normalized)
        if command is None:
            self.voice.say(
                f"I wasn't sure what to do when you said: {text}. "
                "Say help to see what I can do."
            )
            return
        result = command.run_keyword(normalized, self)
        self.voice.say(result)

    def respond(self, text):
        text = text.strip()
        if not text:
            return
        if self.brain.enabled:
            reply, calls = self.brain.ask(text, self.tool_schemas())
            if calls:
                for name, args in calls:
                    self._handle_tool(name, args)
            elif reply:
                self.voice.say(reply)
        else:
            self._fallback(text)

    def run(self):
        self.voice.say("Hello, I am Nova, your voice assistant.")
        if self.brain.enabled:
            self.voice.say("AI mode is ready. Ask me to command your computer.")
        else:
            self.voice.say(
                "No OpenAI key found, so I'm running in built-in command mode. "
                "Say help to see what I can do."
            )
        while not self.should_exit:
            try:
                text = self.voice.listen()
                if not text:
                    continue
                self.respond(text)
            except KeyboardInterrupt:
                break
            except Exception as exc:
                print(exc)
                self.voice.say("Sorry, something went wrong. Please try again.")