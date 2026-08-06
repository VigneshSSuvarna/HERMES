print(">>> BRAIN FILE LOADED CORRECTLY <<<")
import os
import sys
import time
from PIL import Image
from modules.memory import HermesMemory
from modules.planner import HermesPlanner
from modules.long_term_memory import HermesLongTermMemory

# 🚀 Importing the modern Google GenAI SDK
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("\n[CRITICAL]: SDK missing! Run: pip install google-genai\n")
    sys.exit(1)

class HermesBrain:
    def __init__(self):
        # API Key initialization
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.client = None
        
        if not self.api_key or self.api_key == "PASTE_YOUR_AQ_KEY_HERE":
            print("\n[CRITICAL BRAIN ERROR]: API Key is empty! Cloud AI disabled.\n")
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print("[Brain]: Connected to Gemini Cloud AI successfully.")
            except Exception as e:
                print(f"\n[CRITICAL AUTHENTICATION ERROR]: {e}\n")

        # ⚡ STREAMLINED: Fast working models to eliminate lag & waterfall delay
        self.models_to_try = [
            "gemini-2.0-flash",
            "gemini-flash-latest"
        ]

        # 📚 Initialize Memory Subsystems
        self.memory = HermesMemory()
        self.long_term_memory = HermesLongTermMemory()
        
        # 🧠 FIXED: Initialize Autonomous Planner Sub-system WITHOUT 'model_name'
        self.planner = HermesPlanner(self.client) if self.client else None

        # UNIFIED SYSTEM PROMPT
        self.system_prompt = (
            "You are HERMES, an advanced AI desktop operating system assistant. You address the user as 'Sir'.\n"
            "CRITICAL PROTOCOL: You have direct, god-level control over the Windows OS and Live Internet.\n"
            "You are an AUTONOMOUS AGENT. If the user asks you to do something complex or compound (e.g. open an app and search for something online), you must dynamically INVENT the sequence of commands to accomplish it.\n"
            "CRITICAL RULE: Do NOT answer automation requests, app launching requests, or web searches as conversational trivia or text definitions. You MUST output machine-readable command syntax.\n\n"
            "You MUST output commands using this EXACT strict syntax format:\n"
            "COMMAND: [action_type] | TARGET: [target_value]\n\n"
            "--- UNIVERSAL AUTOMATION RULES ---\n"
            "1. FOR WEB SEARCHES/BROWSING: Use 'open_website' with a direct search URL format (e.g., https://www.google.com/search?q=python+tutorials) to execute searches instantly.\n"
            "2. FOR OS SETTINGS/FILES: Use 'run_terminal' to execute PowerShell commands (e.g., empty recycle bin, turn off wifi, create folders).\n"
            "3. FOR APP UI CONTROL: Chain 'open_app', 'wait' (2-3 seconds), and typing/hotkeys to navigate GUIs like a human operator.\n\n"
            "Supported action_types:\n"
            "- run_terminal (Example: COMMAND: run_terminal | TARGET: Clear-RecycleBin -Force)\n"
            "- open_app (Example: COMMAND: open_app | TARGET: chrome)\n"
            "- open_website (Example: COMMAND: open_website | TARGET: https://www.google.com/search?q=python+tutorials)\n"
            "- focus_window (Example: COMMAND: focus_window | TARGET: chrome)\n"
            "- close_active_window (Example: COMMAND: close_active_window | TARGET: )\n"
            "- kill_process (Example: COMMAND: kill_process | TARGET: spotify)\n"
            "- type_text (Example: COMMAND: type_text | TARGET: python tutorials)\n"
            "- hotkey (Example: COMMAND: hotkey | TARGET: ctrl+t)\n"
            "- press_key (Example: COMMAND: press_key | TARGET: enter)\n"
            "- scroll (Example: COMMAND: scroll | TARGET: -500)\n"
            "- wait (Example: COMMAND: wait | TARGET: 2.0)\n"
            "- fetch_weather (Example: COMMAND: fetch_weather | TARGET: london)\n"
            "- fetch_info (Example: COMMAND: fetch_info | TARGET: quantum physics)\n"
            "- set_volume (Example: COMMAND: set_volume | TARGET: 50)\n"
            "- minimize_all, volume_up, volume_down, mute, media_play_pause"
            "- open_whatsapp (Example: COMMAND: open_whatsapp | TARGET: Vignesh)\n"
        )

    def _fallback_think(self, text: str) -> str:
        cmd = text.lower().strip()

        if "search for" in cmd or "search" in cmd:
            query = cmd.replace("open chrome and search for", "").replace("search for", "").replace("search", "").strip()
            formatted_query = query.replace(" ", "+")
            return f"COMMAND: open_website | TARGET: https://www.google.com/search?q={formatted_query}\n\nSearching for {query}, Sir."

        if any(cmd.startswith(prefix) for prefix in ["open ", "launch ", "start ", "run "]):
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

        elif any(cmd.startswith(prefix) for prefix in ["close ", "kill ", "terminate ", "shut "]):
            for prefix in ["close ", "kill ", "terminate ", "shut "]:
                if cmd.startswith(prefix):
                    target = cmd.replace(prefix, "").replace("down", "").strip()
                    break
            if target in ["window", "this", "current window", "app", "application"]:
                return "COMMAND: close_active_window | TARGET: \n\nClosing the active window, Sir."
            return f"COMMAND: kill_process | TARGET: {target}\n\nTerminating {target}, Sir."

        elif any(k in cmd for k in ["maximize", "minimize", "restore", "focus", "switch to"]):
            action = ""
            if "maximize" in cmd: action = "maximize_window"
            elif "minimize" in cmd: action = "minimize_window"
            elif "restore" in cmd: action = "restore_window"
            elif "focus" in cmd or "switch to" in cmd: action = "focus_window"
            
            target = cmd.replace("maximize", "").replace("minimize", "").replace("restore", "").replace("focus", "").replace("switch to", "").replace("window", "").replace("the", "").replace("this", "").strip()
            if target:
                return f"COMMAND: {action} | TARGET: {target}\n\nAdjusting {target} window layout, Sir."
            return f"COMMAND: {action} | TARGET: \n\nAdjusting your current window, Sir."

        return f"Acknowledged, Sir. Processing command: '{text}'"

    def think(self, user_text: str) -> str:
        cleaned_text = user_text.strip() if user_text else ""
        if len(cleaned_text) < 2:
            return "Sir, I heard no actionable command."

        if not self.client:
            return self._fallback_think(cleaned_text)

        # 1. Get Short-Term Context
        short_term_context = self.memory.get_context_string(limit=5)
        
        # 2. 🧠 RECALL: Search Long-Term Memory for relevant past information
        past_memories = self.long_term_memory.recall(cleaned_text)
        
        # 3. Combine contexts seamlessly for the Brain
        context = f"--- PAST LONG-TERM MEMORIES ---\n{past_memories}\n\n--- RECENT CHAT HISTORY ---\n{short_term_context}"
        
        # 🧠 Complex trigger check for Autonomous Multi-Step Planner delegation
        complex_keywords = ["then", "after that", "search for", "write a script", "calculate", "find out", "analyze", "create a file"]
        is_complex = any(kw in cleaned_text.lower() for kw in complex_keywords)

        try:
            if is_complex and self.planner:
                print("[Brain]: Routing request to Autonomous Multi-Step Planner...")
                reply = self.planner.run_multi_step_plan(f"Context:\n{context}\nUser Goal: {cleaned_text}")
            else:
                full_prompt = f"{self.system_prompt}\n\nContext:\n{context}\nUser: {cleaned_text}\nHERMES:"
                reply = None
                for model_name in self.models_to_try:
                    for attempt in range(2):
                        try:
                            response = self.client.models.generate_content(
                                model=model_name,
                                contents=full_prompt,
                            )
                            if response and response.text:
                                reply = response.text.strip()
                                break
                        except Exception as e:
                            err_str = str(e)
                            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                                print(f"[Brain Quota Notice]: Rate limit hit on {model_name}. Pausing for 3s...")
                                time.sleep(3.0)
                            else:
                                break
                    if reply:
                        break

                if not reply:
                    reply = self._fallback_think(cleaned_text)

            # 🛡️ ANTI-POISONING SAFEGUARD & LONG TERM STORAGE
            try:
                if reply and "429" not in reply and "RESOURCE_EXHAUSTED" not in reply and "Planner Error" not in reply:
                    # Save to short-term memory
                    self.memory.append_interaction("user", cleaned_text)
                    self.memory.append_interaction("hermes", reply)
                    
                    # 💾 STORE: Save significant interactions to Long-Term Vector DB
                    # We filter out short commands to save database space for actual knowledge
                    if len(cleaned_text) > 15: 
                        self.long_term_memory.remember(f"User asked/stated: {cleaned_text}")
                    if len(reply) > 20 and "COMMAND:" not in reply:
                        self.long_term_memory.remember(f"HERMES responded: {reply}")
                else:
                    print("[Memory]: System error detected. Excluded from context memory to prevent quota loops.")
            except Exception:
                pass

            return reply

        except Exception as e:
            print(f"[Brain Execution Error]: {e}")
            return self._fallback_think(cleaned_text)

    def think_with_vision(self, user_text: str, image_path: str) -> str:
        if not self.client:
            return "Sir, cloud API client is required for vision processing."
        try:
            if not os.path.exists(image_path):
                return "Sir, screenshot file not found."
            
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            mime_type = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"

            prompt = (
                "You are HERMES, an advanced AI operating system assistant addressing the user as 'Sir'.\n"
                f"Analyze this image and answer: {user_text}"
            )

            for model_name in self.models_to_try:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=[
                            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                            prompt
                        ]
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        print(f"[Vision Quota Notice]: Rate limit hit on {model_name}. Pausing for 3s...")
                        time.sleep(3.0)
                    continue
            return "Sir, visual analysis is temporarily rate-limited or failed."
        except Exception as e:
            return f"[Eyes System Error]: {e}"