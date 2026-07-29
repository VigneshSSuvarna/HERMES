import math
import random
import cv2
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import QTimer, Qt, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPolygonF, QFont
from PyQt5.QtGui import QImage, QPixmap 

class HexagonGauge(QFrame):
    """Custom Hexagonal Vector Telemetry Gauge for CPU & RAM."""
    def __init__(self, title="CPU", unit="%", subtext="", parent=None):
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.subtext = subtext
        self.value = 0.0
        self.setMinimumSize(160, 140)

    def set_value(self, val, sub_val=""):
        self.value = val
        if sub_val:
            self.subtext = sub_val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        r = min(cx, cy) - 12

        # Hexagon Vertices Calculation
        pts = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.radians(angle_deg)
            px = cx + r * math.cos(angle_rad)
            py = cy + r * math.sin(angle_rad)
            pts.append(QPointF(px, py))

        hex_poly = QPolygonF(pts)

        # Draw Outer Hexagon Glow
        painter.setPen(QPen(QColor(0, 240, 255, 60), 6))
        painter.drawPolygon(hex_poly)

        # Draw Inner Double Frame
        painter.setPen(QPen(QColor(0, 240, 255, 220), 2))
        painter.drawPolygon(hex_poly)

        # Draw Text Content
        painter.setFont(QFont("Consolas", 10, QFont.Bold))
        painter.setPen(QPen(QColor(0, 240, 255)))
        painter.drawText(0, int(cy - 28), w, 20, Qt.AlignCenter, self.title)

        painter.setFont(QFont("Consolas", 18, QFont.Bold))
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.drawText(0, int(cy - 6), w, 28, Qt.AlignCenter, f"{self.value:.1f}{self.unit}")

        if self.subtext:
            painter.setFont(QFont("Consolas", 9, QFont.Bold))
            painter.setPen(QPen(QColor(0, 240, 255, 180)))
            painter.drawText(0, int(cy + 22), w, 20, Qt.AlignCenter, self.subtext)


class CyberOscilloscope(QFrame):
    """Live Green Audio Waveform Analyzer."""
    def __init__(self, title="SIGNAL OSCILLOSCOPE", parent=None):
        super().__init__(parent)
        self.title = title
        self.phase = 0.0
        self.setStyleSheet("background-color: rgba(4, 10, 20, 230); border: 1px solid #00f0ff;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(30)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        self.phase += 0.15

        # Header Title
        painter.setFont(QFont("Consolas", 9, QFont.Bold))
        painter.setPen(QPen(QColor(0, 240, 255)))
        painter.drawText(10, 18, f"[ {self.title} ]")

        # Grid Background
        painter.setPen(QPen(QColor(0, 240, 255, 20), 1, Qt.DotLine))
        for x in range(0, w, 20):
            painter.drawLine(x, 25, x, h)
        for y in range(25, h, 15):
            painter.drawLine(0, y, w, y)

        # Green Waveform Line
        painter.setPen(QPen(QColor(0, 255, 136), 2))
        cy = 25 + (h - 25) / 2
        pts = []

        for x in range(10, w - 10, 3):
            y = cy + math.sin(x * 0.05 + self.phase) * 16 + random.uniform(-3, 3)
            pts.append(QPointF(x, y))

        for i in range(len(pts) - 1):
            painter.drawLine(pts[i], pts[i + 1])

        # Subtext Footer
        painter.setFont(QFont("Consolas", 8, QFont.Bold))
        painter.setPen(QPen(QColor(0, 240, 255, 180)))
        painter.drawText(10, h - 8, "AUDIO LOGIC FEED // FREQ 44.1kHz")


class StorageDiagnosticsPanel(QFrame):
    """Top-Right Storage Drives & System Status Monitor."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(4, 10, 20, 230); border: 1px solid #00f0ff;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Storage Section
        drive_box = QVBoxLayout()
        lbl_drive_title = QLabel("[ STORAGE DRIVES ]")
        lbl_drive_title.setFont(QFont("Consolas", 9, QFont.Bold))
        lbl_drive_title.setStyleSheet("color: #00f0ff; border: none;")
        drive_box.addWidget(lbl_drive_title)

        self.lbl_c = QLabel("DRIVE C: 00%")
        self.lbl_c.setFont(QFont("Consolas", 10, QFont.Bold))
        self.lbl_c.setStyleSheet("color: #ffffff; border: none;")
        drive_box.addWidget(self.lbl_c)

        self.bar_c = QProgressBar()
        self.bar_c.setFixedHeight(6)
        self.bar_c.setTextVisible(False)
        self.bar_c.setStyleSheet("QProgressBar{background:#02050a; border:1px solid #00f0ff;} QProgressBar::chunk{background:#00f0ff;}")
        drive_box.addWidget(self.bar_c)

        layout.addLayout(drive_box, 2)

        # Diagnostics Status Box
        diag_box = QVBoxLayout()
        lbl_diag_title = QLabel("[ SYSTEM DIAGNOSTICS ]")
        lbl_diag_title.setFont(QFont("Consolas", 9, QFont.Bold))
        lbl_diag_title.setStyleSheet("color: #00f0ff; border: none;")
        diag_box.addWidget(lbl_diag_title)

        self.lbl_status = QLabel("NOMINAL")
        self.lbl_status.setFont(QFont("Consolas", 16, QFont.Bold))
        self.lbl_status.setStyleSheet("color: #00ff88; border: none;")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        diag_box.addWidget(self.lbl_status)

        layout.addLayout(diag_box, 1)

    def set_storage_data(self, percent):
        self.lbl_c.setText(f"DRIVE C: {int(percent)}%")
        self.bar_c.setValue(int(percent))


class LiveVisionFeed(QFrame):
    """Real-Time Webcam Vision Feed for the HUD."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(4, 10, 20, 230); border: 1px solid #00f0ff;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        self.lbl_title = QLabel("[ SENSORY VISION FEED ]")
        self.lbl_title.setFont(QFont("Consolas", 9, QFont.Bold))
        self.lbl_title.setStyleSheet("color: #00f0ff; border: none;")
        layout.addWidget(self.lbl_title)
        
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("border: none; background-color: #000;")
        layout.addWidget(self.video_label, 1)
        
        # Initialize Webcam (0 is usually the default laptop/USB camera)
        self.cap = cv2.VideoCapture(0)
        
        # Timer to fetch frames at 30 FPS
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(33)

    def update_frame(self):
        """Fetches a frame from the webcam and converts it to a PyQt Image."""
        ret, frame = self.cap.read()
        if ret:
            # Flip horizontally for a mirror effect (optional)
            frame = cv2.flip(frame, 1)
            
            # Convert OpenCV BGR format to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Scale the image to fit the HUD box perfectly
            scaled_pixmap = QPixmap.fromImage(q_img).scaled(
                self.video_label.width(), self.video_label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.video_label.setPixmap(scaled_pixmap)

    def stop_feed(self):
        """Safely release the camera when closing the app."""
        self.timer.stop()
        if self.cap.isOpened():
            self.cap.release()