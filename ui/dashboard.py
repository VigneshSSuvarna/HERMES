import sys
import psutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, 
    QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QGridLayout, QFrame
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont

# Importing the Core UI Modules
from ui.hud_core import CentralArcReactor
from ui.hud_widgets import HexagonGauge, CyberOscilloscope, StorageDiagnosticsPanel, LiveVisionFeed
from PyQt5.QtCore import pyqtSignal, QObject

class DashboardSignals(QObject):
    log_signal = pyqtSignal(str)
    state_signal = pyqtSignal(str, str) # (state_name, subtitle)

class HermesDashboard(QMainWindow):
    def __init__(self, command_callback=None):
        super().__init__()
        self.command_callback = command_callback
        self.signals = DashboardSignals()
        
        # Connect signals to UI update slots safely on the main thread
        self.signals.log_signal.connect(self._append_log)
        self.signals.state_signal.connect(self._update_state_ui)
        
        self.init_ui()
    def log(self, message: str):
        # Thread-safe log method callable from any background thread
        self.signals.log_signal.emit(message)

    def set_voice_state(self, state: str, subtitle: str = ""):
        # Thread-safe state update method
        self.signals.state_signal.emit(state, subtitle)

    def _append_log(self, message: str):
        # Actual UI update running on the main PyQt thread
        self.console_text.append(message)
        # Auto-scroll to bottom
        self.console_text.verticalScrollBar().setValue(
            self.console_text.verticalScrollBar().maximum()
        )

    def _update_state_ui(self, state: str, subtitle: str):
        # Visual state machine rendering (glow, colors, waveforms)
        if state == "LISTENING":
            self.status_display.setStyleSheet("color: #00ffc8; border: 1px solid #00ffc8;")
            self.status_display.setText("LISTENING [ACTIVE]")
        elif state == "PROCESSING":
            self.status_display.setStyleSheet("color: #ffa500; border: 1px solid #ffa500;")
            self.status_display.setText("PROCESSING NEURAL COMMAND...")
        elif state == "SPEAKING":
            self.status_display.setStyleSheet("color: #00ff00; border: 1px solid #00ff00;")
            self.status_display.setText("TRANSMITTING SPEECH...")
        
        if subtitle:
            self.sub_display.setText(subtitle)

class LogBridge(QObject):
    log_signal = pyqtSignal(str)
    state_signal = pyqtSignal(str)


