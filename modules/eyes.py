import os
from PIL import ImageGrab


class HermesEyes:
    def __init__(self):
        self.temp_screen_path = "temp_screenshot.png"

    def capture_screen(self) -> str:
        """Captures the current primary monitor screenshot."""
        try:
            screenshot = ImageGrab.grab()
            screenshot.save(self.temp_screen_path)
            print("[Eyes]: Desktop screen captured successfully.")
            return self.temp_screen_path
        except Exception as e:
            print(f"[Eyes Error]: Screen capture failed: {e}")
            return ""

    def cleanup(self):
        """Removes temporary image artifacts."""
        if os.path.exists(self.temp_screen_path):
            try:
                os.remove(self.temp_screen_path)
            except Exception:
                pass


if __name__ == "__main__":
    eyes = HermesEyes()
    path = eyes.capture_screen()
    print(f"[Eyes Test]: Saved to {path}")