import os
import sys
import google.generativeai as genai
from modules.memory import HermesMemory

class HermesBrain:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("\n[Error]: GEMINI_API_KEY environment variable is missing!")
            sys.exit(1)
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.memory = HermesMemory()
        self.system_prompt = (
            "You are HERMES, a crisp and fiercely loyal enterprise desktop AI assistant. "
            "You address your creator as 'Sir'. "
            "CRITICAL PROTOCOL: If the user explicitly asks you to open a website, application, or perform a system task, "
            "you must prepend your command signature strictly using this exact syntax:\n"
            "COMMAND: [action_type] | TARGET: [target_value]\n\n"
            "Supported action_types:\n"
            "- open_app\n"
            "- open_website\n"
            "- type_text\n\n"
            "If it is a general conversational request, respond normally with crisp executive tone."
        )

    def think(self, user_text):
        try:
            # Query recent contextual interactions from the relational SQL database layer
            context = self.memory.get_context_string(limit=15)
            full_prompt = (
                f"{self.system_prompt}\n\n"
                f"Recent System Memory Matrix:\n{context}\n"
                f"User: {user_text}\nHERMES:"
            )
            response = self.model.generate_content(full_prompt)
            reply = response.text.strip()
            
            # Log the successful transaction safely to our chat_logs database table
            self.memory.append_interaction("user", user_text)
            self.memory.append_interaction("hermes", reply)
            
            return reply
        except Exception as e:
            return f"[Cognition Error]: Core intelligence matrix link disrupted. Details: {e}"