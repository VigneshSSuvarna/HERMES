import os
import sys
import glob
import subprocess
import webbrowser
import pyautogui
import psutil
import time
import pygetwindow as gw

try:
    import screen_brightness_control as sbc
except ImportError:
    sbc = None


class WindowsUniversalLauncher:
    """Diagnostic-grade application launcher with optimized non-blocking window checks."""
    def __init__(self):
        user_profile = os.getenv("USERPROFILE", "C:\\Users\\Default")
        self.shortcut_dirs = [
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
            os.path.join(user_profile, r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs"),
            r"C:\Users\Public\Desktop",
            os.path.join(user_profile, "Desktop")
        ]
        self.app_cache = {}
        self.refresh_app_cache()
        
    def refresh_app_cache(self):
        self.app_cache.clear()
        for folder in self.shortcut_dirs:
            if os.path.exists(folder):
                for root, _, files in os.walk(folder):
                    for file in files:
                        if file.endswith((".lnk", ".url", ".exe")):
                            clean_name = file.rsplit(".", 1)[0].lower()
                            self.app_cache[clean_name] = os.path.join(root, file)
        print(f"[Launcher]: Cached {len(self.app_cache)} application shortcuts from system directories.")
        
    def click_text_on_screen(self, description: str) -> str:
        """Visually finds an element on the screen using AI vision coordinates and clicks it."""
        print(f"[Hands Vision]: Scanning screen for '{description}'...")
        
        screenshot_path = "temp_screen_scan.png"
        pyautogui.screenshot(screenshot_path)
        try:
            from modules.brain import HermesBrain
            brain = HermesBrain()
            
            prompt = (
                f"Look at this screenshot of my computer screen. "
                f"Find the exact center pixel coordinates (X, Y) of the button, icon, or text that matches: '{description}'. "
                f"Reply ONLY with the numbers in this exact format: X, Y. If you cannot find it, reply: NOT_FOUND"
            )
            
            response = brain.think_with_vision(prompt, screenshot_path)
            
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
                
            if "NOT_FOUND" in response or "," not in response:
                return f"Error: Could not visually locate '{description}' on the screen. Target not found."
                
            coords_str = response.strip().split()[0]
            x_str, y_str = coords_str.replace("(", "").replace(")", "").split(",")
            x, y = int(x_str.strip()), int(y_str.strip())
            
            pyautogui.moveTo(x, y, duration=0.5)
            pyautogui.click()
            
            return f"Successfully clicked on '{description}' at coordinates ({x}, {y})."
            
        except Exception as e:
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
            return f"Error: Visual click failed: {e}"

    def launch(self, app_name: str) -> bool:
        target = app_name.strip().lower()
        if not target:
            return False

        aliases = {
            "chrome": "chrome",
            "vscode": "code",
            "word": "winword",
            "excel": "excel",
            "notepad": "notepad",
            "whatsapp": "whatsapp:",
            "spotify": "spotify:",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "soundrecorder": "Sound Recorder:",
            "voice recorder": "Sound Recorder:",
            "netflix": "netflix:",
            "settings": "ms-settings:"
        }
        
        lookup_target = aliases.get(target, target)
        print(f"[Launcher]: Executing nuclear bypass for '{lookup_target}'...")

        # LAYER 1: Native Shell / URI Protocol Injection
        try:
            print(f"[Layer 1] Injecting '{lookup_target}' into Windows Core...")
            if lookup_target == "calc.exe":
                subprocess.Popen("calc.exe")
            elif ":" in lookup_target:
                subprocess.Popen(f'explorer.exe {lookup_target}', shell=True)
            else:
                subprocess.Popen(f'start {lookup_target}', shell=True)
                
            time.sleep(1.0)
            return True
        except Exception as e:
            print(f"[Layer 1] Core Injection Failed: {e}")

        # LAYER 2: PowerShell Stealth Execution
        try:
            print(f"[Layer 2] Injecting '{lookup_target}' into PowerShell...")
            subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "-Command", f"Start-Process '{lookup_target}'"])
            time.sleep(1.0)
            return True
        except Exception as e:
            print(f"[Layer 2] PowerShell Failed: {e}")

        # LAYER 3: Standard OS Startfile
        try:
            os.startfile(lookup_target)
            return True
        except Exception as e:
            print(f"[Layer 3] Startfile Failed: {e}")

        return False


