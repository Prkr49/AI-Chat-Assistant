import threading

from . import config


class Voice:
    def __init__(self, text_mode: bool = False):
        self.text_mode = text_mode
        self.language = config.LANGUAGE
        self.rate = int(config.VOICE_RATE)
        self.wake_word = config.WAKE_WORD.lower()
        self._lock = threading.Lock()
        self.engine = self._init_engine()
        self.mic = None
        self.recognizer = None
        self._init_recognizer()

    def _init_engine(self):
        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            try:
                for voice in engine.getProperty("voices"):
                    if voice.name and any(
                        word in voice.name.lower() for word in ("zira", "david", "natural")
                    ):
                        engine.setProperty("voice", voice.id)
                        break
            except Exception:
                pass
            return engine
        except Exception as exc:
            print("[voice] Text-to-speech unavailable:", exc)
            return None

    def _init_recognizer(self):
        if self.text_mode:
            return
        try:
            import speech_recognition as sr

            self.recognizer = sr.Recognizer()
            self.mic = sr.Microphone()
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        except Exception as exc:
            print("[voice] Microphone unavailable, falling back to text input:", exc)
            self.recognizer = None
            self.mic = None

    def say(self, text):
        print("[assistant]", text)
        with self._lock:
            if self.engine is None:
                return
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                try:
                    self.engine = self._init_engine()
                    if self.engine is not None:
                        self.engine.say(text)
                        self.engine.runAndWait()
                except Exception as exc:
                    print("[voice] Text-to-speech failed:", exc)

    def listen(self):
        if self.mic is None or self.recognizer is None:
            try:
                return input("[you] ").strip() or None
            except EOFError:
                return None
        try:
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                if self.wake_word:
                    print(f'[listening] Say "{self.wake_word}" first, then your request...')
                else:
                    print("[listening]...")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=12)
        except Exception as exc:
            print("[voice] Microphone error:", exc)
            return None

        try:
            import speech_recognition as sr

            text = self.recognizer.recognize_google(audio, language=self.language)
        except sr.UnknownValueError:
            return None
        except sr.RequestError as exc:
            print("[voice] Speech recognition error:", exc)
            return None

        if not text or not text.strip():
            return None
        text = text.strip()
        print("[you]", text)
        if self.wake_word and self.wake_word not in text.lower():
            return None
        return text