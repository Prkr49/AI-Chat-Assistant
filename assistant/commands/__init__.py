from .base import Command, CommandRegistry, normalize, parse_query
from .apps import CloseAppCommand, OpenAppCommand
from .web import WebSearchCommand, WikiCommand
from .music import MusicCommand
from .system import (
    BatteryCommand,
    DateCommand,
    KillProcessCommand,
    LockScreenCommand,
    MuteCommand,
    ProcessListCommand,
    RestartCommand,
    ScreenshotCommand,
    ShutdownCommand,
    SleepCommand,
    TimeCommand,
    UnmuteCommand,
    VolumeAdjustCommand,
    VolumeSetCommand,
)
from .tasks import NoteCommand, ReminderCommand
from .misc import HelpCommand, QuitCommand

__all__ = [
    "Command",
    "CommandRegistry",
    "normalize",
    "parse_query",
    "CloseAppCommand",
    "OpenAppCommand",
    "WebSearchCommand",
    "WikiCommand",
    "MusicCommand",
    "BatteryCommand",
    "DateCommand",
    "KillProcessCommand",
    "LockScreenCommand",
    "MuteCommand",
    "ProcessListCommand",
    "RestartCommand",
    "ScreenshotCommand",
    "ShutdownCommand",
    "SleepCommand",
    "TimeCommand",
    "UnmuteCommand",
    "VolumeAdjustCommand",
    "VolumeSetCommand",
    "NoteCommand",
    "ReminderCommand",
    "HelpCommand",
    "QuitCommand",
]