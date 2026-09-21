from .base import Command


class HelpCommand(Command):
    name = "help"
    description = "Show the list of available commands and features"
    keywords = ["help", "what can you do", "list of commands", "commands list", "your abilities"]

    def run_keyword(self, text, ctx):
        lines = ["Here is what I can do."]
        for command in ctx.registry.all():
            if command.name in ("help", "quit"):
                continue
            lines.append(command.description or command.name + ".")
        return " ".join(line + "." if not line.endswith(".") else line for line in lines)


class QuitCommand(Command):
    name = "quit"
    description = "Stop the assistant"
    keywords = ["goodbye", "bye", "good night", "stop listening", "exit assistant", "quit assistant", "shut up"]

    def run_keyword(self, text, ctx):
        ctx.should_exit = True
        return "Goodbye, have a nice day!"