import time
import subprocess
import pyautogui
from .base_connector import HermesConnector

class GUIConnector(HermesConnector):
    def get_supported_actions(self):
        # ⚡ Added type_text to supported actions
        return ["type_notepad", "type_text"]

    def execute(self, action_type: str, target: str) -> str:
        try:
            if action_type == "type_notepad":
                # Hardcoded Notepad macro
                subprocess.Popen(["notepad.exe"])
                time.sleep(2) 
                pyautogui.write(target, interval=0.02)
                return f"Successfully opened Notepad and typed: {target}"
                
            elif action_type == "type_text":
                # ⚡ Universal typing macro (types into whatever window is currently active)
                time.sleep(0.5) # Brief pause to ensure the previous app (like Notepad) is fully focused
                pyautogui.write(target, interval=0.02)
                return f"Successfully typed the requested text."
                
        except Exception as e:
            return f"GUI Automation Error: {str(e)}"