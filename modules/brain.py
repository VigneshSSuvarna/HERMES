print(">>> BRAIN FILE LOADED (GROQ ACCELERATED & CALENDAR SYNCED) CORRECTLY <<<")
import os
import sys
import time
import base64
from PIL import Image
from modules.memory import HermesMemory
from modules.planner import HermesPlanner
from modules.context_monitor import HermesContextMonitor

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

        # 🌐 Initialize Ambient Context Monitor
        self.context_monitor = HermesContextMonitor()
        self.context_monitor.start()

        # Lightning-fast Groq models
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

        # UNIFIED CLEAN SYSTEM PROMPT
        self.system_prompt = (
            "You are HERMES, an advanced AI desktop operating system assistant. You address the user as 'Sir'.\n"
            "CRITICAL PROTOCOL: You have direct, god-level control over the Windows OS, Live Internet, and Google Calendar.\n"
            "You are an AUTONOMOUS AGENT. If the user asks you to do something complex or compound, dynamically invent the sequence of commands to accomplish it.\n"
            "CRITICAL RULE: Do NOT answer automation requests, app launching requests, schedule queries, or web searches as conversational trivia. You MUST output machine-readable command syntax.\n\n"
            "You MUST output commands using this EXACT strict syntax format:\n"
            "COMMAND: [action_type] | TARGET: [target_value]\n\n"
            "--- CRITICAL AMBIENT QUERY RULE ---\n"
            "If the user asks about recent windows, active apps, clipboard contents, or what they looked at recently, you MUST use this exact command format and NOTHING ELSE:\n"
            "COMMAND: get_context | TARGET: ambient\n\n"
            "--- CRITICAL SCHEDULE & CALENDAR RULE ---\n"
            "If the user asks about their schedule, calendar, meetings, or upcoming events, you MUST use this exact command format and NOTHING ELSE:\n"
            "COMMAND: get_schedule | TARGET: upcoming\n\n"
            "--- UNIVERSAL AUTOMATION RULES ---\n"
            "1. FOR WEB SEARCHES/BROWSING: Use 'open_website' with a direct search URL format (e.g., https://www.google.com/search?q=python+tutorials).\n"
            "2. FOR OS SETTINGS/FILES: Use 'run_terminal' to execute PowerShell commands.\n"
            "3. FOR APP UI CONTROL: Chain 'open_app', 'wait' (2-3 seconds), and typing/hotkeys to navigate GUIs.\n\n"
            "Supported action_types:\n"
            "- run_terminal (Example: COMMAND: run_terminal | TARGET: Get-Process)\n"
            "- open_app (Example: COMMAND: open_app | TARGET: chrome)\n"
            "- open_website (Example: COMMAND: open_website | TARGET: https://www.google.com)\n"
            "- get_context (Example: COMMAND: get_context | TARGET: ambient)\n"
            "- get_schedule (Example: COMMAND: get_schedule | TARGET: upcoming)\n"
            "- focus_window, close_active_window, kill_process, type_text, hotkey, press_key, scroll, wait, fetch_weather, fetch_info, set_volume, open_whatsapp\n"
            "--- UNIVERSAL AUTOMATION RULES ---\n"
        "1. FOR WEB SEARCHES: Use 'open_website' with a direct URL (e.g., https://www.google.com/search?q=python).\n"
        "2. DO NOT attempt to use 'ctrl+s' to save web pages or 'alt+f4' to close browsers for search requests. Keep web tasks to direct navigation.\n"   
        )

    def _fallback_think(self, text: str) -> str:
        cmd = text.lower().strip()

        if any(k in cmd for k in ["recent window", "clipboard", "looked at", "ambient", "history"]):
            return "COMMAND: get_context | TARGET: ambient\n\nRetrieving recent ambient activity, Sir."

        if any(k in cmd for k in ["schedule", "calendar", "meetings", "upcoming events"]):
            return "COMMAND: get_schedule | TARGET: upcoming\n\nAccessing your Google Calendar, Sir."

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

        return f"Acknowledged, Sir. Processing command: '{text}'"

    def think(self, user_text: str) -> str:
        cleaned_text = user_text.strip() if user_text else ""
        if len(cleaned_text) < 2:
            return "Sir, I heard no actionable command."

        if not self.client:
            return self._fallback_think(cleaned_text)

        short_term_context = self.memory.get_context_string(limit=5)
        
        past_memories = ""
        if self.long_term_memory:
            try:
                past_memories = self.long_term_memory.recall(cleaned_text)
            except Exception:
                pass

        ambient_history = self.context_monitor.get_recent_context()
        context = f"--- AMBIENT SYSTEM HISTORY ---\n{ambient_history}\n\n--- PAST MEMORIES ---\n{past_memories}\n\n--- RECENT CHAT ---\n{short_term_context}"
        
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

            try:
                if reply and "Planner Error" not in reply:
                    self.memory.append_interaction("user", cleaned_text)
                    self.memory.append_interaction("hermes", reply)
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
                        {"type": "text", "text": f"You are HERMES, an advanced AI operating system assistant addressing the user as 'Sir'. Analyze this image and answer: {user_text}"},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{encoded_image}"}}
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