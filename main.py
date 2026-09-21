import argparse

from assistant.core import Assistant


def main():
    parser = argparse.ArgumentParser(description="Nova - a modular voice assistant")
    parser.add_argument("--text", action="store_true", help="type your commands instead of speaking")
    parser.add_argument("--task", help="run a single text command once and exit")
    args = parser.parse_args()

    assistant = Assistant(text_mode=bool(args.text or args.task))
    if args.task:
        assistant.respond(args.task)
        return
    assistant.run()


if __name__ == "__main__":
    main()