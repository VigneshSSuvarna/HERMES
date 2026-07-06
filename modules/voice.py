import sys
import pyttsx3

class HermesVoice:
    def __init__(self):
        try:
            # Initialize the local Windows SAPI5 driver subsystem
            self.engine = pyttsx3.init('sapi5')
            
            # Configure a crisp, rapid verbal delivery rate (standard is 200)
            self.engine.setProperty('rate', 195)
            
            # Adjust target audio output volume (0.0 to 1.0)
            self.engine.setProperty('volume', 1.0)
            
            # Extract available system voices installed on your Windows machine
            self.voices = self.engine.getProperty('voices')
            
            # Set the engine to a professional masculine or deep assistant index profile
            # Voice indices: 0 is typically Microsoft David (Male), 1 is Microsoft Zira (Female)
            if len(self.voices) > 0:
                self.engine.setProperty('voice', self.voices[0].id)
                
        except Exception as e:
            print(f"[Voice Subsystem Error]: Failed to bind audio drivers. Details: {e}")
            sys.exit(1)

    def speak(self, text):
        """Translates plain text strings into real-time audio streams through the speakers."""
        if not text:
            return
            
        print(f"🔊 [HERMES Speaking]: {text}")
        try:
            # Stage the text chunk into the audio queue
            self.engine.say(text)
            # Flush the queue and physically generate the speaker frequencies
            self.engine.runAndWait()
        except Exception as e:
            print(f"[Vocal Output Failure]: Audio loop interrupted. Details: {e}")

if __name__ == "__main__":
    # Diagnostic audio validation check
    vocal_unit = HermesVoice()
    print("\n==============================================")
    print("[Testing Voice Array]: Initiating Speaker Sync...")
    print("==============================================\n")
    
    # Run text conversion check
    vocal_unit.speak("Audio matrix synchronized. I am online and fully functional, Sir.")