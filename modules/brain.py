print(">>> BRAIN FILE LOADED CORRECTLY <<<")
import os
import sys
import time
import datetime
from google import genai
from PIL import Image
from modules.memory import HermesMemory


class HermesBrain:
    def __init__(self):
        HARDCODED_KEY = ""  # Optional: Paste fresh Gemini API key here
        self.api_key = HARDCODED_KEY or os.getenv("GEMINI_API_KEY", "")
        self.client = None
        
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print("[Brain]: Connected to Gemini Cloud AI.")
            except Exception as e:
                print(f"[Brain Warning]: Cloud API setup skipped/failed: {e}")

        self.models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        self.memory = HermesMemory()

        self.system_prompt = (
            "You are HERMES, an advanced AI desktop operating system assistant. You address the user as 'Sir'.\n"
            "CRITICAL PROTOCOL: You have direct control over the Windows OS. You can CHAIN multiple actions together to perform complex tasks.\n"
            "Output multiple COMMAND lines in sequence.\n\n"
            "Supported action_types:\n"
            "- open_app (target: app name)\n"
            "- open_website (target: URL)\n"
            "- focus_window (target: window title)\n"
            "- type_text (target: text to type)\n"
            "- hotkey (target: e.g. ctrl+t, ctrl+l, alt+tab)\n"
            "- press_key (target: enter, tab, esc, space)\n"
            "- wait (target: seconds, e.g. 1.5. ALWAYS wait after opening an app before typing!)\n"
            "- fetch_weather (target: city name)\n"
            "- fetch_info (target: search topic)\n"
            "- close_window, minimize_all, volume_up, volume_down, mute, media_play_pause"
        )
        self.system_prompt = (
            "You are HERMES, an advanced AI desktop operating system assistant. You address the user as 'Sir'.\n"
            "CRITICAL PROTOCOL: You have direct control over the Windows OS. You can CHAIN multiple actions together to perform complex tasks.\n"
            "Output multiple COMMAND lines in sequence.\n\n"
            "Supported action_types:\n"
            "- open_app (target: app name)\n"
            "- open_website (target: URL)\n"
            "- focus_window (target: window title)\n"
            "- maximize_window (target: window title, or leave blank for current)\n"
            "- minimize_window (target: window title, or leave blank for current)\n"
            "- restore_window (target: window title, or leave blank for current)\n"
            "- close_active_window (target: window title, or leave blank for current)\n"
            "- kill_process (target: app name)\n"
            "- type_text (target: text to type)\n"
            "- hotkey (target: e.g. ctrl+t, ctrl+l, alt+tab)\n"
            "- press_key (target: enter, tab, esc, space)\n"
            "- wait (target: seconds, e.g. 1.5)\n"
            "- fetch_weather (target: city name)\n"
            "- fetch_info (target: search topic)\n"
            "- minimize_all, volume_up, volume_down, mute, media_play_pause"
        )

    def _fallback_think(self, text: str) -> str:
        """Autonomous Macro Planner: Converts complex natural language into multi-step OS operations."""
        cmd = text.lower().strip()

        if "youtube" in cmd and ("search" in cmd or "find" in cmd or "play" in cmd):
            query = cmd.replace("youtube", "").replace("search", "").replace("find", "").replace("play", "").replace("for", "").strip()
            return (
                "COMMAND: open_app | TARGET: chrome\n"
                "COMMAND: wait | TARGET: 1.5\n"
                "COMMAND: hotkey | TARGET: ctrl+l\n"
                "COMMAND: type_text | TARGET: https://www.youtube.com\n"
                "COMMAND: press_key | TARGET: enter\n"
                "COMMAND: wait | TARGET: 2.0\n"
                f"COMMAND: type_text | TARGET: {query}\n"
                "COMMAND: press_key | TARGET: enter\n\n"
                f"Executing macro search on YouTube for: '{query}', Sir."
            )

        elif "notepad" in cmd and ("write" in cmd or "type" in cmd or "note" in cmd):
            content = cmd.replace("notepad", "").replace("write", "").replace("type", "").replace("note", "").replace("down", "").strip()
            return (
                "COMMAND: open_app | TARGET: notepad\n"
                "COMMAND: wait | TARGET: 1.0\n"
                f"COMMAND: type_text | TARGET: {content}\n\n"
                "Noting down your text in Notepad, Sir."
            )

        elif any(cmd.startswith(prefix) for prefix in ["open ", "launch ", "start ", "run "]):
            for prefix in ["open ", "launch ", "start ", "run "]:
                if cmd.startswith(prefix):
                    target = cmd.replace(prefix, "").strip()
                    break

            if any(dom in target for dom in [".com", ".org", ".net", "youtube", "google", "github"]):
                return f"COMMAND: open_website | TARGET: {target}\n\nOpening website: {target}, Sir."
            return f"COMMAND: open_app | TARGET: {target}\n\nLaunching {target}, Sir."

        elif any(k in cmd for k in ["volume up", "increase volume", "louder"]):
            return "COMMAND: volume_up | TARGET: \n\nIncreasing volume, Sir."
        elif any(k in cmd for k in ["volume down", "decrease volume", "quieter"]):
            return "COMMAND: volume_down | TARGET: \n\nDecreasing volume, Sir."
        elif "mute" in cmd:
            return "COMMAND: mute | TARGET: \n\nToggling audio mute, Sir."
        elif any(k in cmd for k in ["pause", "play", "stop music"]):
            return "COMMAND: media_play_pause | TARGET: \n\nToggling media playback, Sir."

        elif "lock" in cmd and ("pc" in cmd or "computer" in cmd or "screen" in cmd):
            return "COMMAND: lock_pc | TARGET: \n\nLocking workstation, Sir."
       # 5. Workstation & Closing Commands
        elif any(cmd.startswith(prefix) for prefix in ["close ", "kill ", "terminate ", "shut "]):
            for prefix in ["close ", "kill ", "terminate ", "shut "]:
                if cmd.startswith(prefix):
                    target = cmd.replace(prefix, "").replace("down", "").strip()
                    break
            
            # If the user just says "close window" or "close this"
            if target in ["window", "this", "current window", "app", "application"]:
                return "COMMAND: close_active_window | TARGET: \n\nClosing the active window, Sir."
            
            # If the user names a specific app (e.g., "close whatsapp")
            return f"COMMAND: kill_process | TARGET: {target}\n\nTerminating {target}, Sir."

        elif "lock" in cmd and ("pc" in cmd or "computer" in cmd or "screen" in cmd):
            return "COMMAND: lock_pc | TARGET: \n\nLocking workstation, Sir."
        elif any(k in cmd for k in ["minimize", "show desktop"]):
            return "COMMAND: minimize_all | TARGET: \n\nShowing desktop view, Sir."

        elif any(k in cmd for k in ["hi", "hello", "hey", "good morning"]):
            return "Good day, Sir! All systems are operational and ready to execute your commands."
        elif "time" in cmd:
            now_str = datetime.datetime.now().strftime("%I:%M %p")
            return f"The time is {now_str}, Sir."
        elif "date" in cmd:
            date_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {date_str}, Sir."
        # Advanced Window Manipulation (Maximize, Minimize, Restore, Focus)
        elif any(k in cmd for k in ["maximize", "minimize", "restore", "focus", "switch to"]):
            action = ""
            if "maximize" in cmd: action = "maximize_window"
            elif "minimize" in cmd: action = "minimize_window"
            elif "restore" in cmd: action = "restore_window"
            elif "focus" in cmd or "switch to" in cmd: action = "focus_window"
            
            # Extract target (what app they want to control)
            target = cmd.replace("maximize", "").replace("minimize", "").replace("restore", "").replace("focus", "").replace("switch to", "").replace("window", "").replace("the", "").replace("this", "").strip()
            
            if target:
                return f"COMMAND: {action} | TARGET: {target}\n\nAdjusting {target} window layout, Sir."
            else:
                return f"COMMAND: {action} | TARGET: \n\nAdjusting your current window, Sir."

        return f"Acknowledged, Sir. Processing command: '{text}'"

    def think(self, user_text: str) -> str:
        cleaned_text = user_text.strip() if user_text else ""
        if len(cleaned_text) < 2:
            return "Sir, I heard no actionable command."

        if not self.client:
            return self._fallback_think(cleaned_text)

        context = self.memory.get_context_string(limit=5)
        full_prompt = f"{self.system_prompt}\n\nContext:\n{context}\nUser: {cleaned_text}\nHERMES:"

        reply = None
        for model_name in self.models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=full_prompt,
                )
                if response and response.text:
                    reply = response.text.strip()
                    break
            except Exception:
                time.sleep(0.2)
                continue

        if not reply:
            reply = self._fallback_think(cleaned_text)

        try:
            self.memory.append_interaction("user", cleaned_text)
            self.memory.append_interaction("hermes", reply)
        except Exception:
            pass

        return reply
    
    def think_with_vision(self, user_text: str, image_path: str) -> str:
        """Sends both text prompt and an image file to Gemini for multimodal analysis."""
        if not self.client:
            return "Sir, cloud API client is required for vision processing."

        try:
            # The PIL import is now securely at the top of this file
            image_file = Image.open(image_path)
            
            prompt = (
                f"You are HERMES, an advanced AI desktop operating system assistant addressing the user as 'Sir'.\n"
                f"Analyze the provided visual context from the user's screen/camera and answer: {user_text}"
            )

            for model_name in self.models_to_try:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=[prompt, image_file],
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception:
                    continue

            return "Sir, visual analysis failed across all neural endpoints."
        except Exception as e:
            return f"[Vision Error]: {e}"