import urllib.parse
import webbrowser

from .base import Command, parse_query

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    )
}


def instant_answer(query):
    try:
        import requests
    except ImportError:
        return ""
    try:
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            headers=HEADERS,
            timeout=10,
        )
        data = response.json()
    except Exception:
        return ""
    abstract = (data.get("AbstractText") or "").strip()
    if abstract:
        return abstract
    snippets = []
    for topic in data.get("RelatedTopics") or []:
        text = topic.get("Text")
        if text:
            snippets.append(text)
        if len(snippets) >= 2:
            break
    return " ".join(snippets)


class WebSearchCommand(Command):
    name = "web_search"
    tool_name = "web_search"
    description = "Search the web and report the top result"
    keywords = ["search web", "search the web", "search for", "look it up", "look up", "google ", "search "]
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query"}
        },
        "required": ["query"],
    }

    def run_keyword(self, text, ctx):
        query = parse_query(text, self.keywords)
        for connector in ["for me ", "for ", "the web ", "about ", "on google "]:
            if query.lower().startswith(connector):
                query = query[len(connector):].strip(" :.,-")
        return self._search(query)

    def run_tool(self, args, ctx):
        return self._search(args.get("query"))

    def _search(self, query):
        if not query:
            return "What would you like me to search for?"
        url = "https://duckduckgo.com/?q=" + urllib.parse.quote_plus(query)
        webbrowser.open(url)
        answer = instant_answer(query)
        if answer:
            return f"Here's what I found for {query}. {answer[:300]}"
        return f"I opened a browser tab with the search results for {query}."


class WikiCommand(Command):
    name = "wikipedia"
    tool_name = "wikipedia"
    description = "Get a short Wikipedia summary about a topic"
    keywords = ["wikipedia", "tell me about", "define "]
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The topic to look up"}
        },
        "required": ["query"],
    }

    def run_keyword(self, text, ctx):
        return self._summary(parse_query(text, self.keywords))

    def run_tool(self, args, ctx):
        return self._summary(args.get("query"))

    def _summary(self, query):
        if not query:
            return "Which topic should I look up?"
        summary = ""
        try:
            import wikipedia

            summary = wikipedia.summary(query, sentences=2, auto_suggest=True)
        except Exception:
            summary = ""
        if not summary:
            summary = instant_answer(query)
        if summary:
            return summary[:400]
        return f"I couldn't find information about {query} right now."