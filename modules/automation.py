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
    """Dynamically finds and launches ANY application installed on Windows with robust alias mapping."""
    def __init__(self):
        # Universal Start Menu shortcut locations
        user_profile = os.getenv("USERPROFILE", "C:\\Users\\Default")
        self.shortcut_dirs = [
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
            os.path.join(user_profile, r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs"),
            r"C:\Users\Public\Desktop",
            os.path.join(user_profile, "Desktop")
        ]
        
        # Build app cache dictionary on startup
        self.app_cache = {}
        self.refresh_app_cache()

    def refresh_app_cache(self):
        """Scans all Windows Start Menu shortcuts and Desktop links."""
        self.app_cache.clear()
        for folder in self.shortcut_dirs:
            if os.path.exists(folder):
                for root, _, files in os.walk(folder):
                    for file in files:
                        if file.endswith((".lnk", ".url", ".exe")):
                            clean_name = file.rsplit(".", 1)[0].lower()
                            full_path = os.path.join(root, file)
                            self.app_cache[clean_name] = full_path

    def launch(self, app_name: str) -> bool:
        """Attempts to locate and launch the specified application robustly."""
        target = app_name.strip().lower()
        if not target:
            return False

        # Common App Aliases for instant matching
        aliases = {
            "chrome": "google chrome",
            "vscode": "visual studio code",
            "code": "visual studio code",
            "word": "winword",
            "excel": "excel",
            "powerpoint": "powerpnt",
            "notepad": "notepad",
            "calc": "calc",
            "calculator": "calc",
            "spotify": "spotify",
            "discord": "discord"
        }
        
        lookup_target = aliases.get(target, target)

        # 1. Direct Windows command / Start execution
        try:
            os.system(f"start {lookup_target}")
            return True
        except Exception:
            pass

        # 2. Check cached Start Menu shortcuts
        for name, path in self.app_cache.items():
            if lookup_target == name or lookup_target in name or name in lookup_target:
                try:
                    os.startfile(path)
                    return True
                except Exception:
                    pass

        # 3. Aggressive wildcard scan in Program Files & AppData
        search_roots = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
            os.path.expandvars(r"%APPDATA%")
        ]

        for s_root in search_roots:
            if os.path.exists(s_root):
                matches = glob.glob(os.path.join(s_root, "**", f"*{lookup_target}*.exe"), recursive=True)
                if matches:
                    try:
                        os.startfile(matches[0])
                        return True
                    except Exception:
                        pass

        return False


class HermesHands:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        self.launcher = WindowsUniversalLauncher()
        print("[Hands]: Universal Windows Automation Engine Initialized.")

    def execute_action(self, action_type: str, target: str = "") -> str:
        """Master dispatcher for OS execution commands."""
        action = action_type.strip().lower()
        target_val = target.strip()

        try:
            # 1. ADVANCED APP OPERATION & CHAINING
            if action == "focus_window":
                windows = gw.getWindowsWithTitle(target_val)
                if not windows:
                    all_wins = gw.getAllWindows()
                    windows = [w for w in all_wins if target_val.lower() in w.title.lower()]
                
                if windows:
                    win = windows[0]
                    if win.isMinimized:
                        win.restore()
                    win.activate()
                    return f"Focused active window: {win.title}"
                return f"Could not find an open window for '{target_val}'"

            elif action == "press_key":
                pyautogui.press(target_val)
                return f"Pressed key: {target_val}"
                
            elif action == "wait":
                try:
                    delay = float(target_val)
                    time.sleep(delay)
                    return f"Waited for {delay} seconds."
                except:
                    time.sleep(1)
                    return "Waited standard 1 second."

            # 2. UNIVERSAL APPLICATION & WEBSITE CONTROLLER
            elif action == "open_app":
                success = self.launcher.launch(target_val)
                if success:
                    return f"Successfully launched application: {target_val}"
                else:
                    return f"Could not locate '{target_val}' in system shortcuts or Program Files."

            elif action == "open_website":
                url = target_val if target_val.startswith("http") else f"https://{target_val}"
                webbrowser.open(url)
                return f"Opened website: {url}"

            # 3. AUDIO & MEDIA CONTROLLER
            elif action == "volume_up":
                for _ in range(5):
                    pyautogui.press("volumeup")
                return "Increased system volume."

            elif action == "volume_down":
                for _ in range(5):
                    pyautogui.press("volumedown")
                return "Decreased system volume."

            elif action == "mute":
                pyautogui.press("volumemute")
                return "Toggled master audio mute."

            elif action == "media_play_pause":
                pyautogui.press("playpause")
                return "Toggled media playback."

            elif action == "media_next":
                pyautogui.press("nexttrack")
                return "Skipped to next track."

            elif action == "media_prev":
                pyautogui.press("prevtrack")
                return "Returned to previous track."

            # 4. WORKSTATION POWER COMMANDS
            elif action == "lock_pc":
                subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
                return "Workstation locked, Sir."

            elif action == "shutdown_pc":
                os.system("shutdown /s /t 10")
                return "Initiating system shutdown sequence..."

            elif action == "restart_pc":
                os.system("shutdown /r /t 10")
                return "Initiating system restart..."

            # 5. WINDOW & PROCESS MANAGEMENT
            elif action == "close_window":
                pyautogui.hotkey("alt", "f4")
                return "Closed active window."

            elif action == "minimize_all":
                pyautogui.hotkey("win", "d")
                return "Toggled desktop view."

            elif action == "kill_process":
                killed_any = False
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if target_val.lower() in proc.info['name'].lower():
                            proc.kill()
                            killed_any = True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                if killed_any:
                    return f"Terminated process matching '{target_val}'."
                return f"No active process matching '{target_val}' was found."

            # 6. KEYBOARD & MOUSE MACROS
            elif action == "type_text":
                pyautogui.write(target_val, interval=0.02)
                return "Typed requested text."

            elif action == "hotkey":
                keys = [k.strip() for k in target_val.split("+")]
                pyautogui.hotkey(*keys)
                return f"Executed hotkey: {target_val}"

            # 7. FILE EXPLORER CONTROLLER
            elif action == "open_explorer":
                path = target_val if target_val else "C:\\"
                os.startfile(path)
                return f"Opened File Explorer at: {path}"

            else:
                return f"Unknown system action: {action_type}"

        except Exception as e:
            return f"[Execution Error]: {e}"


if __name__ == "__main__":
    hands = HermesHands()
    print("Testing Universal Launcher...")
    print(hands.execute_action("open_app", "chrome"))