import logging
import os

class HermesSafetyCore:
    def __init__(self):
        # 1. Audit Logging (Saves every action to a file)
        logging.basicConfig(filename='hermes_audit.log', level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        
        # 2. Authorization Matrix
        self.allow_list = [
            "open_app", "open_website", "get_weather", "read_clipboard", 
            "web_search", "scrape_url", "type_notepad", "type_text", 
            "wait", "parse_query", "get_context", "ambient", "context", "write_excel"
        ]
        self.require_confirm = [
            "run_terminal", "delete_file", "send_email", "write_file"
        ]
        
        self.require_confirm = ["run_terminal", "delete_file", "send_email", "write_file"]

    def validate_action(self, action_type: str, target: str) -> bool:
        """Validates if an action can be executed autonomously."""
        logging.info(f"REQUESTED ACTION: {action_type} | TARGET: {target}")
        
        if action_type in self.allow_list:
            return True
            
        if action_type in self.require_confirm:
            print(f"\n[⚠️ SAFETY LOCK ENGAGED]")
            print(f"Hermes is attempting a restricted action: {action_type.upper()}")
            print(f"Target/Payload: {target}")
            
            while True:
                user_auth = input("Authorize this action? (Y/N): ").strip().lower()
                if user_auth in ['y', 'yes']:
                    logging.info(f"ACTION AUTHORIZED by user: {action_type}")
                    return True
                elif user_auth in ['n', 'no']:
                    logging.warning(f"ACTION BLOCKED by user: {action_type}")
                    return False
        
        logging.error(f"UNKNOWN ACTION REJECTED: {action_type}")
        print(f"[Safety Error]: Action '{action_type}' is not registered in the safety matrix.")
        return False