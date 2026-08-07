import sys
import os
import time
import glob
import threading
import ctypes

# -------------------------------------------------------------
# 🛡️ GOD-MODE OVERRIDE (AUTO-ADMINISTRATOR)
# -------------------------------------------------------------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# If not running as admin, relaunch the script with elevated privileges
if not is_admin():
    print("[Security]: Requesting Administrator Privileges for Deep System Control...")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join([f'"{sys.argv[0]}"'] + sys.argv[1:]), None, 1)
    sys.exit()

# Include root folder in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QStyle
from modules.daemon import HermesDaemon
from ui.dashboard import HermesDashboard
from modules.brain import HermesBrain
from modules.ears import HermesEars
from modules.voice import HermesVoice
from modules.automation import HermesHands
from modules.eyes import HermesEyes
from modules.internet import HermesInternet


def process_command(cmd: str, app: HermesDashboard, brain: HermesBrain, hands: HermesHands, voice: HermesVoice, eyes: HermesEyes, internet: HermesInternet):
    # Strip whitespace and wrapping quotes to prevent artifact bugs
    cmd_clean = cmd.strip('"\' ')
    if not cmd_clean:
        return

    # 🚀 WAKE-WORD & FILLER STRIPPER: Strip leading conversational prefixes
    cmd_lower_raw = cmd_clean.lower()
    for filler in ["hermes,", "hermes", "jarvis,", "jarvis", "please"]:
        if cmd_lower_raw.startswith(filler):
            cmd_clean = cmd_clean[len(filler):].strip()
            break

    cmd_clean = cmd_clean.strip('"\' ,')
    if not cmd_clean:
        return

    response = ""

    # Visual State: PROCESSING
    app.set_voice_state("PROCESSING", f"PROCESSING: '{cmd_clean.upper()}'")
    app.log(f"[OPERATOR COMMAND]: {cmd_clean}")
    
    # -------------------------------------------------------------
    # ⚡ FAST-TRACK LOCAL OVERRIDES (Zero-Latency OS Controls)
    # -------------------------------------------------------------
    cmd_lower = cmd_clean.lower()
    
    # 1. Fast-Track: Opening Apps (Bypassed if it's a compound search command)
    if cmd_lower.startswith("open ") or cmd_lower.startswith("launch "):
        target = cmd_lower.replace("open ", "").replace("launch ", "").strip()
        
        # If it's a compound search command, let the Cloud Brain handle the macro chain!
        if "and search" in target or "search for" in target or " and " in target:
            pass  
        else:
            app.log(f"[Fast-Track]: Launching {target}")
            exec_result = hands.execute_action("open_app", target)
            print(f"[TRACE]: Fast-Track Hands -> {exec_result}")
            voice.speak(f"Opening {target}, Sir.")
            app.set_voice_state("LISTENING", "DIRECT LISTENING ACTIVE...")
            return
    
    # Fast-Track: Dynamic Volume Control (Extracts ANY number dynamically)
    if "volume" in cmd_lower:
        import re
        numbers = re.findall(r'\d+', cmd_lower)
        if numbers:
            target_vol = numbers[0]  # Captures whatever number you said
            app.log(f"[Fast-Track]: Setting volume to {target_vol}%")
            exec_result = hands.execute_action("set_volume", target_vol)
            print(f"[TRACE]: Fast-Track Hands -> {exec_result}")
            voice.speak(f"Volume set to {target_vol} percent, Sir.")
        elif any(k in cmd_lower for k in ["up", "increase", "louder"]):
            hands.execute_action("volume_up", "")
            voice.speak("Increasing volume, Sir.")
        elif any(k in cmd_lower for k in ["down", "decrease", "quieter"]):
            hands.execute_action("volume_down", "")
            voice.speak("Decreasing volume, Sir.")
        elif "mute" in cmd_lower:
            hands.execute_action("mute", "")
            voice.speak("Toggling audio mute, Sir.")
            
        app.set_voice_state("LISTENING", "DIRECT LISTENING ACTIVE...")
        return
    
    # 2. Fast-Track: Closing Apps & Windows
    if cmd_lower.startswith("close ") or cmd_lower.startswith("kill "):
        target = cmd_lower.replace("close ", "").replace("kill ", "").replace(" the ", "").strip()
        
        if target in ["window", "this", "app", "application", "it"]:
            app.log(f"[Fast-Track]: Closing active window")
            exec_result = hands.execute_action("close_active_window", "")
        else:
            app.log(f"[Fast-Track]: Terminating {target}")
            exec_result = hands.execute_action("kill_process", target)
            
        print(f"[TRACE]: Fast-Track Hands -> {exec_result}")
        voice.speak("Task executed, Sir.")
        app.set_voice_state("LISTENING", "DIRECT LISTENING ACTIVE...")
        return

    # 3. Fast-Track: Window Resizing
    if cmd_lower.startswith("maximize"):
        hands.execute_action("maximize_window", "")
        voice.speak("Maximized, Sir.")
        app.set_voice_state("LISTENING", "DIRECT LISTENING ACTIVE...")
        return
        
    if cmd_lower.startswith("minimize"):
        hands.execute_action("minimize_window", "")
        voice.speak("Minimized, Sir.")
        app.set_voice_state("LISTENING", "DIRECT LISTENING ACTIVE...")
        return

    # -------------------------------------------------------------
    # SYSTEM & UI OVERRIDES
    # -------------------------------------------------------------
    if any(k in cmd_clean.lower() for k in ["shutdown system", "exit hermes", "quit hermes"]):
        voice.speak("Shutting down systems. Goodbye, Sir.")
        if hasattr(app, 'vision_box'):
            app.vision_box.stop_feed()
        QApplication.quit()
        sys.exit(0)

    if any(k in cmd_clean.lower() for k in ["hide hud", "hide interface", "minimize to tray"]):
        app.hide()
        voice.speak("Minimizing interface to system tray, Sir. I am still listening.")
        app.set_voice_state("LISTENING", "DIRECT LISTENING ACTIVE...")
        return

    if any(k in cmd_clean.lower() for k in ["show hud", "open interface", "bring up dashboard"]):
        app.showFullScreen()
        voice.speak("Restoring visual interface, Sir.")
        app.set_voice_state("LISTENING", "DIRECT LISTENING ACTIVE...")
        return

    # -------------------------------------------------------------
    # VISION & LOCAL IMAGE READING OVERRIDES
    # -------------------------------------------------------------
    cmd_lower_vision = cmd_clean.lower().replace('"', '').replace("'", "")
    
    # Expanded vision triggers
    vision_triggers = [
        "look at my screen", 
        "analyze screen", 
        "what is on my screen", 
        "what is there on my screen",
        "what do you see", 
        "see my screen",
        "whats on my screen",
        "what's on my screen"
    ]
    
    if any(k in cmd_lower_vision for k in vision_triggers):
        app.log("[Eyes]: Capturing screen for neural vision analysis...")
        print("\n--- TRACE: VISION SCREEN CAPTURE TRIGGERED ---")
        screen_file = eyes.capture_screen()
        
        if screen_file and os.path.exists(screen_file):
            print(f"[TRACE]: Screenshot captured to '{screen_file}'. Handing to Brain...")
            response = brain.think_with_vision("Analyze what is currently visible on my screen and summarize it for me.", screen_file)
            eyes.cleanup()
        else:
            response = "Sir, screen capture failed."
        
        app.log(f"[HERMES]: {response}")
        app.set_voice_state("SPEAKING", "TRANSMITTING NEURAL SPEECH...")
        voice.speak(response)
        app.set_voice_state("LISTENING", "DIRECT LISTENING ACTIVE...")
        return

    # Local Image File Reader
    if cmd_lower_vision.startswith("read ") or cmd_lower_vision.startswith("analyze image ") or cmd_lower_vision.startswith("look at image "):
        target_name = cmd_lower_vision.replace("read ", "").replace("analyze image ", "").replace("look at image ", "").strip()
        app.log(f"[Eyes]: Searching local storage for image matching '{target_name}'...")
        
        possible_files = glob.glob(f"*{target_name.replace(' ', '_')}*") + glob.glob(f"*{target_name}*")
        image_file = None
        for f in possible_files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
                image_file = f
                break
                
        if not image_file and "test" in target_name:
            for default_name in ["test.png", "test.jpg", "test_image.png", "test_image.jpg"]:
                if os.path.exists(default_name):
                    image_file = default_name
                    break
                    
        if image_file and os.path.exists(image_file):
            app.log(f"[TRACE]: Found image file '{image_file}'. Handing to Vision AI...")
            response = brain.think_with_vision(f"Read and extract all text or describe what is visible in this image file: {target_name}", image_file)
        else:
            response = f"Sir, I could not find an image file matching '{target_name}' in the working directory."
            
        app.log(f"[HERMES]: {response}")
        app.set_voice_state("SPEAKING", "TRANSMITTING NEURAL SPEECH...")
        voice.speak(response)
        app.set_voice_state("LISTENING", "DIRECT LISTENING ACTIVE...")
        return

    # -------------------------------------------------------------
    # GENERAL AI BRAIN INGESTION
    # -------------------------------------------------------------
    if not response:
        response = brain.think(cmd_clean)

    # -------------------------------------------------------------
    # COMMAND PARSER & EXECUTION (WITH CONCISE REPLY FILTERING)
    # -------------------------------------------------------------
    clean_reply = response
    
    print(f"\n--- TRACE: RAW BRAIN OUTPUT ---\n{response}\n-------------------------------")

    if "COMMAND:" in response:
        try:
            action_types_executed = []
            for line in response.split("\n"):
                if "COMMAND:" in line:
                    print(f"[TRACE]: Parsing line -> {line.strip()}")
                    parts = line.split("COMMAND:")[1].split("|")
                    action_type = parts[0].strip()
                    target_val = ""
                    if len(parts) > 1 and "TARGET:" in parts[1]:
                        target_val = parts[1].split("TARGET:")[1].strip()

                    action_types_executed.append(action_type)
                    app.log(f"[Dispatch]: Action='{action_type}', Target='{target_val}'")
                    print(f"[TRACE]: Successfully Dispatched -> Action: '{action_type}', Target: '{target_val}'")
                    
                    if action_type == "fetch_weather":
                        exec_result = internet.fetch_weather(target_val)
                        app.log(f"[Internet]: {exec_result}")
                        clean_reply = exec_result
                    elif action_type == "fetch_info":
                        exec_result = internet.fetch_wiki(target_val)
                        app.log(f"[Internet]: {exec_result}")
                        clean_reply = exec_result
                    else:
                        print(f"[TRACE]: Handing off to automation.py...")
                        exec_result = hands.execute_action(action_type, target_val)
                        print(f"[TRACE]: Hands returned -> {exec_result}")
                        app.log(f"[Hands Output]: {exec_result}")

            # ⚡ CONCISE SPEECH FILTER: Prevent long technical readouts
            if not any(k in response for k in ["fetch_weather", "fetch_info"]):
                if "open_website" in action_types_executed:
                    clean_reply = "Opening page, Sir."
                elif "type_text" in action_types_executed:
                    clean_reply = "Searching, Sir."
                elif "close_active_window" in action_types_executed or "kill_process" in action_types_executed:
                    clean_reply = "Task executed, Sir."
                else:
                    lines = [l.strip() for l in response.split("\n") if not l.startswith("COMMAND:") and l.strip()]
                    if lines and len(lines[0]) < 60:
                        clean_reply = lines[0]
                    else:
                        clean_reply = "Done, Sir."

        except Exception as e:
            print(f"[TRACE ERROR]: Command parsing failed: {e}")
            app.log(f"[Main Error]: Command parsing failed: {e}")

    app.log(f"[HERMES]: {clean_reply}")
    app.set_voice_state("SPEAKING", "TRANSMITTING NEURAL SPEECH...")
    voice.speak(clean_reply)
    app.set_voice_state("LISTENING", "DIRECT LISTENING ACTIVE...")


