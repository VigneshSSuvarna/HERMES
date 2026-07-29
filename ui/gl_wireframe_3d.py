import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont


class Holographic3DWireframe(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0

        # Golden ratio for Icosphere geometry
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        self.base_vertices = [
            [-1,  phi,  0], [ 1,  phi,  0], [-1, -phi,  0], [ 1, -phi,  0],
            [ 0, -1,  phi], [ 0,  1,  phi], [ 0, -1, -phi], [ 0,  1, -phi],
            [ phi,  0, -1], [ phi,  0,  1], [-phi,  0, -1], [-phi,  0,  1]
        ]
        self.edges = [
            (0, 11), (0, 5), (0, 1), (0, 7), (0, 10), (3, 9), (3, 4), (3, 8), (3, 6), (3, 2),
            (2, 6), (2, 10), (2, 4), (9, 5), (9, 1), (9, 4), (8, 7), (8, 1), (8, 6), (5, 4),
            (11, 5), (11, 10), (11, 4), (7, 10), (7, 1)
        ]

        # 60 FPS Animation Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_rotation)
        self.timer.start(16)

    def update_rotation(self):
        self.angle_x += 0.015
        self.angle_y += 0.025
        self.angle_z += 0.010
        self.update()

    def _rotate_3d(self, x, y, z):
        # Rotate around X-axis
        rad_x = self.angle_x
        y1 = y * math.cos(rad_x) - z * math.sin(rad_x)
        z1 = y * math.sin(rad_x) + z * math.cos(rad_x)
        x1 = x

        # Rotate around Y-axis
        rad_y = self.angle_y
        x2 = x1 * math.cos(rad_y) + z1 * math.sin(rad_y)
        z2 = -x1 * math.sin(rad_y) + z1 * math.cos(rad_y)
        y2 = y1

        # Rotate around Z-axis
        rad_z = self.angle_z
        x3 = x2 * math.cos(rad_z) - y2 * math.sin(rad_z)
        y3 = x2 * math.sin(rad_z) + y2 * math.cos(rad_z)
        z3 = z2

        return x3, y3, z3

    def _project(self, x, y, z, cx, cy, scale):
        distance = 4.0
        perspective = distance / (distance + z * 0.5)
        px = cx + x * scale * perspective
        py = cy + y * scale * perspective
        return QPointF(px, py)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        scale = min(cx, cy) * 0.45

        if scale < 10:
            return

        # Background Container Outline & Title
        painter.setPen(QPen(QColor(0, 240, 255, 120), 1))
        painter.drawRect(2, 2, w - 4, h - 4)
        painter.setFont(QFont("Consolas", 9, QFont.Bold))
        painter.setPen(QPen(QColor(0, 240, 255)))
        painter.drawText(10, 20, "[ 3D HOLOGRAPHIC CORE MATRIX ]")

        # Outer Cyan Wireframe Sphere
        painter.setPen(QPen(QColor(0, 240, 255, 200), 2))
        rotated_outer = [self._rotate_3d(v[0] * 0.8, v[1] * 0.8, v[2] * 0.8) for v in self.base_vertices]
        projected_outer = [self._project(v[0], v[1], v[2], cx, cy, scale) for v in rotated_outer]

        for p1_idx, p2_idx in self.edges:
            painter.drawLine(projected_outer[p1_idx], projected_outer[p2_idx])

        # Inner Gold Concentric Core Wireframe
        painter.setPen(QPen(QColor(255, 170, 0, 180), 1))
        rotated_inner = [self._rotate_3d(-v[0] * 0.4, -v[1] * 0.4, -v[2] * 0.4) for v in self.base_vertices]
        projected_inner = [self._project(v[0], v[1], v[2], cx, cy, scale) for v in rotated_inner]

        for p1_idx, p2_idx in self.edges:
            painter.drawLine(projected_inner[p1_idx], projected_inner[p2_idx])