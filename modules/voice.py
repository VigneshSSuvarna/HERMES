import os
import time
import asyncio
import edge_tts
import pygame
import threading
import pyttsx3
class HermesVoice:
    def __init__(self):
        self.engine = pyttsx3.init()
        # Optimize speech rate for speed
        self.engine.setProperty('rate', 190)

    def speak(self, text: str):
        """Sparks speech in a background thread to prevent freezing the main system loop."""
        def _talk():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                pass
        
        speech_thread = threading.Thread(target=_talk, daemon=True)
        speech_thread.start()

class HermesVoice:
    def __init__(self, voice_model="en-GB-RyanNeural"):
        """
        Initializes the Neural TTS Engine.
        Default Voice: 'en-GB-RyanNeural' (Male British J.A.R.V.I.S style)
        Other options: 'en-GB-ThomasNeural', 'en-US-ChristopherNeural'
        """
        self.voice_model = voice_model
        self.temp_audio_file = "hermes_response.mp3"
        
        # CRITICAL: Tracks speech state to prevent microphone feedback loops
        self.is_speaking = False

        # Initialize Pygame Audio Mixer
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"[Voice Warning]: Pygame mixer init failed: {e}")

    def speak(self, text: str):
        """
        Generates and plays realistic neural audio for the given text.
        """
        if not text or not text.strip():
            return

        # Strip markdown symbols so speech remains natural
        clean_text = text.replace("*", "").replace("#", "").replace("`", "").strip()

        self.is_speaking = True

        try:
            # 1. Handle file locking gracefully by generating a unique timestamped filename if needed
            unique_suffix = int(time.time() * 1000)
            target_file = f"hermes_response_{unique_suffix}.mp3"

            # 2. Generate MP3 file asynchronously via Edge TTS
            asyncio.run(self._create_audio_file(clean_text, target_file))

            # 3. Brief buffer to ensure the hard drive finished writing
            time.sleep(0.05)

            # 4. Play audio via Pygame Mixer
            if os.path.exists(target_file):
                pygame.mixer.music.load(target_file)
                pygame.mixer.music.play()

                # Block until audio finishes playing
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

                pygame.mixer.music.unload()
                time.sleep(0.05) # Allow mixer to fully release file handle

                # Clean up temporary audio file safely
                try:
                    if os.path.exists(target_file):
                        os.remove(target_file)
                except Exception:
                    pass # Ignore if locked, will be cleaned up later

        except Exception as e:
            print(f"[Voice Error]: Neural TTS playback failed: {e}")
        finally:
            # Ensure lock releases even if an exception occurs
            self.is_speaking = False

    async def _create_audio_file(self, text: str, output_path: str):
        """Streams audio directly from Edge Neural TTS to a unique target path."""
        communicate = edge_tts.Communicate(text, self.voice_model)
        await communicate.save(output_path)


if __name__ == "__main__":
    # Test Voice Engine
    hermes_voice = HermesVoice()
    hermes_voice.speak("Good day, Sir. All neural speech matrices are online and operating at maximum fidelity.")