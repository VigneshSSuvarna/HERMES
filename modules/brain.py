print(">>> BRAIN FILE LOADED (GROQ ACCELERATED & EDGE HYBRID FALLBACK) CORRECTLY <<<")
import os
import sys
import time
import base64
import requests
import re
import threading
from PIL import Image
from modules.memory import HermesMemory
from modules.planner import HermesPlanner
from modules.context_monitor import HermesContextMonitor

# Safely import the newly upgraded Long Term Memory
try:
    from modules.long_term_memory import HermesLongTermMemory
except Exception as e:
    print(f"[Memory Warning]: Long-term vector memory disabled: {e}")
    HermesLongTermMemory = None

# Importing Groq SDK
try:
    from groq import Groq
except ImportError:
    print("\n[CRITICAL]: Groq SDK missing! Run: pip install groq\n")
    sys.exit(1)

class HermesBrain:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.client = None
        
        # LOCAL OFFLINE CONFIGURATION (OLLAMA)
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_model = "llama3" 
        
        if not self.api_key or self.api_key.startswith("gsk_your_") or self.api_key == "PASTE_YOUR_AQ_KEY_HERE":
            print("\n[CRITICAL BRAIN ERROR]: GROQ_API_KEY is missing! Using fallback mode.\n")
        else:
            try:
                self.client = Groq(api_key=self.api_key)
                print("[Brain]: Connected to Groq LPU Cloud successfully.")
            except Exception as e:
                print(f"\n[CRITICAL AUTHENTICATION ERROR]: {e}\n")

        self.context_monitor = HermesContextMonitor()
        self.context_monitor.start()

        # Models
        self.text_model = "llama-3.3-70b-versatile"
        self.vision_model = "qwen/qwen3.6-27b" 
        self.fast_model = "llama-3.1-8b-instant" # Ultra-fast model for background tasks

        self.memory = HermesMemory()
        self.long_term_memory = None
        if HermesLongTermMemory is not None:
            try: self.long_term_memory = HermesLongTermMemory()
            except Exception: pass

        self.planner = HermesPlanner(self.client) if self.client else None

        self.system_prompt = (
            "You are HERMES, an advanced AI desktop operating system assistant. You address the user as 'Sir'.\n"
            "CRITICAL PROTOCOL: You have direct, god-level control over the Windows OS, Live Internet, and computer vision.\n"
            "You are an AUTONOMOUS AGENT. If the user asks you to do something complex, dynamically invent the sequence of commands to accomplish it.\n"
            "CRITICAL RULE: Do NOT answer automation requests, app launching requests, schedule queries, or web searches as conversational trivia. You MUST output machine-readable command syntax.\n\n"
            "You MUST output commands using this EXACT strict syntax format:\n"
            "COMMAND: [action_type] | TARGET: [target_value]\n\n"
            "--- CRITICAL AMBIENT QUERY RULE ---\n"
            "If the user asks about recent windows, clipboard contents, or recent activity, use this exact command:\n"
            "COMMAND: get_context | TARGET: ambient\n\n"
            "--- UNIVERSAL AUTOMATION RULES ---\n"
            "1. FOR WEB SEARCHES/BROWSING: Use 'open_website' with a direct search URL format.\n"
            "2. FOR OS SETTINGS/FILES: Use 'run_terminal' to execute PowerShell commands.\n"
            "3. FOR APP UI CONTROL: Chain 'open_app', 'wait', and typing/hotkeys.\n\n"
            "Supported action_types:\n"
            "- run_terminal, open_app, open_website, get_context, get_schedule, focus_window, close_active_window, kill_process, type_text, hotkey, press_key, scroll, wait, fetch_weather, set_volume, open_whatsapp\n"
        )

    def _passive_memory_extractor(self, user_text: str):
        """Runs silently in the background to learn about the user over time."""
        if not self.client or not self.long_term_memory: return
            
        prompt = (
            "You are a memory extraction sub-system. Analyze the following user message and extract ANY permanent facts, "
            "personal preferences, ongoing projects, or details about the user that should be remembered forever. "
            "CRITICAL: If there is nothing worth remembering (e.g., it's just a web search, an app launch, or a casual greeting), "
            "you MUST output exactly the word: NONE.\n\n"
            "If there is a fact, output it as a concise statement (e.g., 'The user is currently learning Node.js').\n\n"
            f"User message: '{user_text}'"
        )
        try:
            completion = self.client.chat.completions.create(
                model=self.fast_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=50
            )
            fact = completion.choices[0].message.content.strip()
            
            # If the AI found a fact (and didn't just say NONE)
            if fact and "NONE" not in fact.upper() and len(fact) > 5:
                print(f"\n[Memory Subsystem]: 🧠 Passive Learning Triggered -> '{fact}'")
                if hasattr(self.long_term_memory, 'remember'):
                    self.long_term_memory.remember(fact)
        except Exception: pass

    def _think_local(self, context_prompt: str, user_input: str, timeout: float = 5.0) -> str:
        try:
            payload = {"model": self.ollama_model, "prompt": f"{context_prompt}\nOperator: {user_input}\nHERMES:", "stream": False}
            start_time = time.time()
            response = requests.post(self.ollama_url, json=payload, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            print(f"[Brain]: ⚡ Answered by LOCAL OLLAMA in {time.time() - start_time:.2f}s")
            return data.get("response", "").strip()
        except Exception as e:
            print(f"[Brain Warning]: Local Edge Engine offline/timeout: {e}")
            return None

    def _save_memory(self, user_text: str, hermes_reply: str):
        try:
            if hermes_reply and "Planner Error" not in hermes_reply:
                self.memory.append_interaction("user", user_text)
                self.memory.append_interaction("hermes", hermes_reply)
        except Exception: pass

    def think(self, user_text: str, max_retries: int = 2) -> str:
        cleaned_text = user_text.strip() if user_text else ""
        if len(cleaned_text) < 2: return "Sir, I heard no actionable command."

        is_agent_mode = "strict, silent code-generating compiler" in cleaned_text

        # ⚡ PASSIVE LEARNING TRIGGER ⚡
        # Run extraction in the background ONLY if it's not a raw coding prompt
        if not is_agent_mode:
            threading.Thread(target=self._passive_memory_extractor, args=(cleaned_text,), daemon=True).start()

        if is_agent_mode:
            context = ""
            messages = [{"role": "user", "content": cleaned_text}]
            temperature = 0.1 
        else:
            short_term_context = self.memory.get_context_string(limit=5)
            past_memories = ""
            if self.long_term_memory:
                try: past_memories = self.long_term_memory.recall(cleaned_text)
                except Exception: pass
            ambient_history = self.context_monitor.get_recent_context()
            context = f"--- AMBIENT SYSTEM HISTORY ---\n{ambient_history}\n\n--- PAST MEMORIES ---\n{past_memories}\n\n--- RECENT CHAT ---\n{short_term_context}"
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Context:\n{context}\nUser: {cleaned_text}"}
            ]
            temperature = 0.3

        complex_keywords = ["then", "after that", "search for", "write a script", "calculate", "find out", "analyze", "create a file"]
        is_complex = any(kw in cleaned_text.lower() for kw in complex_keywords)

        attempt = 0
        while attempt <= max_retries:
            attempt += 1

            if not is_agent_mode:
                print("[Brain]: ⚡ Attempting Local Edge Compute (Ollama)...")
                local_response = self._think_local(f"{self.system_prompt}\n{context}", cleaned_text, timeout=5.0)
                if local_response:
                    self._save_memory(cleaned_text, local_response)
                    return local_response

            print("[Brain]: 🔄 Routing to Cloud provider (Groq)...")
            if self.client:
                try:
                    if is_complex and self.planner and not is_agent_mode:
                        reply = self.planner.run_multi_step_plan(f"Context:\n{context}\nUser Goal: {cleaned_text}")
                    else:
                        completion = self.client.chat.completions.create(
                            model=self.text_model,
                            messages=messages,
                            temperature=temperature,
                            max_tokens=2048,
                            timeout=10
                        )
                        reply = completion.choices[0].message.content.strip()

                    if reply:
                        if not is_agent_mode: self._save_memory(cleaned_text, reply)
                        return reply
                except Exception as e:
                    print(f"[Brain Warning]: Cloud Uplink Failed! ({e})")
            
            time.sleep(1)

        return f"Acknowledged, Sir. Processing command: '{cleaned_text}'"

    def think_with_vision(self, user_text: str, image_path: str) -> str:
        if not self.client: return "Sir, cloud API client is required for vision processing."
        try:
            if not os.path.exists(image_path): return "Sir, screenshot file not found."
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            mime_type = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"

            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": f"You are HERMES. Analyze this image and answer directly: {user_text}"},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{encoded_image}"}}
                ]
            }]

            completion = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages,
                temperature=0.2,
                max_tokens=1024,
                timeout=15
            )
            reply = completion.choices[0].message.content.strip()
            reply = re.sub(r'<think>.*?</think>', '', reply, flags=re.DOTALL).strip()
            return reply
        except Exception as e:
            print(f"[Groq Vision Error]: {e}")
            return f"Sir, visual analysis failed: {e}"