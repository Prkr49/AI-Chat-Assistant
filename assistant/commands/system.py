import ctypes
import datetime
import os
import re
import subprocess
import time

from .. import config
from .base import Command, parse_query


def _volume_device():
    try:
        from pycaw.pycaw import AudioUtilities
    except Exception:
        return None
    try:
        device = AudioUtilities.GetSpeakers()
    except Exception:
        return None
    if hasattr(device, "EndpointVolume"):
        return device.EndpointVolume
    try:
        from ctypes import POINTER, cast

        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import IAudioEndpointVolume

        interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))
    except Exception:
        return None


class TimeCommand(Command):
    name = "time"
    tool_name = "get_time"
    description = "Get the current local time"
    keywords = ["what time", "current time", "time is it", "tell me the time"]
    parameters = {"type": "object", "properties": {}}

    def run_keyword(self, text, ctx):
        return self._reply()

    def run_tool(self, args, ctx):
        return self._reply()

    def _reply(self):
        return f"The time is {datetime.datetime.now():%I:%M %p}."


class DateCommand(Command):
    name = "date"
    tool_name = "get_date"
    description = "Get today's date"
    keywords = ["today's date", "what day", "current date", "today is", "day of week"]
    parameters = {"type": "object", "properties": {}}

    def run_keyword(self, text, ctx):
        return self._reply()

    def run_tool(self, args, ctx):
        return self._reply()

    def _reply(self):
        return f"Today is {datetime.datetime.now():%A, %B %d, %Y}."


class VolumeSetCommand(Command):
    name = "set_volume"
    tool_name = "set_volume"
    description = "Set the system volume to a specific level from 0 to 100"
    keywords = ["set volume", "volume to "]
    parameters = {
        "type": "object",
        "properties": {
            "level": {"type": "integer", "minimum": 0, "maximum": 100}
        },
        "required": ["level"],
    }

    def run_keyword(self, text, ctx):
        match = re.search(r"(\d{1,3})\s*%?", text)
        if not match:
            return "Please tell me a volume level, like set volume to 50."
        return self._set(int(match.group(1)))

    def run_tool(self, args, ctx):
        return self._set(int(args.get("level", 50)))

    def _set(self, level):
        device = _volume_device()
        if device is None:
            return "Volume control is not available on this system."
        level = max(0, min(100, int(level)))
        try:
            device.SetMasterVolumeLevelScalar(level / 100.0, None)
            return f"Volume set to {level} percent."
        except Exception as exc:
            return f"Could not set volume: {exc}."


class VolumeAdjustCommand(Command):
    name = "volume_adjust"
    tool_name = "adjust_volume"
    description = "Turn the volume up or down"
    keywords = [
        "volume up",
        "volume down",
        "increase volume",
        "decrease volume",
        "turn it up",
        "turn it down",
        "louder",
        "quieter",
    ]
    parameters = {
        "type": "object",
        "properties": {
            "delta": {"type": "integer", "description": "Positive raises volume, negative lowers it"}
        },
        "required": ["delta"],
    }

    def run_keyword(self, text, ctx):
        lowered = text.lower()
        up = any(word in lowered for word in ["up", "increase", "louder", "turn it up"])
        match = re.search(r"by\s+(\d{1,3})", lowered)
        step = int(match.group(1)) if match else 10
        return self._adjust(step if up else -step)

    def run_tool(self, args, ctx):
        return self._adjust(int(args.get("delta", 10)))

    def _adjust(self, delta):
        device = _volume_device()
        if device is None:
            return "Volume control is not available on this system."
        try:
            current = device.GetMasterVolumeLevelScalar()
            level = max(0.0, min(1.0, current + int(delta) / 100.0))
            device.SetMasterVolumeLevelScalar(level, None)
            direction = "up" if delta > 0 else "down"
            return f"Volume turned {direction} to {round(level * 100)} percent."
        except Exception as exc:
            return f"Could not adjust volume: {exc}."


class MuteCommand(Command):
    name = "mute_volume"
    tool_name = "mute_volume"
    description = "Mute the system volume"
    keywords = ["mute", "silence"]
    parameters = {"type": "object", "properties": {}}

    def run_keyword(self, text, ctx):
        return self._set_muted(True)

    def run_tool(self, args, ctx):
        return self._set_muted(True)

    def _set_muted(self, muted):
        device = _volume_device()
        if device is None:
            return "Volume control is not available on this system."
        try:
            device.SetMute(1 if muted else 0, None)
            return "The volume is muted." if muted else "The volume is unmuted."
        except Exception as exc:
            return f"Could not mute volume: {exc}."


class UnmuteCommand(Command):
    name = "unmute_volume"
    tool_name = "unmute_volume"
    description = "Unmute the system volume"
    keywords = ["unmute", "unmute sound", "turn sound back on"]
    parameters = {"type": "object", "properties": {}}

    def run_keyword(self, text, ctx):
        return MuteCommand()._set_muted(False)

    def run_tool(self, args, ctx):
        return MuteCommand()._set_muted(False)


class BatteryCommand(Command):
    name = "battery"
    tool_name = "get_battery"
    description = "Check the battery status"
    keywords = ["battery", "charge", "power level"]
    parameters = {"type": "object", "properties": {}}

    def run_keyword(self, text, ctx):
        return self._reply()

    def run_tool(self, args, ctx):
        return self._reply()

    def _reply(self):
        try:
            import psutil
        except ImportError:
            return "psutil is not installed. Run pip install psutil."
        battery = psutil.sensors_battery()
        if battery is None:
            return "Battery information is not available on this system."
        status = "on battery" if not battery.power_plugged else "plugged in"
        return f"Battery is at {battery.percent} percent, {status}."


