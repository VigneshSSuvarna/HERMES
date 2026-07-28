import os
import time
import shutil
import asyncio
import psutil
from pathlib import Path
from modules.brain import HermesBrain
from modules.voice import HermesVoice

class HermesAutonomousAgent:
    def __init__(self):
        self.brain = HermesBrain()
        self.voice = HermesVoice()
        self.is_running = True
        self.ram_threshold_pct = 85.0
        
        # Define target folder for autonomous monitoring
        self.downloads_folder = Path.home() / "Downloads"
        
        # File categorization rules for autonomous sorting
        self.file_categories = {
            "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".csv"],
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"],
            "Executables": [".exe", ".msi"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"]
        }
        
        # Folder names to skip completely during file scans
        self.protected_folders = {"Documents", "Images", "Executables", "Archives"}

    async def observe_system_telemetry(self):
        """Phase 1: Gather RAM and CPU usage telemetry from the operating system kernel."""
        try:
            vm = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=None)
            return {
                "ram_usage_percent": vm.percent,
                "available_ram_gb": round(vm.available / (1024**3), 2),
                "cpu_usage_percent": cpu
            }
        except Exception as e:
            print(f"[Telemetry Warning]: Could not fetch hardware metrics: {e}")
            return {"ram_usage_percent": 0.0, "available_ram_gb": 0.0, "cpu_usage_percent": 0.0}

    def _get_unique_target_path(self, target_file: Path) -> Path:
        """Generates a unique path if a file with the same name already exists in destination."""
        if not target_file.exists():
            return target_file
        
        stem = target_file.stem
        suffix = target_file.suffix
        parent = target_file.parent
        counter = 1
        
        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1

    async def auto_organize_downloads(self):
        """Phase 2: Independent file watcher and auto-sorter with directory and OneDrive safety."""
        if not self.downloads_folder.exists():
            return 0

        moved_count = 0
        current_time = time.time()

        try:
            for item in self.downloads_folder.iterdir():
                item_str = str(item)

                # 1. Skip all directories and protected category subfolders
                if os.path.isdir(item_str) or item.name in self.protected_folders:
                    continue

                # 2. Skip anything that isn't strictly a file
                if not os.path.isfile(item_str):
                    continue

                # 3. Skip hidden files, system files, and active download extensions
                if (
                    item.name.startswith('.') 
                    or item.name.lower().endswith(('.crdownload', '.tmp', '.part', '.download', '.ini'))
                    or not item.suffix
                ):
                    continue

                # 4. Ensure file has been untouched for at least 3 seconds (not mid-download)
                try:
                    file_age = current_time - item.stat().st_mtime
                    if file_age < 3:
                        continue
                except Exception:
                    continue

                # 5. Categorize and move file safely
                ext = item.suffix.lower()
                for category, extensions in self.file_categories.items():
                    if ext in extensions:
                        target_dir = self.downloads_folder / category
                        target_dir.mkdir(exist_ok=True)
                        
                        target_file = self._get_unique_target_path(target_dir / item.name)
                        
                        try:
                            shutil.move(item_str, str(target_file))
                            moved_count += 1
                        except Exception:
                            # Catch all permission/OneDrive lock errors silently
                            pass
                        break
        except Exception as scan_err:
            print(f"[Agent Directory Scan Warning]: {scan_err}")

        return moved_count

    async def execute_autonomous_loop(self):
        """Phase 3: Continuous autonomous background monitoring loop."""
        print("[Agent]: Autonomous Routine Engine Active in Background.")
        
        while self.is_running:
            try:
                # 1. Trigger File System Sorter
                moved = await self.auto_organize_downloads()
                if moved > 0:
                    msg = f"Independently organized {moved} downloaded files, Sir."
                    print(f"[Agent Action]: {msg}")
                    await asyncio.to_thread(self.voice.speak, msg)

                # 2. Trigger System Telemetry Check
                telemetry = await self.observe_system_telemetry()
                if telemetry["ram_usage_percent"] > self.ram_threshold_pct:
                    print(f"[Agent Warning]: High RAM usage detected ({telemetry['ram_usage_percent']}%).")
                    agent_prompt = f"SYSTEM ALERT: Current system RAM usage is high at {telemetry['ram_usage_percent']}%."
                    decision = await asyncio.to_thread(self.brain.think, agent_prompt)
                    await asyncio.to_thread(self.voice.speak, "System memory footprint is high, Sir. Re-allocating reserves.")

                # Sleep for 30 seconds before running the next autonomous sweep
                await asyncio.sleep(30)
                
            except Exception as e:
                print(f"[Agent Loop Exception]: {e}")
                await asyncio.sleep(5)