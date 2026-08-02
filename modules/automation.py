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
    """Dynamically finds and launches ANY application installed on Windows with human-mimic fallback."""
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

    def launch(self, app_name: str) -> bool:
        target = app_name.strip().lower()
        if not target:
            return False

        # UWP Apps use registered URI protocols (adding a colon)
        aliases = {
            "chrome": "chrome",
            "vscode": "code",
            "word": "winword",
            "excel": "excel",
            "notepad": "notepad",
            "whatsapp": "whatsapp:",
            "spotify": "spotify:"
        }
        
        lookup_target = aliases.get(target, target)

        # 1. Direct Execution (Fastest)
        try:
            # os.startfile will cleanly throw an error if it fails, unlike os.system
            os.startfile(lookup_target)
            return True
        except Exception:
            pass

        # 2. Check cached Start Menu shortcuts
        for name, path in self.app_cache.items():
            if target == name or target in name:
                try:
                    os.startfile(path)
                    return True
                except Exception:
                    pass

        # 3. GHOST TYPING PROTOCOL (Bulletproof for Windows Store Apps)
        # If the file path fails, HERMES will manually type it into the Start Menu
        try:
            pyautogui.press('win')
            time.sleep(0.8)  # Wait for Start Menu to open
            pyautogui.write(target, interval=0.05)
            time.sleep(0.8)  # Wait for Windows Search to find the app
            pyautogui.press('enter')
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

            elif action == "open_app":
                success = self.launcher.launch(target_val)
                if success:
                    return f"Successfully launched application: {target_val}"
                else:
                    return f"Could not locate '{target_val}' on this system."

            elif action == "open_website":
                url = target_val if target_val.startswith("http") else f"https://{target_val}"
                webbrowser.open(url)
                return f"Opened website: {url}"

            elif action == "volume_up":
                for _ in range(5): pyautogui.press("volumeup")
                return "Increased system volume."

            elif action == "volume_down":
                for _ in range(5): pyautogui.press("volumedown")
                return "Decreased system volume."

            elif action == "mute":
                pyautogui.press("volumemute")
                return "Toggled master audio mute."

            elif action == "media_play_pause":
                pyautogui.press("playpause")
                return "Toggled media playback."

            elif action == "lock_pc":
                subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
                return "Workstation locked, Sir."

            # --- THE CLOSING PROTOCOLS ---
            elif action == "close_active_window":
                pyautogui.hotkey("alt", "f4")
                return "Closed active window."

            elif action == "kill_process":
                killed_any = False
                target_proc = target_val.lower().strip()
                
                # Special alias handling for UWP apps
                if target_proc == "whatsapp": target_proc = "whatsapp.exe"
                elif target_proc == "spotify": target_proc = "spotify.exe"
                elif target_proc in ["chrome", "google", "browser"]: target_proc = "chrome.exe"
                elif target_proc in ["code", "vscode"]: target_proc = "code.exe"

                # Scan RAM for the active application and terminate it
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if target_proc in proc.info['name'].lower():
                            proc.kill()
                            killed_any = True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if killed_any:
                    return f"Successfully terminated {target_val}."
                return f"Could not find any active process named '{target_val}'."

            elif action == "minimize_all":
                pyautogui.hotkey("win", "d")
                return "Toggled desktop view."

            elif action == "type_text":
                pyautogui.write(target_val, interval=0.02)
                return "Typed requested text."

            elif action == "hotkey":
                keys = [k.strip() for k in target_val.split("+")]
                pyautogui.hotkey(*keys)
                return f"Executed hotkey: {target_val}"
            # --- ADVANCED WINDOW MANAGEMENT ---
            elif action in ["maximize_window", "minimize_window", "restore_window", "close_active_window"]:
                # If no target specified, act on the currently active window
                if not target_val or target_val in ["this", "current", "it", "window"]:
                    win = gw.getActiveWindow()
                else:
                    # Search for a specific window by name
                    windows = gw.getWindowsWithTitle(target_val)
                    if not windows:
                        all_wins = gw.getAllWindows()
                        windows = [w for w in all_wins if target_val.lower() in w.title.lower()]
                    win = windows[0] if windows else None

                if win:
                    if action == "maximize_window":
                        win.maximize()
                        return f"Maximized window: {win.title}"
                    elif action == "minimize_window":
                        win.minimize()
                        return f"Minimized window: {win.title}"
                    elif action == "restore_window":
                        win.restore()
                        return f"Restored window: {win.title}"
                    elif action == "close_active_window":
                        win.close()
                        return f"Closed window: {win.title}"
                else:
                    return f"Could not find an open window matching '{target_val}'"

            elif action == "focus_window":
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

            elif action == "kill_process":
                # Scans RAM for the active application and forcefully terminates it
                killed_any = False
                target_proc = target_val.lower().strip()
                
                # Special alias handling for UWP/Tricky apps
                if target_proc == "whatsapp": target_proc = "whatsapp.exe"
                elif target_proc == "spotify": target_proc = "spotify.exe"
                elif target_proc in ["chrome", "google", "browser"]: target_proc = "chrome.exe"
                elif target_proc in ["code", "vscode"]: target_proc = "code.exe"

                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if target_proc in proc.info['name'].lower():
                            proc.kill()
                            killed_any = True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if killed_any:
                    return f"Successfully terminated {target_val}."
                return f"Could not find any active process named '{target_val}'."

            else:
                return f"Unknown system action: {action_type}"

        except Exception as e:
            return f"[Execution Error]: {e}"
        