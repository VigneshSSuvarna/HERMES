import os
import sys
import json
import queue
import pyaudio
from vosk import Model, KaldiRecognizer

class HermesEars:
    def __init__(self, model_path="model"):
        if not os.path.exists(model_path):
            print(f"[Error]: Vosk model not found at '{model_path}'.")
            sys.exit(1)
            
        # Initialize upgraded high-accuracy translation arrays
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.audio_queue = queue.Queue()
        self.p = pyaudio.PyAudio()

    def audio_callback(self, in_data, frame_count, time_info, status):
        self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    def listen_for_wake_word(self, wake_word="wake up"):
        print(f"\n[Sensory]: Upgraded Microphone Array online. Listening for '{wake_word}'...")
        
        stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4000,
            stream_callback=self.audio_callback
        )
        stream.start_stream()

        try:
            while True:
                data = self.audio_queue.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").lower().strip()
                    
                    if text:
                        print(f"[Heard]: {text}")
                        if wake_word in text:
                            print(f"\n🎯 [Sensory]: Wake-word detected! Greetings, Sir.")
                            return True
        except KeyboardInterrupt:
            print("\n[Sensory]: Shutting down audio workers safely.")
        finally:
            stream.stop_stream()
            stream.close()
            self.p.terminate()

if __name__ == "__main__":
    ears = HermesEars()
    ears.listen_for_wake_word()