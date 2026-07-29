import math
import random
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont


class ArcReactorCore(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rot_1 = 0.0
        self.rot_2 = 0.0
        self.rot_3 = 0.0
        self.pulse = 0.0
        self.state = "LISTENING"

        self.particles = [
            {"a": random.uniform(0, 6.28), "r": random.uniform(40, 220), "s": random.uniform(0.01, 0.03)}
            for _ in range(80)
        ]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

    def set_state(self, new_state):
        self.state = new_state.upper()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2

        self.rot_1 += 0.01
        self.rot_2 -= 0.02
        self.rot_3 += 0.03
        self.pulse += 0.05

        cyan = QColor(0, 240, 255)
        gold = QColor(255, 170, 0)
        green = QColor(0, 255, 136)

        color = cyan if self.state == "LISTENING" else (gold if self.state == "PROCESSING" else green)

        # 1. Outer Target Reticle Rings
        r_max = min(cx, cy) - 20
        if r_max < 30:
            return

        painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 100), 1, Qt.DashLine))
        painter.drawEllipse(QPointF(cx, cy), r_max, r_max)

        # 2. Rotating Radial Ticks
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(math.degrees(self.rot_1))
        painter.setPen(QPen(color, 2))
        for i in range(48):
            len_tick = 18 if i % 4 == 0 else 8
            painter.drawLine(int(r_max - len_tick), 0, int(r_max), 0)
            painter.rotate(7.5)
        painter.restore()

        # 3. Inner Tech Ring (FIXED: Cast start_angle and span_angle to int)
        r_mid = r_max - 40
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(math.degrees(self.rot_2))
        painter.setPen(QPen(color, 3))
        for i in range(16):
            start_angle = int(i * 22.5 * 16)
            span_angle = int(12 * 16)
            painter.drawArc(
                int(-r_mid), 
                int(-r_mid), 
                int(r_mid * 2), 
                int(r_mid * 2), 
                start_angle, 
                span_angle
            )
        painter.restore()

        # 4. Floating HUD Particles
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 60)))
        for p in self.particles:
            p["a"] += p["s"]
            px = cx + p["r"] * math.cos(p["a"])
            py = cy + p["r"] * math.sin(p["a"])
            painter.drawEllipse(QPointF(px, py), 2, 2)

        # 5. Core Pulse Circle
        pulse_r = 30 + math.sin(self.pulse) * 8
        painter.setPen(QPen(color, 2))
        painter.drawEllipse(QPointF(cx, cy), pulse_r, pulse_r)
        painter.drawEllipse(QPointF(cx, cy), 10, 10)