class ScreenshotCommand(Command):
    name = "screenshot"
    tool_name = "take_screenshot"
    description = "Take a screenshot and save it to a file"
    keywords = ["screenshot", "capture screen", "screen capture"]
    parameters = {"type": "object", "properties": {}}

    def run_keyword(self, text, ctx):
        return self._shot()

    def run_tool(self, args, ctx):
        return self._shot()

    def _shot(self):
        try:
            import pyautogui
        except ImportError:
            return "pyautogui is not installed. Run pip install pyautogui."
        try:
            os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
            path = os.path.join(config.SCREENSHOT_DIR, "screenshot_" + str(int(time.time())) + ".png")
            pyautogui.screenshot(path)
            return f"Screenshot saved to {path}."
        except Exception as exc:
            return f"Could not take a screenshot: {exc}."


class LockScreenCommand(Command):
    name = "lock_screen"
    tool_name = "lock_screen"
    description = "Lock the computer screen"
    keywords = ["lock the screen", "lock screen", "lock the computer", "lock computer"]
    parameters = {"type": "object", "properties": {}}

    def run_keyword(self, text, ctx):
        return self._lock()

    def run_tool(self, args, ctx):
        return self._lock()

    def _lock(self):
        try:
            ctypes.windll.user32.LockWorkStation()
            return "Locking your screen."
        except Exception as exc:
            return f"Could not lock the screen: {exc}."


class SleepCommand(Command):
    name = "sleep_computer"
    tool_name = "sleep_computer"
    description = "Put the computer to sleep"
    keywords = ["sleep the computer", "computer to sleep", "go to sleep", "hibernate"]
    parameters = {"type": "object", "properties": {}}

    def run_keyword(self, text, ctx):
        return self._sleep()

    def run_tool(self, args, ctx):
        return self._sleep()

    def _sleep(self):
        try:
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
            return "Putting the computer to sleep."
        except Exception as exc:
            return f"Could not put the computer to sleep: {exc}."


class RestartCommand(Command):
    name = "restart_computer"
    tool_name = "restart_computer"
    description = "Restart the computer"
    keywords = ["restart the computer", "restart computer", "reboot", "reboot the computer"]
    parameters = {"type": "object", "properties": {}}

    def run_keyword(self, text, ctx):
        return self._restart()

    def run_tool(self, args, ctx):
        return self._restart()

    def _restart(self):
        try:
            subprocess.run(["shutdown", "/r", "/t", "10"], check=True)
            return "Restarting in ten seconds. See you soon!"
        except Exception as exc:
            return f"Could not restart the computer: {exc}."


class ShutdownCommand(Command):
    name = "shutdown_computer"
    tool_name = "shutdown_computer"
    description = "Shut down the computer"
    keywords = ["shut down the computer", "shut down my computer", "shutdown the computer", "shutdown the pc", "power off"]
    parameters = {"type": "object", "properties": {}}

    def run_keyword(self, text, ctx):
        return self._shutdown()

    def run_tool(self, args, ctx):
        return self._shutdown()

    def _shutdown(self):
        try:
            subprocess.run(["shutdown", "/s", "/t", "10"], check=True)
            return "Shutting down in ten seconds. Goodbye!"
        except Exception as exc:
            return f"Could not shut down the computer: {exc}."


class ProcessListCommand(Command):
    name = "list_processes"
    tool_name = "list_processes"
    description = "List the top running processes by CPU usage"
    keywords = ["running processes", "task list", "what apps are running", "processes running"]
    parameters = {"type": "object", "properties": {}}

    def run_keyword(self, text, ctx):
        return self._list()

    def run_tool(self, args, ctx):
        return self._list()

    def _list(self):
        try:
            import psutil
        except ImportError:
            return "psutil is not installed. Run pip install psutil."
        processes = []
        for proc in psutil.process_iter(["name", "cpu_percent"]):
            try:
                processes.append((proc.info["name"] or "?", proc.info["cpu_percent"] or 0.0))
            except Exception:
                continue
        processes.sort(key=lambda item: item[1], reverse=True)
        top = processes[:8]
        if not top:
            return "No running processes found."
        names = ", ".join(name for name, _ in top)
        return "The top processes are " + names + "."


class KillProcessCommand(Command):
    name = "kill_process"
    tool_name = "kill_process"
    description = "Stop or kill a running process by name"
    keywords = ["kill process", "stop process", "end process", "stop using "]
    parameters = {
        "type": "object",
        "properties": {
            "process": {"type": "string", "description": "The name of the process or application to stop"}
        },
        "required": ["process"],
    }

    def run_keyword(self, text, ctx):
        return self._kill(parse_query(text, self.keywords))

    def run_tool(self, args, ctx):
        return self._kill(args.get("process"))

    def _kill(self, target):
        if not target:
            return "Which process should I stop?"
        try:
            import psutil
        except ImportError:
            return "psutil is not installed. Run pip install psutil."
        matches = []
        for proc in psutil.process_iter(["name", "pid"]):
            try:
                if target.lower() in (proc.info["name"] or "").lower():
                    matches.append(proc)
            except Exception:
                continue
        if not matches:
            return f"No running process matched {target}."
        killed = []
        for proc in matches[:3]:
            try:
                proc.terminate()
                killed.append(proc.info["name"] or "?")
            except Exception:
                continue
        if not killed:
            return f"Could not stop {target}."
        unique = list(dict.fromkeys(killed))
        return f"Stopped {len(killed)} process: " + ", ".join(unique) + "."