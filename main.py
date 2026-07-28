import os
import sys
import time
import subprocess
import webbrowser
import requests

from modules.ears import HermesEars
from modules.brain import HermesBrain
from modules.automation import HermesHands
from modules.voice import HermesVoice
from modules.eyes import HermesEyes


def get_current_location():
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5).json()
        city = res.get("city", "Unknown City")
        region = res.get("region", "Unknown Region")
        country = res.get("country", "Unknown Country")
        return f"You are currently located near {city}, {region}, {country}."
    except Exception:
        return "I was unable to determine your current location, Sir."


def process_command(command_text, brain, hands, voice, eyes):
    command_lower = command_text.lower().strip()
    print(f"\n[Executing Command]: '{command_lower}'")

    # 1. System Shutdown
    if any(w in command_lower for w in ["shutdown", "exit", "stop hermes", "bye"]):
        voice.speak("Disconnecting terminal matrices. Goodbye, Sir.")
        print("[System]: Shutting down...")
        os._exit(0)

    # 2. Launch Applications
    elif "notepad" in command_lower:
        print("[Action]: Opening Notepad...")
        voice.speak("Opening Notepad, Sir.")
        try:
            subprocess.Popen(["notepad.exe"])
            print("[Success]: Notepad process started.")
        except Exception as e:
            print(f"[Error launching Notepad]: {e}")

    elif "calculator" in command_lower or "calc" in command_lower:
        print("[Action]: Opening Calculator...")
        voice.speak("Opening Calculator, Sir.")
        subprocess.Popen(["calc.exe"])

    # 3. Launch Websites
    elif "youtube" in command_lower:
        print("[Action]: Opening YouTube...")
        voice.speak("Opening YouTube, Sir.")
        webbrowser.open("https://www.youtube.com")

    elif "google" in command_lower:
        print("[Action]: Opening Google...")
        voice.speak("Opening Google, Sir.")
        webbrowser.open("https://www.google.com")

    # 4. Location Query
    elif any(phrase in command_lower for phrase in ["location", "where am i"]):
        loc_info = get_current_location()
        print(f"[HERMES]: {loc_info}")
        voice.speak(loc_info)

    # 5. Screen Snapshot (Vision)
    elif any(phrase in command_lower for phrase in ["screen", "monitor"]):
        voice.speak("Capturing desktop snapshot, Sir.")
        vision_summary = eyes.see_screen("Summarize what is open on my monitor in detail.")
        print(f"\n[HERMES Vision Analysis]:\n{vision_summary}\n")
        voice.speak(vision_summary)

    # 6. Webcam Snapshot (Vision)
    elif any(phrase in command_lower for phrase in ["webcam", "camera"]):
        voice.speak("Accessing optical camera feed, Sir.")
        vision_summary = eyes.see_webcam("Describe what you see in front of the camera in detail.")
        print(f"\n[HERMES Camera Analysis]:\n{vision_summary}\n")
        voice.speak(vision_summary)

    # 7. Conversational AI Brain Reasoning
    else:
        raw_response = brain.think(command_lower)
        print(f"[HERMES]: {raw_response}")
        voice.speak(raw_response)


def main():
    print("==============================================")
    print("   HERMES HYBRID VOICE & TEXT CONTROL CENTER  ")
    print("==============================================\n")

    print("[System]: Initializing core modules...")
    ears = HermesEars()
    brain = HermesBrain()
    hands = HermesHands()
    voice = HermesVoice()
    eyes = HermesEyes()

    voice.speak("Voice perception matrices online, Sir.")
    print("\n[System]: Listening for voice commands in background...")

    while True:
        try:
            # 1. Check for incoming spoken commands from background thread
            voice_cmd = ears.get_command()
            if voice_cmd:
                process_command(voice_cmd, brain, hands, voice, eyes)

            time.sleep(0.1) # Prevents CPU usage spike

        except KeyboardInterrupt:
            print("\nShutting down HERMES, Sir.")
            break
        except Exception as e:
            print(f"[Loop Error]: {e}")


if __name__ == "__main__":
    main()