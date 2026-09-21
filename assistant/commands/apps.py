import shutil
import subprocess
import webbrowser

from .base import Command, parse_query

WINDOWS_APPS = {
    "notepad": "notepad",
    "calculator": "calc",
    "paint": "mspaint",
    "file explorer": "explorer",
    "terminal": "cmd",
    "command prompt": "cmd",
    "powershell": "powershell",
    "task manager": "taskmgr",
    "control panel": "control",
    "registry editor": "regedit",
    "settings": "ms-settings:",
    "chrome": "chrome",
    "edge": "msedge",
    "firefox": "firefox",
    "spotify": "spotify",
    "discord": "discord",
    "vscode": "code",
    "visual studio code": "code",
}

WEB_APPS = {
    "youtube": "https://www.youtube.com",
    "gmail": "https://mail.google.com",
    "google": "https://www.google.com",
    "maps": "https://maps.google.com",
    "wikipedia": "https://www.wikipedia.org",
    "netflix": "https://www.netflix.com",
    "instagram": "https://www.instagram.com",
    "whatsapp": "https://web.whatsapp.com",
    "github": "https://github.com",
    "twitter": "https://twitter.com",
    "x": "https://twitter.com",
    "facebook": "https://www.facebook.com",
}

FRIENDLY_TO_EXE = {
    name: exe + ".exe" if not exe.lower().endswith(".exe") else exe
    for name, exe in WINDOWS_APPS.items()
    if exe.lower() not in ("", "ms-settings:")
}


class OpenAppCommand(Command):
    name = "open_app"
    tool_name = "open_application"
    description = "Open a local application, website or web app"
    keywords = ["open ", "launch ", "start ", "run "]
    parameters = {
        "type": "object",
        "properties": {
            "app_name": {"type": "string", "description": "Name of the app, website or web app to open"}
        },
        "required": ["app_name"],
    }

    def run_keyword(self, text, ctx):
        return self._launch(parse_query(text, self.keywords))

    def run_tool(self, args, ctx):
        return self._launch(args.get("app_name") or args.get("name"))

    def _launch(self, target):
        if not target:
            return "Which application should I open?"
        key = target.strip().lower()
        if key in WEB_APPS:
            webbrowser.open(WEB_APPS[key])
            return f"Opening {key} in the browser."
        if key in WINDOWS_APPS:
            try:
                subprocess.Popen("start " + WINDOWS_APPS[key], shell=True)
                return f"Opening {key}."
            except Exception as exc:
                return f"Could not open {key}: {exc}."
        exe = shutil.which(target) or shutil.which(target + ".exe")
        if exe:
            try:
                subprocess.Popen([exe])
                return f"Opening {target}."
            except Exception as exc:
                return f"Could not open {target}: {exc}."
        return (
            f"I couldn't find {target}. "
            "Use the exact name, or ask me to open a website like youtube or gmail."
        )


class CloseAppCommand(Command):
    name = "close_app"
    tool_name = "close_application"
    description = "Close or quit a running application"
    keywords = ["close ", "quit ", "exit ", "stop "]
    parameters = {
        "type": "object",
        "properties": {
            "app_name": {"type": "string", "description": "Name of the running application to close"}
        },
        "required": ["app_name"],
    }

    def run_keyword(self, text, ctx):
        return self._close(parse_query(text, self.keywords))

    def run_tool(self, args, ctx):
        return self._close(args.get("app_name") or args.get("name"))

    def _close(self, name):
        if not name:
            return "Which application should I close?"
        exe = FRIENDLY_TO_EXE.get(name.lower(), name)
        if "." not in exe:
            exe += ".exe"
        try:
            subprocess.run(["taskkill", "/IM", exe, "/F"], capture_output=True, text=True, timeout=15)
            return f"I've closed {name}."
        except Exception as exc:
            return f"Could not close {name}: {exc}."