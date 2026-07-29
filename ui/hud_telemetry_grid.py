import math
import random
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont


class CyberOscilloscope(QFrame):
    def __init__(self, title="SIGNAL MATRIX", parent=None):
        super().__init__(parent)
        self.title = title
        self.phase = 0
        self.setStyleSheet("background-color: rgba(2, 6, 14, 230); border: 1px solid #00f0ff;")
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(30)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        self.phase += 0.15

        # Draw Title
        painter.setFont(QFont("Consolas", 9, QFont.Bold))
        painter.setPen(QPen(QColor(0, 240, 255)))
        painter.drawText(10, 18, f"[ {self.title} ]")

        # Draw Background Grid
        painter.setPen(QPen(QColor(0, 240, 255, 20), 1, Qt.DotLine))
        for x in range(0, w, 20):
            painter.drawLine(x, 25, x, h)
        for y in range(25, h, 15):
            painter.drawLine(0, y, w, y)

        # Draw Dynamic Sine Waveform Line
        painter.setPen(QPen(QColor(0, 255, 136), 2))
        cy = 25 + (h - 25) / 2
        
        pts = []
        for x in range(10, w - 10, 3):
            y = cy + math.sin(x * 0.05 + self.phase) * 15 + random.uniform(-2, 2)
            pts.append(QPointF(x, y))

        for i in range(len(pts) - 1):
            painter.drawLine(pts[i], pts[i + 1])


class DiagnosticGaugePanel(QFrame):
    def __init__(self, title="DIAGNOSTIC", parent=None):
        super().__init__(parent)
        self.title = title
        self.val = 50
        self.setStyleSheet("background-color: rgba(2, 6, 14, 230); border: 1px solid #00f0ff;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        self.lbl_title = QLabel(f"[ {self.title} ]")
        self.lbl_title.setFont(QFont("Consolas", 9, QFont.Bold))
        self.lbl_title.setStyleSheet("color: #00f0ff; border: none;")
        layout.addWidget(self.lbl_title)

        self.lbl_val = QLabel("LOAD: 00.0%")
        self.lbl_val.setFont(QFont("Consolas", 14, QFont.Bold))
        self.lbl_val.setStyleSheet("color: #ffffff; border: none;")
        layout.addWidget(self.lbl_val)

    def set_value(self, val):
        self.val = val
        self.lbl_val.setText(f"LOAD: {val:.1f}%")