class HermesHands:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05
        self.launcher = WindowsUniversalLauncher()
        print("[Hands]: Universal Windows Automation Engine Initialized.")

    def open_whatsapp_chat(self, contact_name: str) -> str:
        """Automates WhatsApp to search for a contact and open their chat."""
        try:
            print(f"[Hands]: Opening WhatsApp and searching for contact: '{contact_name}'...")
            whatsapp_windows = [w for w in gw.getWindowsWithTitle('WhatsApp') if w.title]
            
            if whatsapp_windows:
                w = whatsapp_windows[0]
                if w.isMinimized:
                    w.restore()
                w.activate()
                time.sleep(0.8)
            else:
                webbrowser.open("https://web.whatsapp.com")
                time.sleep(5.0)

            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)
            pyautogui.write(contact_name, interval=0.03)
            time.sleep(0.8)
            pyautogui.press('enter')
            return f"Successfully opened WhatsApp chat for '{contact_name}', Sir."
        except Exception as e:
            return f"Error: Failed to automate WhatsApp chat: {e}"

    def write_excel_cell(self, target: str) -> str:
        """Phase 2 COM Connector: Writes text into an Excel file cell (filepath|cell|value)."""
        try:
            import win32com.client
            parts = target.split("|")
            if len(parts) < 3: 
                return "Error: Target must be formatted as 'filepath|cell|value'"
            
            filepath = os.path.abspath(parts[0].strip())
            cell = parts[1].strip()
            value = parts[2].strip()

            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = True 
            
            if not os.path.exists(filepath):
                wb = excel.Workbooks.Add()
                wb.SaveAs(filepath)
            else:
                wb = excel.Workbooks.Open(filepath)
                
            sheet = wb.ActiveSheet
            sheet.Range(cell).Value = value
            wb.Save()
            
            return f"Successfully wrote '{value}' to cell {cell} in {os.path.basename(filepath)}."
        except Exception as e:
            return f"Office Automation Error: {e}"

    def type_notepad_content(self, target: str) -> str:
        """Phase 2 GUI Connector: Opens Notepad and types text."""
        try:
            subprocess.Popen(["notepad.exe"])
            time.sleep(2) 
            pyautogui.write(target, interval=0.02)
            return f"Successfully opened Notepad and typed: {target}"
        except Exception as e:
            return f"GUI Automation Error: {str(e)}"

    def get_ambient_history(self) -> str:
        """Non-blocking reader for recent ambient activity."""
        log_path = "data/context_history.txt"
        if not os.path.exists(log_path):
            return "No ambient history recorded yet, Sir."
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                recent = "".join(lines[-10:])
                return f"Recent Ambient Activity Log:\n{recent}"
        except Exception as e:
            return f"Error: Could not read ambient history: {e}"

    def execute_action(self, action_type: str, target: str = "") -> str:
        action = action_type.strip().lower()
        target_val = target.strip()
        print(f"[Hands Dispatch]: Action='{action}', Target='{target_val}'")

        try:
            # 🛡️ Native Context Routing
            if action in ["get_context", "ambient", "context"]:
                return self.get_ambient_history()

            elif action == "open_app":
                success = self.launcher.launch(target_val)
                return f"Successfully launched application: {target_val}" if success else f"Failed to launch '{target_val}'. App not found."

            elif action == "write_excel":
                return self.write_excel_cell(target_val)

            elif action == "type_notepad":
                return self.type_notepad_content(target_val)

            elif action == "open_whatsapp":
                return self.open_whatsapp_chat(target_val)

            elif action == "vision_click":
                return self.launcher.click_text_on_screen(target_val)

            elif action in ["maximize_window", "minimize_window", "restore_window", "close_active_window"]:
                win = gw.getActiveWindow() if not target_val or target_val in ["this", "current", "it"] else gw.getWindowsWithTitle(target_val)[0] if gw.getWindowsWithTitle(target_val) else None
                if win:
                    if action == "maximize_window": win.maximize()
                    elif action == "minimize_window": win.minimize()
                    elif action == "restore_window": win.restore()
                    elif action == "close_active_window": win.close()
                    return f"Executed {action} on {win.title}"
                return f"Failed: Could not find window matching '{target_val}'"

            elif action == "focus_window":
                windows = gw.getWindowsWithTitle(target_val)
                if windows:
                    win = windows[0]
                    if win.isMinimized: win.restore()
                    win.activate()
                    return f"Focused active window: {win.title}"
                return f"Failed: Window not found for '{target_val}'"

            elif action == "kill_process":
                target_proc = target_val.lower().replace(".exe", "").strip()
                
                # ⚡ Special handler for Windows UWP Calculator package
                if "calc" in target_proc or "calculator" in target_proc:
                    result1 = subprocess.run("taskkill /F /IM ApplicationFrameHost.exe /T", shell=True, capture_output=True, text=True)
                    result2 = subprocess.run("taskkill /F /IM CalculatorApp.exe /T", shell=True, capture_output=True, text=True)
                    if result1.returncode == 0 or result2.returncode == 0:
                        return f"Successfully terminated {target_val}."
                
                result = subprocess.run(f"taskkill /F /IM {target_proc}.exe /T", shell=True, capture_output=True, text=True)
                return f"Successfully terminated {target_val}." if result.returncode == 0 else f"Failed: Process '{target_val}' not found."

            elif action == "run_terminal":
                subprocess.Popen(f'start cmd /k "{target_val}"', shell=True)
                return "Terminal task launched successfully."

            elif action == "scroll":
                try: clicks = int(target_val); pyautogui.scroll(clicks)
                except: pyautogui.scroll(-500)
                return "Scrolled screen."

            elif action == "press_key":
                pyautogui.press(target_val)
                return f"Pressed key: {target_val}"

            elif action == "wait":
                try: time.sleep(float(target_val))
                except: time.sleep(1.0)
                return f"Waited for {target_val} seconds."

            elif action == "open_website":
                url = target_val if target_val.startswith("http") else f"https://{target_val}"
                webbrowser.open(url)
                return f"Opened website: {url}"

            elif action == "volume_up":
                for _ in range(5): pyautogui.press("volumeup")
                return "Increased volume."

            elif action == "volume_down":
                for _ in range(5): pyautogui.press("volumedown")
                return "Decreased volume."

            elif action == "mute":
                pyautogui.press("volumemute")
                return "Toggled mute."

            elif action == "lock_pc":
                subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
                return "Workstation locked."

            elif action == "close_window":
                pyautogui.hotkey("alt", "f4")
                return "Closed active window."

            elif action == "minimize_all":
                pyautogui.hotkey("win", "d")
                return "Toggled desktop view."

            elif action == "type_text":
                pyautogui.write(target_val, interval=0.01)
                return "Typed requested text."

            elif action == "hotkey":
                keys = [k.strip() for k in target_val.split("+")]
                pyautogui.hotkey(*keys)
                return f"Executed hotkey: {target_val}"

            elif action == "set_volume":
                vol_level = max(0, min(100, int(target_val.replace("%", "").strip())))
                scalar = vol_level / 100.0
                from pycaw.pycaw import AudioUtilities
                devices = AudioUtilities.GetSpeakers()
                devices.EndpointVolume.SetMasterVolumeLevelScalar(scalar, None)
                return f"System volume set to {vol_level}%."

            else:
                return f"Error: Unknown system action: {action_type}"
                
        except Exception as e:
            err_msg = f"Error during execution: {e}"
            print(err_msg)
            return err_msg