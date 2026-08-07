print(">>> BRAIN FILE LOADED (GROQ ACCELERATED) CORRECTLY <<<")
import os
import sys
import time
import base64
from PIL import Image
from modules.memory import HermesMemory
from modules.planner import HermesPlanner

# Try to import HermesLongTermMemory with safety catch for PyTorch DLL issues
try:
    from modules.long_term_memory import HermesLongTermMemory
except Exception as e:
    print(f"[Memory Warning]: Long-term vector memory disabled due to dependency error: {e}")
    HermesLongTermMemory = None

# 🚀 Importing the Groq SDK for blazing-fast sub-second responses
try:
    from groq import Groq
except ImportError:
    print("\n[CRITICAL]: Groq SDK missing! Run: pip install groq\n")
    sys.exit(1)

class HermesBrain:
    def __init__(self):
        # API Key initialization (prioritizing GROQ_API_KEY environment variable)
        self.api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.client = None
        
        if not self.api_key or self.api_key.startswith("gsk_your_") or self.api_key == "PASTE_YOUR_AQ_KEY_HERE":
            print("\n[CRITICAL BRAIN ERROR]: GROQ_API_KEY is missing or invalid in environment variables! Using fallback mode.\n")
        else:
            try:
                self.client = Groq(api_key=self.api_key)
                print("[Brain]: Connected to Groq LPU Cloud successfully (Sub-second response active).")
            except Exception as e:
                print(f"\n[CRITICAL AUTHENTICATION ERROR]: {e}\n")

        # Lightning-fast Groq models (Updated active vision model: qwen/qwen3.6-27b)
        self.text_model = "llama-3.3-70b-versatile"
        self.vision_model = "qwen/qwen3.6-27b"

        # 📚 Initialize Memory Subsystems safely
        self.memory = HermesMemory()
        self.long_term_memory = None
        if HermesLongTermMemory is not None:
            try:
                self.long_term_memory = HermesLongTermMemory()
            except Exception as mem_err:
                print(f"[Memory Warning]: Long-term memory initialized with fallback mode: {mem_err}")

        # 🧠 Initialize Autonomous Planner Sub-system
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
            "- minimize_all, volume_up, volume_down, mute, media_play_pause\n"
            "- open_whatsapp (Example: COMMAND: open_whatsapp | TARGET: Vignesh)\n"
            "You are HERMES, an advanced AI desktop operating system assistant. You address the user as 'Sir'.\n"
            "CRITICAL PROTOCOL: You have direct, god-level control over the Windows OS and Live Internet.\n"
            "You are an AUTONOMOUS AGENT. If the user asks you to do something complex or compound (e.g. open YouTube and search for something), you must use efficient execution paths.\n\n"
            "--- UNIVERSAL AUTOMATION RULES ---\n"
            "1. FOR WEB SEARCHES/YOUTUBE: Prefer using 'open_website' with a direct search URL format (e.g., https://www.youtube.com/results?search_query=python+tutorials) to execute searches instantly without GUI tabbing errors.\n"
            "2. IF ALREADY ON YOUTUBE: To focus the search bar, use shortcut key '/' instead of tabbing (Sequence: hotkey | TARGET: /, wait | TARGET: 0.5, type_text | TARGET: query, press_key | TARGET: enter).\n"
            "3. FOR OS SETTINGS/FILES: Use 'run_terminal' to execute PowerShell commands.\n\n"
            "You MUST output commands using this EXACT strict syntax format:\n"
            "COMMAND: [action_type] | TARGET: [target_value]"
            "--- UNIVERSAL AUTOMATION RULES ---\n"
            "1. FOR WEB SEARCHES/BROWSING: Use 'open_website' with a direct search URL format.\n"
            "2. FOR OS SETTINGS/FILES: Use 'run_terminal' to execute PowerShell commands.\n"
            "3. FOR SYSTEM CLEANUP & REPAIR: You MUST use 'run_terminal | TARGET: cleanmgr /sagerun:1' to clean the disk. NEVER use 'Clean-Manager'. Use 'sfc /scannow' for system file checks.\n"
            "4. FOR APP UI CONTROL: Chain 'open_app', 'wait', and typing/hotkeys to navigate GUIs.\n\n"
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
        
        # 2. 🧠 RECALL: Search Long-Term Memory if available
        past_memories = ""
        if self.long_term_memory:
            try:
                past_memories = self.long_term_memory.recall(cleaned_text)
            except Exception:
                pass
        
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
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Context:\n{context}\nUser: {cleaned_text}"}
                ]
                
                completion = self.client.chat.completions.create(
                    model=self.text_model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1024
                )
                reply = completion.choices[0].message.content.strip()

            # 🛡️ ANTI-POISONING SAFEGUARD & MEMORY STORAGE
            try:
                if reply and "Planner Error" not in reply:
                    self.memory.append_interaction("user", cleaned_text)
                    self.memory.append_interaction("hermes", reply)
                    
                    if self.long_term_memory:
                        if len(cleaned_text) > 15: 
                            self.long_term_memory.remember(f"User asked/stated: {cleaned_text}")
                        if len(reply) > 20 and "COMMAND:" not in reply:
                            self.long_term_memory.remember(f"HERMES responded: {reply}")
            except Exception:
                pass

            return reply

        except Exception as e:
            print(f"[Groq Brain Execution Error]: {e}")
            return self._fallback_think(cleaned_text)

    def think_with_vision(self, user_text: str, image_path: str) -> str:
        if not self.client:
            return "Sir, cloud API client is required for vision processing."
        try:
            if not os.path.exists(image_path):
                return "Sir, screenshot file not found."
            
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

            mime_type = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": f"You are HERMES, an advanced AI operating system assistant addressing the user as 'Sir'. Analyze this image and answer: {user_text}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ]

            completion = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages,
                temperature=0.2,
                max_tokens=1024
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Groq Vision Error]: {e}")
            return f"Sir, visual analysis failed: {e}"