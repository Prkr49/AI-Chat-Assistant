import re
from typing import Any, Dict, List, Optional


class Command:
    name: str = "base"
    tool_name: Optional[str] = None
    description: str = ""
    keywords: List[str] = []
    patterns: List[str] = []
    parameters: Optional[Dict[str, Any]] = None

    def match(self, text: str) -> bool:
        lowered = text.lower()
        if any(keyword in lowered for keyword in self.keywords):
            return True
        return any(re.search(pattern, lowered) for pattern in self.patterns)

    def run_keyword(self, text: str, ctx: Any) -> str:
        return f"You said '{self.name}' but I don't know how to handle it yet."

    def run_tool(self, args: Dict[str, Any], ctx: Any) -> str:
        return self.run_keyword(str(args), ctx)


class CommandRegistry:
    def __init__(self) -> None:
        self._commands: Dict[str, Command] = {}

    def register(self, command: Command) -> None:
        self._commands[command.name] = command

    def get(self, name: str) -> Optional[Command]:
        return self._commands.get(name)

    def get_by_tool(self, tool_name: str) -> Optional[Command]:
        for command in self._commands.values():
            if command.tool_name == tool_name:
                return command
        return None

    def all(self) -> List[Command]:
        return list(self._commands.values())

    def find(self, text: str) -> Optional[Command]:
        best = None
        for command in self._commands.values():
            if command.match(text):
                if best is None or len(command.keywords) > len(best.keywords):
                    best = command
        return best


def normalize(text: str) -> str:
    result = text.strip()
    prefixes = [
        "hey nova",
        "hello nova",
        "hi nova",
        "nova",
        "please",
        "can you",
        "could you",
        "will you",
        "would you",
        "i want you to",
        "i need you to",
        "hey",
    ]
    changed = True
    while changed:
        changed = False
        for prefix in prefixes:
            if result.lower().startswith(prefix):
                result = result[len(prefix):].strip(" ,.:-")
                changed = True
    return result


def parse_query(text: str, words: List[str]) -> str:
    lowered = text.strip().lower()
    for word in sorted(words, key=len, reverse=True):
        if lowered.startswith(word):
            return text.strip()[len(word):].strip(" :.,-")
    return text.strip()