import os
import time
from PIL import Image
import pyautogui

# Check for OpenCV (Webcam capture support)
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

# Import Gemini API support
try:
    from google import genai
    HAS_NEW_GENAI = True
except ImportError:
    try:
        import google.generativeai as genai
        HAS_NEW_GENAI = False
    except ImportError:
        genai = None


class HermesEyes:
    def __init__(self, api_key=None):
        """Initialize HERMES visual processing engine."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-2.5-flash"
        
        if HAS_NEW_GENAI:
            if self.api_key:
                self.client = genai.Client(api_key=self.api_key)
            else:
                self.client = genai.Client()
        elif genai is not None:
            if self.api_key:
                genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)

    def capture_screen(self, save_path="temp_screen.png") -> str:
        """Takes an instant snapshot of your current monitor."""
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            print(f"[Eyes]: Desktop snapshot captured -> '{save_path}'")
            return save_path
        except Exception as e:
            print(f"[Eyes Error]: Screen capture failed: {e}")
            return ""

    def capture_webcam(self, save_path="temp_webcam.jpg") -> str:
        """Captures a frame from your default webcam."""
        if not HAS_OPENCV:
            print("[Eyes Error]: opencv-python is not installed (`pip install opencv-python`).")
            return ""

        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("[Eyes Error]: Could not access webcam device.")
                return ""

            # Warm up camera sensor
            time.sleep(0.2)
            ret, frame = cap.read()
            cap.release()

            if ret:
                cv2.imwrite(save_path, frame)
                print(f"[Eyes]: Webcam frame captured -> '{save_path}'")
                return save_path
            else:
                print("[Eyes Error]: Failed to read frame from webcam.")
                return ""
        except Exception as e:
            print(f"[Eyes Exception]: Webcam error: {e}")
            return ""

    def analyze_image(self, image_path: str, prompt: str = "Describe what you see in this image in detail.") -> str:
        """Sends an image to Gemini Vision AI for multimodal analysis."""
        if not os.path.exists(image_path):
            return "Error: Target image file does not exist."

        try:
            img = Image.open(image_path)
            print(f"[Eyes]: Processing visual payload with prompt: '{prompt}'...")

            if HAS_NEW_GENAI:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt, img]
                )
                return response.text
            else:
                response = self.model.generate_content([prompt, img])
                return response.text

        except Exception as e:
            print(f"[Eyes Error]: Visual processing failed: {e}")
            return f"Sorry Sir, visual processing encountered an error: {e}"
        finally:
            # Clean up temporary snapshot file
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception:
                    pass

    def see_screen(self, query: str = "Analyze what is on my screen right now.") -> str:
        """One-step tool to grab screen and summarize content."""
        img_path = self.capture_screen()
        if img_path:
            return self.analyze_image(img_path, prompt=query)
        return "Failed to capture screen image, Sir."

    def see_webcam(self, query: str = "Describe what you see in front of the camera.") -> str:
        """One-step tool to grab camera feed and describe object/person."""
        img_path = self.capture_webcam()
        if img_path:
            return self.analyze_image(img_path, prompt=query)
        return "Failed to capture webcam image, Sir."

    