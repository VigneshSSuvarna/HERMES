import sys
import os
import time
import threading
from PyQt5.QtWidgets import QApplication

# Include root folder in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.dashboard import HermesDashboard
from modules.brain import HermesBrain
from modules.ears import HermesEars
from modules.voice import HermesVoice
from modules.automation import HermesHands
from modules.eyes import HermesEyes


def process_command(cmd: str, app: HermesDashboard, brain: HermesBrain, hands: HermesHands, voice: HermesVoice, eyes: HermesEyes):
    cmd_clean = cmd.strip()
    if not cmd_clean:
        return

    # Visual State: PROCESSING
    app.set_voice_state("PROCESSING", f"PROCESSING: '{cmd_clean.upper()}'")
    app.log(f"[OPERATOR COMMAND]: {cmd_clean}")

    # Exit Overrides
    if any(k in cmd_clean.lower() for k in ["shutdown system", "exit hermes", "quit hermes"]):
        voice.speak("Shutting down systems. Goodbye, Sir.")
        if hasattr(app, 'vision_box'):
            app.vision_box.stop_feed()
        QApplication.quit()
        sys.exit(0)

    # Screen Vision Analysis
    if any(k in cmd_clean.lower() for k in ["analyze screen", "look at my screen"]):
        app.log("[Eyes]: Capturing screen for neural vision analysis...")
        screen_file = eyes.capture_screen()
        if screen_file:
            response = brain.think("Please analyze what is currently visible on my screen.")
            eyes.cleanup()
        else:
            response = "Sir, screen capture failed."
    else:
        # Get response from Brain
        response = brain.think(cmd_clean)

    # -------------------------------------------------------------
    # COMMAND PARSER & EXECUTION
    # -------------------------------------------------------------
    clean_reply = response

    if "COMMAND:" in response:
        try:
            # Extract line containing COMMAND:
            for line in response.split("\n"):
                if "COMMAND:" in line:
                    # Syntax: COMMAND: action_type | TARGET: target_value
                    parts = line.split("COMMAND:")[1].split("|")
                    action_type = parts[0].strip()
                    target_val = ""
                    if len(parts) > 1 and "TARGET:" in parts[1]:
                        target_val = parts[1].split("TARGET:")[1].strip()

                    app.log(f"[Hands Dispatch]: Action='{action_type}', Target='{target_val}'")
                    
                    # Execute automation on system
                    exec_result = hands.execute_action(action_type, target_val)
                    app.log(f"[Hands Output]: {exec_result}")

            # Strip COMMAND line out of spoken audio response
            lines = [l for l in response.split("\n") if not l.startswith("COMMAND:")]
            clean_reply = "\n".join(lines).strip()
            if not clean_reply:
                clean_reply = "Task executed, Sir."

        except Exception as e:
            app.log(f"[Main Error]: Command parsing failed: {e}")

    # Visual State & Speech Output: SPEAKING
    app.log(f"[HERMES]: {clean_reply}")
    app.set_voice_state("SPEAKING", "TRANSMITTING NEURAL SPEECH...")
    voice.speak(clean_reply)

    # Reset State to Listening
    app.set_voice_state("LISTENING", "DIRECT LISTENING ACTIVE...")


def background_voice_loop(app, ears, brain, hands, voice, eyes):
    """Listens continuously for direct voice commands with noise filtering."""
    while True:
        try:
            app.set_voice_state("LISTENING", "DIRECT LISTENING ACTIVE...")
            
            # Direct voice command capture
            voice_cmd = ears.get_command()
            
            # Require at least 2 words or 3+ characters to avoid static noise triggers
            if voice_cmd and len(voice_cmd.strip().split()) >= 1:
                app.log(f"[Voice Captured]: {voice_cmd}")
                process_command(voice_cmd, app, brain, hands, voice, eyes)

            time.sleep(1.0)
        except Exception as e:
            app.log(f"[Voice Loop Error]: {e}")
            time.sleep(2.0)


def main():
    app = QApplication(sys.argv)

    # Core Module Initializations
    brain = HermesBrain()
    ears = HermesEars()
    voice = HermesVoice()
    hands = HermesHands()
    eyes = HermesEyes()

    # Create HUD Dashboard with Command Handler
    def handle_gui_command(cmd_text):
        threading.Thread(
            target=process_command,
            args=(cmd_text, gui, brain, hands, voice, eyes),
            daemon=True
        ).start()

    gui = HermesDashboard(command_callback=handle_gui_command)

    # Launch Voice Listener Thread
    voice_thread = threading.Thread(
        target=background_voice_loop,
        args=(gui, ears, brain, hands, voice, eyes),
        daemon=True
    )
    voice_thread.start()

    gui.log("[HERMES]: Systems online. Direct OS automation bridge active.")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()