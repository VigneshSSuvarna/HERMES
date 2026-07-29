import os
import asyncio
import edge_tts
import pygame


class HermesVoice:
    def __init__(self, voice_model="en-GB-RyanNeural"):
        """
        Initializes the Neural TTS Engine.
        Default Voice: 'en-GB-RyanNeural' (Male British J.A.R.V.I.S style)
        Other options: 'en-GB-ThomasNeural', 'en-US-ChristopherNeural'
        """
        self.voice_model = voice_model
        self.temp_audio_file = "hermes_response.mp3"

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

        try:
            # Generate MP3 file asynchronously
            asyncio.run(self._create_audio_file(clean_text))

            # Play audio via Pygame Mixer
            if os.path.exists(self.temp_audio_file):
                pygame.mixer.music.load(self.temp_audio_file)
                pygame.mixer.music.play()

                # Block until audio finishes playing
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

                pygame.mixer.music.unload()

                # Clean up temporary audio file
                if os.path.exists(self.temp_audio_file):
                    os.remove(self.temp_audio_file)

        except Exception as e:
            print(f"[Voice Error]: Neural TTS playback failed: {e}")

    async def _create_audio_file(self, text: str):
        """Streams audio directly from Edge Neural TTS."""
        communicate = edge_tts.Communicate(text, self.voice_model)
        await communicate.save(self.temp_audio_file)


if __name__ == "__main__":
    # Test Voice Engine
    hermes_voice = HermesVoice()
    hermes_voice.speak("Good day, Sir. All neural speech matrices are online and operating at maximum fidelity.")