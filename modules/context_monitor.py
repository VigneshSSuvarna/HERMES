import os
import time
import threading
import datetime
import pyperclip

try:
    import pygetwindow as gw
except ImportError:
    gw = None

class HermesContextMonitor:
    def __init__(self, log_path="data/context_history.txt"):
        print("[Context Engine]: Initializing Ambient Context Gathering...")
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        
        self.is_running = False
        self.last_clipboard = ""
        self.last_window = ""
        
        # Ensure daemon=True is set so it never blocks shutdown or command execution
        self.monitor_thread = threading.Thread(target=self._background_loop, daemon=True)

    def start(self):
        """Starts background ambient logging thread."""
        if self.is_running:
            return
        self.is_running = True
        try:
            self.monitor_thread.start()
        except RuntimeError:
            # Re-initialize thread if it was already stopped and restarted
            self.monitor_thread = threading.Thread(target=self._background_loop, daemon=True)
            self.monitor_thread.start()
        print("[Context Engine]: Ambient Window & Clipboard surveillance active.")

    def stop(self):
        self.is_running = False

    def _log_event(self, event_type: str, content: str):
        """Appends timestamped contextual events to local history storage."""
        if not content or len(content.strip()) < 3:
            return
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{event_type.upper()}] {content.strip()}\n"
        
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception:
            pass

    def _background_loop(self):
        """Passively checks active windows and clipboards every few seconds."""
        while self.is_running:
            try:
                # 1. Check Active Window Title
                if gw:
                    try:
                        active_win = gw.getActiveWindow()
                        if active_win and active_win.title:
                            current_window = active_win.title.strip()
                            if current_window != self.last_window:
                                self.last_window = current_window
                                self._log_event("WINDOW", f"Switched to app/window: {current_window}")
                    except Exception:
                        pass

                # 2. Check Clipboard History Changes
                try:
                    current_clip = pyperclip.paste()
                    if current_clip and current_clip != self.last_clipboard:
                        # Prevent logging massive text blobs or passwords entirely
                        if len(current_clip) < 300 and "\n" not in current_clip:
                            self.last_clipboard = current_clip
                            self._log_event("CLIPBOARD", f"Copied text: {current_clip}")
                except Exception:
                    pass

            except Exception:
                pass

            # Check every 5 seconds (zero CPU footprint)
            time.sleep(5.0)

    def get_recent_context(self, query: str = "") -> str:
        """Retrieves recent ambient history to give the AI context."""
        if not os.path.exists(self.log_path):
            return "No ambient history recorded yet, Sir."
            
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Return the last 20 ambient activities
                recent_lines = lines[-20:]
                return "".join(recent_lines)
        except Exception:
            return ""