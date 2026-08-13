import os
import subprocess
import time
from .base_connector import HermesConnector

class SystemConnector(HermesConnector):
    def get_supported_actions(self):
        return ["open_app", "open_website", "run_terminal", "delete_file", "wait"]

    def execute(self, action_type: str, target: str) -> str:
        try:
            if action_type == "open_website":
                os.system(f"start {target}")
                return f"Successfully opened website: {target}"
                
            elif action_type == "run_terminal":
                result = subprocess.run(["powershell", "-Command", target], 
                                        capture_output=True, text=True, timeout=15)
                return result.stdout.strip()
                
            elif action_type == "delete_file":
                os.remove(target)
                return f"File {target} successfully deleted."
                
            elif action_type == "open_app":
                os.system(f"start {target}")
                return f"Opened application: {target}"
                
            elif action_type == "wait":
                wait_time = int(target) if target.isdigit() else 2
                time.sleep(wait_time)
                return f"Waited for {wait_time} seconds."
                
        except Exception as e:
            raise RuntimeError(f"SystemConnector Error: {str(e)}")