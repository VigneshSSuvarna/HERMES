import os
import time
import asyncio
import edge_tts
import pygame
import threading
import pyttsx3
import socket

class HermesVoice:
    def __init__(self, voice_model="en-GB-RyanNeural"):
        """
        Initializes the Hybrid Neural TTS Engine.
        Default Voice: 'en-GB-RyanNeural' (Male British J.A.R.V.I.S style)
        """
        print("[Voice]: Initializing Hybrid Speech Synthesizer...")
        self.voice_model = voice_model
        
        # CRITICAL: State tracking for microphone feedback and interruptions
        self.is_speaking = False
        self.stop_event = threading.Event()

        # 1. Initialize Pygame Audio Mixer (For Neural TTS)
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"[Voice Warning]: Pygame mixer init failed: {e}")

        # 2. Initialize Offline Pyttsx3 (Fallback)
        try:
            self.offline_engine = pyttsx3.init()
            self.offline_engine.setProperty('rate', 190) # Fast pacing
            
            # Try to pick a clear English voice if available
            voices = self.offline_engine.getProperty('voices')
            for voice in voices:
                if "Zira" in voice.name or "David" in voice.name or "English" in voice.name:
                    self.offline_engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"[Voice Warning]: Offline Pyttsx3 failed to initialize: {e}")
            self.offline_engine = None

    def _check_internet(self) -> bool:
        """Pings Cloudflare DNS to quickly check if we are online."""
        try:
            socket.create_connection(("1.1.1.1", 53), timeout=1.5)
            return True
        except OSError:
            return False

    async def _create_audio_file(self, text: str, output_path: str):
        """Streams audio directly from Edge Neural TTS to a unique target path."""
        communicate = edge_tts.Communicate(text, self.voice_model)
        await communicate.save(output_path)

    def _speak_online(self, text: str):
        """Handles high-quality Neural playback with interruption support."""
        unique_suffix = int(time.time() * 1000)
        target_file = f"hermes_response_{unique_suffix}.mp3"
        
        try:
            # Generate MP3 file asynchronously via Edge TTS
            asyncio.run(self._create_audio_file(text, target_file))
            time.sleep(0.05) # Buffer to ensure hard drive finished writing

            if os.path.exists(target_file) and not self.stop_event.is_set():
                pygame.mixer.music.load(target_file)
                pygame.mixer.music.play()

                # Block this thread until audio finishes OR an interrupt is triggered
                while pygame.mixer.music.get_busy():
                    if self.stop_event.is_set():
                        pygame.mixer.music.stop()
                        break
                    pygame.time.Clock().tick(10)

                pygame.mixer.music.unload()
                time.sleep(0.05) # Allow mixer to fully release file handle
                
        except Exception as e:
            print(f"\n[Voice Error]: Neural TTS failed ({e}). Rerouting to Offline Fallback...")
            self._speak_offline(text)
        finally:
            # Clean up temporary audio file safely
            try:
                if os.path.exists(target_file):
                    os.remove(target_file)
            except Exception:
                pass # Ignore if locked, will be overwritten/ignored later

    def _speak_offline(self, text: str):
        """Uses local Windows voice drivers if internet is down."""
        if not self.offline_engine or self.stop_event.is_set():
            return
        try:
            self.offline_engine.say(text)
            self.offline_engine.runAndWait()
        except Exception as e:
            print(f"[Voice Error]: Offline TTS failed completely: {e}")

    def speak(self, text: str):
        """Sparks speech in a background thread, prioritizing Cloud Neural TTS."""
        if not text or not text.strip():
            return

        # Instantly cut off any previous speech before starting a new one
        self.stop() 
        self.stop_event.clear()
        self.is_speaking = True

        # Clean text for TTS (remove emojis, complex markdown, code blocks)
        clean_text = text.replace("*", "").replace("#", "").replace("`", "").strip()
        
        # Don't read raw system commands aloud
        if "COMMAND:" in clean_text:
            clean_text = "Executing command, Sir."

        def _speech_thread():
            try:
                if self._check_internet():
                    self._speak_online(clean_text)
                else:
                    print("[Voice]: Connection severed. Engaging offline synthesizer.")
                    self._speak_offline(clean_text)
            finally:
                # Ensure the system knows speech has concluded
                self.is_speaking = False

        # Launch the speech logic without freezing the main application loop
        threading.Thread(target=_speech_thread, daemon=True).start()

    def stop(self):
        """Instantly interrupts any currently playing speech."""
        if self.is_speaking:
            self.stop_event.set()
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

if __name__ == "__main__":
    # Quick Local Test
    hermes_voice = HermesVoice()
    
    # Test 1: Normal Speech
    hermes_voice.speak("Good day, Sir. All neural speech matrices are online and operating at maximum fidelity.")
    time.sleep(5)
    
    # Test 2: Interruption Test
    hermes_voice.speak("I am about to say a very long sentence, but you are going to cut me off before I can finish it.")
    time.sleep(2)
    hermes_voice.stop() # Cuts him off instantly
    print("Speech interrupted successfully.")