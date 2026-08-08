import math
import time
import tkinter as tk
from tkinter import Canvas

class HexagonGauge(Canvas):
    """Cyberpunk hexagonal visual progress / status gauge."""
    def __init__(self, parent, width=120, height=120, title="SYSTEM"):
        super().__init__(parent, width=width, height=height, bg="#0b0f19", highlightthickness=0)
        self.width = width
        self.height = height
        self.title = title
        self.progress = 75.0  # Percentage
        self.draw_gauge()

    def draw_gauge(self):
        self.delete("all")
        cx, cy = self.width / 2, self.height / 2
        r = min(cx, cy) - 15

        # Draw outer rotating/hex ring lines
        points = []
        for i in range(6):
            angle = math.radians(i * 60 - 30)
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.append((x, y))

        self.create_polygon(points, outline="#00ffcc", width=2, fill="")
        
        # Inner text indicators
        self.create_text(cx, cy - 8, text=self.title, fill="#00ffcc", font=("Consolas", 9, "bold"))
        self.create_text(cx, cy + 10, text=f"{int(self.progress)}%", fill="#ffffff", font=("Consolas", 10))

    def update_value(self, val: float):
        self.progress = max(0.0, min(100.0, val))
        self.draw_gauge()


class CyberOscilloscope(Canvas):
    """Animated audio-reactive line wave visualizer."""
    def __init__(self, parent, width=300, height=80):
        super().__init__(parent, width=width, height=height, bg="#0b0f19", highlightthickness=0)
        self.width = width
        self.height = height
        self.offset = 0
        self.animate()

    def animate(self):
        self.delete("all")
        cy = self.height / 2
        points = []
        
        for x in range(0, self.width, 4):
            # Sine wave modulation modulated by offset
            y = cy + math.sin((x + self.offset) * 0.05) * 18 * math.sin(x * 0.01)
            points.append((x, y))

        if len(points) > 1:
            self.create_line(points, fill="#00ffcc", width=2, smooth=True)

        self.offset += 6
        self.after(50, self.animate)


class StorageDiagnosticsPanel(Canvas):
    """System memory and storage status visualizer."""
    def __init__(self, parent, width=220, height=120):
        super().__init__(parent, width=width, height=height, bg="#0b0f19", highlightthickness=0)
        self.width = width
        self.height = height
        self.draw_panel()

    def draw_panel(self):
        self.delete("all")
        # Cyberpunk container outline
        self.create_rectangle(5, 5, self.width - 5, self.height - 5, outline="#1f293d", width=1)
        self.create_text(15, 15, text="CORE TELEMETRY", fill="#00ffcc", anchor="w", font=("Consolas", 9, "bold"))
        
        # Simulated metrics bars
        metrics = [("CPU LPU LOAD", 0.42), ("RAM ALLOCATION", 0.68), ("CORE SYNC", 0.95)]
        y = 35
        for label, val in metrics:
            self.create_text(15, y, text=label, fill="#8a99ad", anchor="w", font=("Consolas", 8))
            # Bar background
            self.create_rectangle(15, y + 10, self.width - 15, y + 16, fill="#161e2e", outline="")
            # Bar fill
            fill_width = int((self.width - 30) * val)
            self.create_rectangle(15, y + 10, 15 + fill_width, y + 16, fill="#00ffcc", outline="")
            y += 26