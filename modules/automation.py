import os
import subprocess
import webbrowser
import pyautogui
import time

class HermesHands:
    def __init__(self):
        # Move mouse to any corner of the screen to instantly abort script if it acts up
        pyautogui.FAILSAFE = True

    def execute_system_command(self, action_type, target):
        """Maps structured instructions directly into native Windows actions."""
        action_type = action_type.lower().strip()
        target_clean = target.strip()
        
        print(f"\n⚙️ [Execution Array]: Initiating macro '{action_type}' -> Target: {target_clean}")
        
        try:
            # 🚀 MACRO 1: Open Local Applications
            if action_type == "open_app":
                target_lower = target_clean.lower()
                if "notepad" in target_lower:
                    subprocess.Popen(["notepad.exe"])
                elif "calculator" in target_lower or "calc" in target_lower:
                    subprocess.Popen(["calc.exe"])
                elif "chrome" in target_lower:
                    # Tries standard installation paths for Google Chrome
                    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                    if os.path.exists(chrome_path):
                        subprocess.Popen([chrome_path])
                    else:
                        os.system("start chrome")
                else:
                    # Generic Windows shell launch fallback
                    os.system(f"start {target_clean}")
                return f"Successfully opened {target_clean}, Sir."

            # 🌐 MACRO 2: Intelligent Web Navigation & Google Searching
            elif action_type == "open_website":
                target_lower = target_clean.lower()
                # If it looks like a clean domain name, wrap it properly
                if target_lower.endswith((".com", ".org", ".net", ".in", ".edu")):
                    url = f"https://{target_clean}" if not target_clean.startswith("http") else target_clean
                    webbrowser.open(url)
                    return f"Navigating directly to {target_clean}, Sir."
                else:
                    # If it's a general request, convert it into an automated Google query search string
                    url = f"https://www.google.com/search?q={target_clean.replace(' ', '+')}"
                    webbrowser.open(url)
                    return f"Searching the web for '{target_clean}', Sir."

            # ⌨️ MACRO 3: Direct Core Text Injection (Typing Simulation)
            elif action_type == "type_text":
                # Brief sleep delay to allow a text box to gain target screen focus
                time.sleep(1.0)
                pyautogui.write(target_clean, interval=0.03)
                return "Text matrix successfully injected, Sir."

            # ❌ Unrecognized Action Fallback
            else:
                return f"[Execution Error]: Core instruction pattern '{action_type}' is unmapped."
                
        except Exception as e:
            return f"[Execution Failure]: Physical link dropped. Details: {e}"

if __name__ == "__main__":
    # Diagnostic multi-test verification script
    hands = HermesHands()
    print("\n[Diagnostic Test Run]: Running advanced website search routing logic...")
    res = hands.execute_system_command("open_website", "latest space x launch updates")
    print(f"Result: {res}\n")