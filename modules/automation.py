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
    """Diagnostic-grade application launcher with verbose error tracking."""
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
        """
        Visually finds an element on the screen based on a natural language description 
        and clicks it using AI vision coordinates.
        """
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
                return f"Could not visually locate '{description}' on the screen."
                
            coords_str = response.strip().split()[0]
            x_str, y_str = coords_str.replace("(", "").replace(")", "").split(",")
            x, y = int(x_str.strip()), int(y_str.strip())
            
            pyautogui.moveTo(x, y, duration=0.5)
            pyautogui.click()
            
            return f"Successfully clicked on '{description}' at coordinates ({x}, {y})."
            
        except Exception as e:
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
            return f"Visual click failed: {e}"

    def launch(self, app_name: str) -> bool:
        target = app_name.strip().lower()
        if not target:
            return False

        # Protocol aliases for standard desktop apps & UWP store apps
        aliases = {
            "chrome": "chrome",
            "vscode": "code",
            "word": "winword",
            "excel": "excel",
            "notepad": "notepad",
            "whatsapp": "whatsapp:",
            "spotify": "spotify:",
            "calculator": "calculator:",
            "calc": "calculator:",
            "soundrecorder": "Sound Recorder:",
            "voice recorder": "Sound Recorder:",
            "netflix": "netflix:",
            "settings": "ms-settings:"
        }
        
        lookup_target = aliases.get(target, target)
        print(f"[Launcher]: Executing nuclear bypass for '{lookup_target}'...")

        # LAYER 1: Native Shell / URI Protocol Injection with Auto-Focus
        try:
            print(f"[Layer 1] Injecting '{lookup_target}' into Windows Core...")
            if ":" in lookup_target:
                subprocess.Popen(f'explorer.exe {lookup_target}', shell=True)
            else:
                subprocess.Popen(f'start {lookup_target}', shell=True)
                
            # Wait 1.5 seconds for the app window to render
            time.sleep(1.5)

            # --- AUTOMATIC WINDOW FOCUS FIX ---
            try:
                search_term = target.replace(":", "").replace("app", "").strip()
                windows = gw.getAllWindows()
                for win in windows:
                    if search_term in win.title.lower():
                        if win.isMinimized:
                            win.restore()
                        win.activate()
                        print(f"[Launcher]: Successfully focused window -> '{win.title}'")
                        break
            except Exception as focus_err:
                print(f"[Launcher Focus Warning]: {focus_err}")

            print("[Layer 1] Execution sent successfully.")
            return True
        except Exception as e:
            print(f"[Layer 1] Core Injection Failed: {e}")

        # LAYER 2: PowerShell Stealth Execution
        try:
            print(f"[Layer 2] Injecting '{lookup_target}' into PowerShell...")
            subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "-Command", f"Start-Process '{lookup_target}'"])
            time.sleep(1.5)
            
            # Auto-focus fallback for PowerShell layer
            try:
                search_term = target.replace(":", "").replace("app", "").strip()
                windows = gw.getAllWindows()
                for win in windows:
                    if search_term in win.title.lower():
                        if win.isMinimized:
                            win.restore()
                        win.activate()
                        break
            except:
                pass

            print("[Layer 2] Execution sent successfully.")
            return True
        except Exception as e:
            print(f"[Layer 2] PowerShell Failed: {e}")

        # LAYER 3: Standard OS Startfile
        try:
            print(f"[Layer 3] Attempting standard Python startfile...")
            os.startfile(lookup_target)
            print("[Layer 3] Execution sent successfully.")
            return True
        except Exception as e:
            print(f"[Layer 3] Startfile Failed: {e}")

        print(f"[Launcher Error]: All bypasses failed for '{target}'.")
        return False