def background_voice_loop(app, ears, brain, hands, voice, eyes, internet):
    """Listens continuously for direct voice commands."""
    last_speech_time = 0
    while True:
        try:
            if getattr(voice, 'is_speaking', False):
                time.sleep(0.2)
                last_speech_time = time.time()
                continue
            
            if time.time() - last_speech_time < 3.5:
                time.sleep(0.1)
                continue

            app.set_voice_state("LISTENING", "DIRECT LISTENING ACTIVE...")
            voice_cmd = ears.get_command()
            
            if voice_cmd and len(voice_cmd.strip().split()) >= 1:
                clean_cmd = voice_cmd.strip().lower()
                
                echo_phrases = ["acknowledged", "processing command", "sir", "neural speech", "acknowledged sir", "hermes", "at your service"]
                if any(phrase in clean_cmd for phrase in echo_phrases) and len(clean_cmd.split()) <= 4:
                    time.sleep(0.1)
                    continue

                app.log(f"[Voice Captured]: {voice_cmd}")
                process_command(voice_cmd, app, brain, hands, voice, eyes, internet)
            
            time.sleep(0.1)
        except Exception as e:
            app.log(f"[Voice Loop Error]: {e}")
            time.sleep(0.5)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    brain = HermesBrain()
    daemon = HermesDaemon()
    daemon.start()
    
    ears = HermesEars()
    voice = HermesVoice()
    hands = HermesHands()
    eyes = HermesEyes()
    internet = HermesInternet()

    def handle_gui_command(cmd_text):
        threading.Thread(
            target=process_command,
            args=(cmd_text, gui, brain, hands, voice, eyes, internet),
            daemon=True
        ).start()

    gui = HermesDashboard(command_callback=handle_gui_command)

    # -------------------------------------------------------------
    # SYSTEM TRAY DAEMON
    # -------------------------------------------------------------
    tray_icon = QSystemTrayIcon(app.style().standardIcon(QStyle.SP_ComputerIcon), app)
    tray_icon.setToolTip("HERMES AI Operating System")
    
    tray_menu = QMenu()
    show_action = QAction("Show Dashboard", app)
    show_action.triggered.connect(gui.showFullScreen)
    hide_action = QAction("Hide Dashboard", app)
    hide_action.triggered.connect(gui.hide)
    quit_action = QAction("Shutdown HERMES", app)
    quit_action.triggered.connect(lambda: sys.exit(0))
    
    tray_menu.addAction(show_action)
    tray_menu.addAction(hide_action)
    tray_menu.addSeparator()
    tray_menu.addAction(quit_action)
    
    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()

    voice_thread = threading.Thread(
        target=background_voice_loop,
        args=(gui, ears, brain, hands, voice, eyes, internet),
        daemon=True
    )
    voice_thread.start()

    gui.log("[HERMES]: Systems online. Administrator privileges granted.")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()