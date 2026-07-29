import math
import random
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont


class CentralArcReactor(QWidget):
    """Concentric Multi-Ring Arc Reactor with Sector Labels."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rot_outer = 0.0
        self.rot_mid = 0.0
        self.rot_inner = 0.0
        self.pulse = 0.0
        self.state = "LISTENING"

        self.particles = [
            {"a": random.uniform(0, 6.28), "r": random.uniform(40, 220), "s": random.uniform(0.01, 0.03)}
            for _ in range(70)
        ]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # 60 FPS

    def set_state(self, state):
        self.state = state.upper()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2

        self.rot_outer += 0.008
        self.rot_mid -= 0.018
        self.rot_inner += 0.025
        self.pulse += 0.05

        cyan = QColor(0, 240, 255)
        gold = QColor(255, 170, 0)
        green = QColor(0, 255, 136)

        primary_color = cyan if self.state == "LISTENING" else (gold if self.state == "PROCESSING" else green)

        # Outer Reticle Boundary
        r_max = min(cx, cy) - 25
        if r_max < 30:
            return

        # 1. Outer Tick Ring
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(math.degrees(self.rot_outer))
        painter.setPen(QPen(primary_color, 2))

        for i in range(60):
            tick_len = 14 if i % 5 == 0 else 6
            painter.drawLine(int(r_max - tick_len), 0, int(r_max), 0)
            painter.rotate(6)
        painter.restore()

        # 2. Gold Sector Arc Outer Ring
        r_gold = r_max - 20
        painter.setPen(QPen(QColor(255, 170, 0, 220), 2))
        painter.drawEllipse(QPointF(cx, cy), r_gold, r_gold)

        # 3. Rotating Tech Arc Ring (Integer Angles to Prevent PyQt Crashes)
        r_tech = r_gold - 30
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(math.degrees(self.rot_mid))
        painter.setPen(QPen(primary_color, 3))

        for i in range(12):
            start_angle = int(i * 30 * 16)
            span_angle = int(18 * 16)
            painter.drawArc(int(-r_tech), int(-r_tech), int(r_tech * 2), int(r_tech * 2), start_angle, span_angle)
        painter.restore()

        # 4. Floating Holographic Particles
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 70)))
        for p in self.particles:
            p["a"] += p["s"]
            px = cx + p["r"] * math.cos(p["a"])
            py = cy + p["r"] * math.sin(p["a"])
            painter.drawEllipse(QPointF(px, py), 2, 2)

        # 5. Inner Core Target Reticle
        r_core = 40 + math.sin(self.pulse) * 6
        painter.setPen(QPen(primary_color, 2))
        painter.drawEllipse(QPointF(cx, cy), r_core, r_core)
        painter.drawEllipse(QPointF(cx, cy), 12, 12)

        # Crosshairs
        painter.setPen(QPen(QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 140), 1, Qt.DashLine))
        painter.drawLine(int(cx - r_gold), int(cy), int(cx + r_gold), int(cy))
        painter.drawLine(int(cx), int(cy - r_gold), int(cx), int(cy + r_gold))

        # 6. Sector Text Overlays
        painter.setFont(QFont("Consolas", 8, QFont.Bold))
        painter.setPen(QPen(primary_color))
        painter.drawText(int(cx - 80), int(cy - r_tech + 18), 160, 20, Qt.AlignCenter, "SYSTEM SYNC")
        painter.drawText(int(cx - 80), int(cy + r_tech - 30), 160, 20, Qt.AlignCenter, "NEURAL MATRIX")