class HermesHands:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        self.launcher = WindowsUniversalLauncher()
        print("[Hands]: Universal Windows Automation Engine Initialized with Verbose Tracing.")

    def open_whatsapp_chat(self, contact_name: str) -> str:
        """
        Automates WhatsApp (Desktop app or Web) to search for a contact and open their chat.
        """
        try:
            print(f"[Hands]: Opening WhatsApp and searching for contact: '{contact_name}'...")
            
            # 1. Bring WhatsApp or Chrome to focus (tries WhatsApp desktop app first, then browser fallback)
            whatsapp_windows = [w for w in gw.getWindowsWithTitle('WhatsApp') if w.title]
            
            if whatsapp_windows:
                w = whatsapp_windows[0]
                if w.isMinimized:
                    w.restore()
                w.activate()
                time.sleep(1.0)
            else:
                # Fallback: Open WhatsApp Web via default browser if desktop app isn't open
                webbrowser.open("https://web.whatsapp.com")
                print("[Hands]: WhatsApp Desktop app not found. Opening WhatsApp Web... waiting 6 seconds to load.")
                time.sleep(6.0)

            # 2. Press Ctrl + F to focus the chat search bar
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.8)

            # 3. Type the contact name cleanly
            pyautogui.write(contact_name, interval=0.05)
            time.sleep(1.2)

            # 4. Press Enter to select the top matching contact/chat
            pyautogui.press('enter')
            time.sleep(0.5)

            return f"Successfully opened WhatsApp chat for '{contact_name}', Sir."

        except Exception as e:
            return f"Failed to automate WhatsApp chat: {e}"

    def execute_action(self, action_type: str, target: str = "") -> str:
        action = action_type.strip().lower()
        target_val = target.strip()
        print(f"[Hands Dispatch]: Action='{action}', Target='{target_val}'")

        try:
            # --- APP LAUNCHING ---
            if action == "open_app":
                success = self.launcher.launch(target_val)
                if success:
                    return f"Successfully launched application: {target_val}"
                else:
                    return f"Could not locate or launch '{target_val}' on this system."

            # --- WHATSAPP GUI MACRO ---
            elif action == "open_whatsapp":
                return self.open_whatsapp_chat(target_val)

            # --- ADVANCED WINDOW MANAGEMENT ---
            elif action in ["maximize_window", "minimize_window", "restore_window", "close_active_window"]:
                if not target_val or target_val in ["this", "current", "it", "window"]:
                    win = gw.getActiveWindow()
                else:
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

            # --- PROCESS KILLER (NUCLEAR TASKKILL) ---
            elif action == "kill_process":
                target_proc = target_val.lower().strip()
                
                aliases = {
                    "whatsapp": "whatsapp.exe",
                    "spotify": "spotify.exe",
                    "chrome": "chrome.exe",
                    "google": "chrome.exe",
                    "browser": "chrome.exe",
                    "code": "code.exe",
                    "vscode": "code.exe",
                    "calculator": "calculatorapp.exe",
                    "calc": "calculatorapp.exe",
                    "notepad": "notepad.exe"
                }
                
                exe_name = aliases.get(target_proc, f"{target_proc}.exe")
                print(f"[Hands]: Attempting nuclear TaskKill on {exe_name}...")
                
                try:
                    result = subprocess.run(f"taskkill /F /IM {exe_name} /T", shell=True, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        return f"Successfully terminated {target_val}."
                    else:
                        killed_any = False
                        for proc in psutil.process_iter(['pid', 'name']):
                            try:
                                if exe_name.replace(".exe", "") in proc.info['name'].lower():
                                    proc.kill()
                                    killed_any = True
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                continue
                                
                        if killed_any:
                            return f"Successfully terminated {target_val} via memory sweep."
                        return f"Could not find any active process matching '{exe_name}'."
                        
                except Exception as e:
                    return f"[Kill Error]: {e}"

            # --- SYSTEM TERMINAL (GOD MODE) ---
            elif action == "run_terminal":
                print(f"[Hands]: Executing system command -> {target_val}")
                try:
                    result = subprocess.run(["powershell", "-Command", target_val], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        out = result.stdout.strip()
                        return f"Terminal execution successful. Output: {out[:100]}..." if out else "Terminal execution successful."
                    else:
                        return f"Terminal execution failed: {result.stderr.strip()}"
                except Exception as e:
                    return f"Terminal error: {e}"

            elif action == "scroll":
                try:
                    clicks = int(target_val)
                    pyautogui.scroll(clicks)
                    return f"Scrolled screen by {clicks} units."
                except:
                    pyautogui.scroll(-500)
                    return "Scrolled down."
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

            elif action == "close_window":
                pyautogui.hotkey("alt", "f4")
                return "Closed active window."

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
                
            elif action == "set_volume":
                try:
                    vol_level = int(target_val.replace("%", "").strip())
                    vol_level = max(0, min(100, vol_level)) # Clamp between 0 and 100
                    scalar = vol_level / 100.0
                    
                    try:
                        from pycaw.pycaw import AudioUtilities
                        devices = AudioUtilities.GetSpeakers()
                        volume = devices.EndpointVolume
                        volume.SetMasterVolumeLevelScalar(scalar, None)
                    except Exception:
                        from ctypes import cast, POINTER
                        from comtypes import CLSCTX_ALL
                        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                        devices = AudioUtilities.GetSpeakers()
                        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                        volume = cast(interface, POINTER(IAudioEndpointVolume))
                        volume.SetMasterVolumeLevelScalar(scalar, None)
                        
                    return f"System volume set to {vol_level}%, Sir."
                except ImportError:
                    return "Sir, please run 'pip install pycaw comtypes' in your terminal."
                except Exception as e:
                    return f"Failed to set volume: {e}"

            else:
                return f"Unknown system action: {action_type}"
            
        except Exception as e:
            err_msg = f"[Execution Error]: {e}"
            print(err_msg)
            return err_msg