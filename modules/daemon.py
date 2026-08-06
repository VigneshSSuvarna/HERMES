import threading
import time
import psutil

class HermesDaemon:
    def __init__(self, tts_engine=None):
        print("[Daemon]: Initializing Background Proactive Subsystem...")
        self.tts_engine = tts_engine  # Optional: pass your voice engine here so he can speak out loud
        self.is_running = False
        
        # Cooldowns to prevent HERMES from spamming alerts
        self.cooldowns = {
            "cpu_warning": 0,
            "battery_warning": 0,
            "disk_warning": 0
        }
        
    def start(self):
        """Starts the background monitoring loop in a separate thread."""
        if self.is_running:
            return
        self.is_running = True
        daemon_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        daemon_thread.start()
        print("[Daemon]: Proactive threaded monitoring active. HERMES is watching.")

    def stop(self):
        self.is_running = False

    def _alert(self, message):
        """Handles the actual interruption (Print + Voice)."""
        print(f"\n[PROACTIVE ALERT]: {message}")
        if self.tts_engine:
            try:
                self.tts_engine.speak(message)
            except Exception:
                pass

    def _monitor_loop(self):
        """The infinite background loop that watches system vitals safely."""
        while self.is_running:
            try:
                current_time = time.time()
                
                # 1. 🌡️ Monitor CPU Usage (Alert if stuck above 90%)
                cpu_usage = psutil.cpu_percent(interval=1)
                if cpu_usage > 90.0:
                    if current_time - self.cooldowns["cpu_warning"] > 300: # Every 5 minutes
                        self._alert(f"Sir, pardon the interruption. System CPU usage has spiked to {int(cpu_usage)} percent. You may want to check for runaway processes.")
                        self.cooldowns["cpu_warning"] = current_time

                # 2. 🔋 Monitor Battery Life (If on a laptop)
                if hasattr(psutil, 'sensors_battery'):
                    battery = psutil.sensors_battery()
                    if battery:
                        if battery.percent < 20 and not battery.power_plugged:
                            if current_time - self.cooldowns["battery_warning"] > 600: # Every 10 mins
                                self._alert(f"Sir, battery reserves are dropping. We are currently at {battery.percent} percent. Please connect to a power source.")
                                self.cooldowns["battery_warning"] = current_time
                        
                        elif battery.percent == 100 and battery.power_plugged:
                            if current_time - self.cooldowns["battery_warning"] > 3600: # Hourly
                                self._alert("Sir, the battery has reached maximum capacity. You may disconnect the power.")
                                self.cooldowns["battery_warning"] = current_time

                # 3. 💾 Monitor Primary Disk Space (Alert if below 10GB)
                disk_usage = psutil.disk_usage('/')
                free_space_gb = disk_usage.free / (1024 ** 3)
                if free_space_gb < 10.0:
                    if current_time - self.cooldowns["disk_warning"] > 3600: # Hourly
                        self._alert(f"Warning, Sir. Primary storage is critically low. Only {int(free_space_gb)} gigabytes remaining.")
                        self.cooldowns["disk_warning"] = current_time

            except Exception as e:
                # Ensures background thread never crashes due to a minor monitoring glitch
                pass

            # Sleep for 10 seconds before checking again (Ultra-low CPU overhead)
            time.sleep(10)