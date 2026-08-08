import os
from PIL import Image

try:
    import pyautogui
except ImportError:
    pyautogui = None


class HermesEyes:
    """Handles desktop screen snapshots for multimodal AI analysis without requiring a camera."""
    def __init__(self):
        self.screenshot_path = "temp_vision_capture.jpg"
        print("[Eyes]: Blazing-fast Desktop Vision Subsystem Initialized (Camera Free).")

    def capture_screen(self) -> str:
        """Takes an ultra-fast, downscaled screenshot of the primary monitor for sub-second processing."""
        try:
            if pyautogui is None:
                print("[Eyes Error]: pyautogui package is missing.")
                return None

            screenshot = pyautogui.screenshot()
            
            # ⚡ SPEED OPTIMIZATION: Downscale aggressively to max 1280px 
            screenshot.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
            
            # Save as optimized JPEG with compressed quality
            screenshot.save(self.screenshot_path, "JPEG", quality=75)
            print(f"[Eyes]: Screen captured successfully: {self.screenshot_path}")
            return self.screenshot_path
        except Exception as e:
            print(f"[Eyes Error]: Screen capture failed: {e}")
            return None

    def cleanup(self):
        """Removes temporary image files from disk."""
        if os.path.exists(self.screenshot_path):
            try:
                os.remove(self.screenshot_path)
            except Exception:
                pass


if __name__ == "__main__":
    eyes = HermesEyes()
    print("Testing screen capture...")
    path = eyes.capture_screen()
    print(f"Saved to: {path}")
    eyes.cleanup()