class HermesDashboard(QMainWindow):
    def __init__(self, command_callback=None):
        super().__init__()

        self.command_callback = command_callback
        self.bridge = LogBridge()
        self.bridge.log_signal.connect(self._append_log)
        self.bridge.state_signal.connect(self._update_state)

        # Fullscreen Zero-Void Configuration
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: #02060d;")

        self.keyPressEvent = self._handle_key
        
        # Build UI
        self._build_ui()

        # System Polling Loop
        self.telemetry_timer = QTimer(self)
        self.telemetry_timer.timeout.connect(self._poll_telemetry)
        self.telemetry_timer.start(1000)

    def _handle_key(self, event):
        if event.key() == Qt.Key_Escape:
            self._exit_system()

    def _exit_system(self):
        # Safely turn off webcam when exiting
        if hasattr(self, 'vision_box'):
            self.vision_box.stop_feed()
        QApplication.quit()

    def _build_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        root_layout = QVBoxLayout(main_widget)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(8)

        # --- TOP HEADER ---
        top_bar = QHBoxLayout()
        header_title = QLabel("HERMES // AI PYTHON DESKTOP COMMAND MATRIX")
        header_title.setFont(QFont("Consolas", 14, QFont.Bold))
        header_title.setStyleSheet("color: #00f0ff;")
        top_bar.addWidget(header_title)

        top_bar.addStretch()

        close_btn = QPushButton("✖ CLOSE [ESC]")
        close_btn.setFont(QFont("Consolas", 9, QFont.Bold))
        close_btn.setStyleSheet("background-color: #ff1e56; color: white; padding: 4px 12px; border-radius: 2px;")
        close_btn.clicked.connect(self._exit_system)
        top_bar.addWidget(close_btn)

        root_layout.addLayout(top_bar)

        # --- EDGE-TO-EDGE GRID ---
        grid = QGridLayout()
        grid.setSpacing(10)

        # COLUMN 0: Left Hex Telemetry & Oscilloscope
        left_hex_box = QHBoxLayout()
        self.hex_cpu = HexagonGauge(title="CPU", unit="%", subtext="FREQ 4.2GHz")
        self.hex_ram = HexagonGauge(title="RAM MATRIX", unit="%", subtext="ALLOC 10.3GB")
        left_hex_box.addWidget(self.hex_cpu)
        left_hex_box.addWidget(self.hex_ram)

        self.scope = CyberOscilloscope("SIGNAL OSCILLOSCOPE")

        grid.addLayout(left_hex_box, 0, 0, 2, 1)
        grid.addWidget(self.scope, 2, 0, 2, 1)

        # COLUMN 1: Central Multi-Ring Arc Reactor
        self.reactor = CentralArcReactor()
        grid.addWidget(self.reactor, 0, 1, 4, 1)

        # COLUMN 2: Storage, Vision Feed & Macros
        self.storage_panel = StorageDiagnosticsPanel()
        grid.addWidget(self.storage_panel, 0, 2)

        # Sensory Vision Preview Box (Live Webcam)
        self.vision_box = LiveVisionFeed()
        grid.addWidget(self.vision_box, 1, 2)

        # Quick Macros Grid
        macro_frame = QFrame()
        macro_frame.setStyleSheet("background-color: rgba(4, 10, 20, 230); border: 1px solid #00f0ff;")
        m_layout = QVBoxLayout(macro_frame)
        m_layout.setContentsMargins(8, 8, 8, 8)

        lbl_m_title = QLabel("[ TACTICAL QUICK MACROS ]")
        lbl_m_title.setFont(QFont("Consolas", 9, QFont.Bold))
        lbl_m_title.setStyleSheet("color: #00f0ff; border: none;")
        m_layout.addWidget(lbl_m_title)

        m_grid = QGridLayout()
        macros = [
            ("OPEN NOTEPAD", "open notepad"),
            ("CALCULATOR", "open calculator"),
            ("YOUTUBE", "open youtube"),
            ("SCREEN ANALYSIS", "screen"),
            ("EMERGENCY SHUTDOWN", "shutdown")
        ]

        for i, (label, cmd) in enumerate(macros):
            btn = QPushButton(label)
            btn.setFont(QFont("Consolas", 8, QFont.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #040a14;
                    color: #00f0ff;
                    border: 1px solid #00f0ff;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #00f0ff;
                    color: #000;
                }
            """)
            btn.clicked.connect(lambda checked, c=cmd: self._trigger_cmd(c))
            m_grid.addWidget(btn, i // 2, i % 2)

        m_layout.addLayout(m_grid)
        
        # FIXED: Correct addWidget call for QFrame
        grid.addWidget(macro_frame, 2, 2, 2, 1)

        # Add grid to root layout with stretch factor 5
        root_layout.addLayout(grid, 5)

        # --- BOTTOM TERMINAL FEED & COMMAND BAR ---
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont("Consolas", 10))
        self.terminal.setStyleSheet("background-color: #02050a; color: #00f0ff; border: 1px solid #005b66;")
        self.terminal.append("[HERMES HUD MATRIX ONLINE]")
        self.terminal.append("[DIRECT LISTENING ACTIVE // NO WAKE WORD]\n")
        root_layout.addWidget(self.terminal, 2)

        input_bar = QHBoxLayout()
        self.entry = QLineEdit()
        self.entry.setFont(QFont("Consolas", 11))
        self.entry.setPlaceholderText("Enter command override...")
        self.entry.setStyleSheet("background-color: #040810; color: #fff; border: 1px solid #00f0ff; padding: 6px;")
        self.entry.returnPressed.connect(self._on_enter)
        input_bar.addWidget(self.entry)

        send_btn = QPushButton("EXECUTE [↵]")
        send_btn.setFont(QFont("Consolas", 10, QFont.Bold))
        send_btn.setStyleSheet("background-color: #00f0ff; color: #000; padding: 6px 16px;")
        send_btn.clicked.connect(self._on_enter)
        input_bar.addWidget(send_btn)

        root_layout.addLayout(input_bar)

    def _poll_telemetry(self):
        cpu_val = psutil.cpu_percent()
        ram_val = psutil.virtual_memory().percent
        disk_val = psutil.disk_usage('/').percent

        self.hex_cpu.set_value(cpu_val)
        self.hex_ram.set_value(ram_val)
        self.storage_panel.set_storage_data(disk_val)

    def _trigger_cmd(self, cmd):
        self.log(f"[MACRO TRIGGERED]: {cmd}")
        if self.command_callback:
            self.command_callback(cmd)

    def _on_enter(self):
        text = self.entry.text().strip()
        if text:
            self.log(f"[OPERATOR]: {text}")
            self.entry.clear()
            if self.command_callback:
                self.command_callback(text)

    def log(self, text):
        self.bridge.log_signal.emit(text)

    def _append_log(self, text):
        self.terminal.append(text)

    def set_voice_state(self, state, subtext=""):
        self.bridge.state_signal.emit(state)

    def _update_state(self, state):
        self.reactor.set_state(state)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = HermesDashboard()
    sys.exit(app.exec_())