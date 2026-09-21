import urllib.parse
import webbrowser

from .base import Command, parse_query


class MusicCommand(Command):
    name = "play_music"
    tool_name = "play_music"
    description = "Play music or a song on YouTube"
    keywords = ["play some ", "play music", "play the song", "play a song", "play ", "put on ", "music", "song "]
    parameters = {
        "type": "object",
        "properties": {
            "song": {"type": "string", "description": "Name of the song or music to play"}
        },
        "required": ["song"],
    }

    def run_keyword(self, text, ctx):
        return self._play(parse_query(text, self.keywords))

    def run_tool(self, args, ctx):
        return self._play(args.get("song"))

    def _play(self, song):
        if not song:
            return "Which song would you like to play?"
        url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(song)
        webbrowser.open(url)
        return f"Playing {song} on YouTube."