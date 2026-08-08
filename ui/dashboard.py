import tkinter as tk
from ui.hud_widgets import HexagonGauge, CyberOscilloscope, StorageDiagnosticsPanel

class HermesDashboard:
    def __init__(self, command_callback=None):
        self.command_callback = command_callback
        self.root = tk.Tk()
        self.root.title("HERMES // OS HOLOGRAPHIC HUD")
        self.root.geometry("950x680")
        self.root.configure(bg="#0b0f19")
        
        # Top Header Banner
        header_frame = tk.Frame(self.root, bg="#0b0f19", height=50)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        title_label = tk.Label(header_frame, text="PROMETHEUS CORE // OPERATING SYSTEM HUD", fg="#00ffcc", bg="#0b0f19", font=("Consolas", 14, "bold"))
        title_label.pack(side="left")
        
        self.status_label = tk.Label(header_frame, text="[ONLINE - READY]", fg="#00ffcc", bg="#0b0f19", font=("Consolas", 10, "bold"))
        self.status_label.pack(side="right")

        # Main Workspace Split Frame
        main_frame = tk.Frame(self.root, bg="#0b0f19")
        main_frame.pack(fill="both", expand=True, padx=20, pady=5)

        # Left Column: Diagnostics & Gauges
        left_col = tk.Frame(main_frame, bg="#0b0f19")
        left_col.pack(side="left", fill="y", padx=10)

        self.gauge1 = HexagonGauge(left_col, title="GROQ LPU")
        self.gauge1.pack(pady=5)
        
        self.storage_panel = StorageDiagnosticsPanel(left_col)
        self.storage_panel.pack(pady=10)

        # Right Column: Audio & Terminal Log Feed
        right_col = tk.Frame(main_frame, bg="#0b0f19")
        right_col.pack(side="right", fill="both", expand=True, padx=10)

        audio_label = tk.Label(right_col, text="AUDIO STREAM OSCILLOSCOPE", fg="#8a99ad", bg="#0b0f19", font=("Consolas", 9))
        audio_label.pack(anchor="w")
        
        self.oscilloscope = CyberOscilloscope(right_col, width=550, height=80)
        self.oscilloscope.pack(pady=5)

        # Terminal Text Activity Output
        log_label = tk.Label(right_col, text="SYSTEM EVENT LOG", fg="#8a99ad", bg="#0b0f19", font=("Consolas", 9))
        log_label.pack(anchor="w", pady=(5, 0))

        self.log_box = tk.Text(right_col, bg="#070a12", fg="#00ffcc", font=("Consolas", 9), highlightthickness=0, bd=0)
        self.log_box.pack(fill="both", expand=True, pady=5)
        self.log_box.insert("end", "[HUD Core]: Initialized successfully. Command prompt active.\n")

        # -------------------------------------------------------------
        # ⌨️ COMMAND INPUT PROMPT PANEL (Bottom Bar)
        # -------------------------------------------------------------
        input_frame = tk.Frame(self.root, bg="#0b0f19")
        input_frame.pack(fill="x", padx=20, pady=(0, 15))

        prompt_label = tk.Label(input_frame, text="OPERATOR >", fg="#00ffcc", bg="#0b0f19", font=("Consolas", 10, "bold"))
        prompt_label.pack(side="left", padx=(0, 8))

        self.cmd_entry = tk.Entry(input_frame, bg="#111827", fg="#00ffcc", insertbackground="#00ffcc", font=("Consolas", 11), relief="flat", highlightthickness=1, highlightbackground="#1f293d", highlightcolor="#00ffcc")
        self.cmd_entry.pack(side="left", fill="x", expand=True, ipadx=5, ipady=5)  # 👈 Fully corrected parameters
        self.cmd_entry.bind("<Return>", self._on_submit)

        submit_btn = tk.Button(input_frame, text="TRANSMIT", bg="#162032", fg="#00ffcc", activebackground="#00ffcc", activeforeground="#0b0f19", font=("Consolas", 9, "bold"), relief="flat", padx=12, pady=5, command=self._on_submit)
        submit_btn.pack(side="right", padx=(8, 0))

    def _on_submit(self, event=None):
        """Captures typed text and sends it to the command processor callback."""
        cmd = self.cmd_entry.get().strip()
        if cmd:
            self.cmd_entry.delete(0, tk.END)
            if self.command_callback:
                self.command_callback(cmd)

    def log(self, message: str):
        """Thread-safe logging method for background worker threads."""
        def _update():
            self.log_box.insert("end", f"{message}\n")
            self.log_box.see("end")
        try:
            self.root.after(0, _update)
        except Exception:
            pass

    def set_voice_state(self, state: str, description: str = ""):
        """Thread-safe voice state badge updater."""
        def _update_status():
            color_map = {
                "LISTENING": "#00ffcc",
                "PROCESSING": "#ffaa00",
                "SPEAKING": "#00aaff",
                "IDLE": "#8a99ad"
            }
            fg_color = color_map.get(state.upper(), "#00ffcc")
            self.status_label.config(text=f"[{state}: {description}]", fg=fg_color)
        try:
            self.root.after(0, _update_status)
        except Exception:
            pass

    def showFullScreen(self):
        is_full = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_full)

    def hide(self):
        self.root.withdraw()

    def show(self):
        self.root.deiconify()

    def run(self):
        self.root.mainloop()