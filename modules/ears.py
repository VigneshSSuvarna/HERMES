import sys
import time
import threading
import queue

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False


class HermesEars:
    def __init__(self):
        if not HAS_SR:
            print("[Ears Error]: SpeechRecognition is not installed. Run 'pip install SpeechRecognition pyaudio'")
            sys.exit(1)

        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        self.speech_queue = queue.Queue()
        self.is_listening = True

        # Start microphone listener in a dedicated background thread
        self.listener_thread = threading.Thread(target=self._background_listener, daemon=True)
        self.listener_thread.start()
        print("[Sensory]: Background Threaded Voice Receiver Active.")

    def _background_listener(self):
        """Continuously listens to microphone in background without freezing main loop."""
        with sr.Microphone() as source:
            # Calibrate for ambient noise once
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            except Exception:
                pass

            while self.is_listening:
                try:
                    # Listen for phrase (timeout prevents blocking indefinitely)
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=7)
                    text = self.recognizer.recognize_google(audio)
                    text = text.lower().strip()
                    
                    if text:
                        print(f"\n[Voice Captured]: {text}")
                        self.speech_queue.put(text)
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    time.sleep(0.5)

    def get_command(self) -> str:
        """Non-blocking fetch of recognized voice commands."""
        try:
            return self.speech_queue.get_nowait()
        except queue.Empty:
            return ""