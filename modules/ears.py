import speech_recognition as sr


class HermesEars:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Increase energy threshold (e.g., from 300 to 800) so it ignores quiet room noise
        self.recognizer.energy_threshold = 800 
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

        print("[Ears]: Direct Continuous Listening Active (Noise Filtered).")
    def __init__(self):
        """
        Initializes continuous direct voice capture without any wake word requirement.
        """
        self.recognizer = sr.Recognizer()
        
        # Micro-calibrated sensitivity for continuous ambient speech
        self.recognizer.energy_threshold = 1000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

        print("[Ears]: Direct Continuous Listening Active (Wake Word Disabled).")

    def listen_for_wakeword() -> bool:
        """Compatibility hook - returns True immediately as wake word is bypassed."""
        return True

    def get_command(self) -> str:
        """
        Captures spoken audio directly from the microphone.
        """
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
            try:
                # Listens directly for speech
                audio = self.recognizer.listen(source, timeout=4, phrase_time_limit=10)
                command = self.recognizer.recognize_google(audio)
                return command.strip()
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                return ""
            except Exception as e:
                print(f"[Ears Error]: Speech capture issue: {e}")
                return ""


if __name__ == "__main__":
    # Standalone Test
    ears = HermesEars()
    print("Speak directly into your mic (no wake word needed)...")
    cmd = ears.get_command()
    if cmd:
        print(f"[Captured Command]: '{cmd}'")
    else:
        print("No command captured.")