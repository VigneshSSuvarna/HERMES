import os
import sys
import json
import pyaudio
from vosk import Model, KaldiRecognizer

class HermesEars:
    def __init__(self):
        model_path = "model"
        if not os.path.exists(model_path):
            print(f"\n[Sensory Error]: Language matrix folder '{model_path}' not found!")
            sys.exit(1)
            
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        
        # Force Vosk to recognize partial/incomplete words immediately for responsiveness
        self.recognizer.SetWords(True)
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4000  # Optimized buffer matching chunk read size
        )
        self.stream.start_stream()

    def listen(self):
        # Read matching chunk sizes to avoid hardware stream sync loss
        data = self.stream.read(4000, exception_on_overflow=False)
        if len(data) == 0:
            return None
            
        if self.recognizer.AcceptWaveform(data):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                return text
        else:
            # Fallback: Capture words even if there wasn't a long structural pause
            partial = json.loads(self.recognizer.PartialResult())
            partial_text = partial.get("partial", "").strip()
            # If a long phrase is built up but hasn't finalized, return it to clear backlog
            if len(partial_text.split()) > 3:
                self.recognizer.Reset()
                return partial_text
                
        return None