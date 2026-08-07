import os
import cv2
try:
    import pyautogui
except ImportError:
    pyautogui = None
from PIL import Image


class HermesEyes:
    """Handles real-time webcam captures and desktop screen snapshots for multimodal AI analysis."""
    def __init__(self):
        self.screenshot_path = "temp_vision_capture.jpg"
        print("[Eyes]: Blazing-fast Multimodal Vision Subsystem Initialized.")

    def capture_screen(self) -> str:
        """Takes an ultra-fast, downscaled screenshot of the primary monitor for sub-second processing."""
        try:
            if pyautogui is None:
                print("[Eyes Error]: pyautogui package is missing.")
                return None

            screenshot = pyautogui.screenshot()
            
            # ⚡ SPEED OPTIMIZATION: Downscale aggressively to max 1280px 
            # This cuts network upload bottlenecks down to milliseconds!
            screenshot.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
            
            # Save as optimized JPEG with compressed quality
            screenshot.save(self.screenshot_path, "JPEG", quality=75)
            print(f"[Eyes]: Screen captured successfully: {self.screenshot_path}")
            return self.screenshot_path
        except Exception as e:
            print(f"[Eyes Error]: Screen capture failed: {e}")
            return None

    def capture_webcam(self) -> str:
        """Captures a single frame from the live webcam feed."""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("[Eyes Warning]: No webcam detected.")
                return None
            
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                cv2.imwrite(self.screenshot_path, frame)
                return self.screenshot_path
            return None
        except Exception as e:
            print(f"[Eyes Error]: Webcam capture failed: {e}")
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