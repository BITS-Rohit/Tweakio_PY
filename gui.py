import os
import queue  # thread-safe communication
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# --- CONFIGURATION ---
ENV_FILE = ".env"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_TO_RUN = os.path.join(BASE_DIR, "Start.py")
LOGOUT_DIR = os.path.join(BASE_DIR, "Whatsapp", "Wa_Session")


# --- COLOR PALETTE ---
COLORS = {
    "bg_main": "#1e1e1e",
    "bg_sec":  "#252526",
    "fg_text": "#d4d4d4",
    "accent":  "#007acc",
    "success": "#4caf50",
    "danger":  "#f44336",
    "warning": "#ff9800",
    "input_bg": "#3c3c3c",
    "input_fg": "#ffffff",
    "border":  "#3e3e42"
}

class ScrollableFrame(ttk.Frame):
    """A helper class to make a scrollable frame that fills width."""
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0, bg=COLORS["bg_sec"])
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="Card.TFrame")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

class EnvManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Environment Manager")
        self.root.geometry("750x850") # Increased height for log box
        self.root.configure(bg=COLORS["bg_main"])

        # --- STYLE KA ENGINE ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background=COLORS["bg_main"], foreground=COLORS["fg_text"], font=("Segoe UI", 10))
        self.style.configure('TEntry', fieldbackground=COLORS["input_bg"], foreground=COLORS["input_fg"], bordercolor=COLORS["border"], lightcolor=COLORS["border"], darkcolor=COLORS["border"])
        self.style.configure('TLabelframe', background=COLORS["bg_sec"], bordercolor=COLORS["border"])
        self.style.configure('TLabelframe.Label', background=COLORS["bg_sec"], foreground=COLORS["accent"], font=("Segoe UI", 11, "bold"))
        self.style.configure('TButton', background=COLORS["bg_sec"], foreground=COLORS["fg_text"], borderwidth=1, bordercolor=COLORS["border"], focuscolor="none")
        self.style.map('TButton', background=[('active', '#3e3e42'), ('disabled', COLORS["bg_sec"])], foreground=[('active', 'white'), ('disabled', '#666666')])
        
        # Colored Buttons
        self.style.configure('Action.TButton', background=COLORS["accent"], foreground="white", borderwidth=0)
        self.style.map('Action.TButton', background=[('active', '#0098ff')])
        self.style.configure('Save.TButton', background=COLORS["success"], foreground="white", borderwidth=0)
        self.style.map('Save.TButton', background=[('active', '#66bb6a')])
        self.style.configure('Stop.TButton', background=COLORS["danger"], foreground="white", borderwidth=0)
        self.style.map('Stop.TButton', background=[('active', '#ff7961')])
        self.style.configure('Warning.TButton', background=COLORS["warning"], foreground="black", borderwidth=0)
        self.style.map('Warning.TButton', background=[('active', '#ffb74d')])
        self.style.configure('Card.TFrame', background=COLORS["bg_sec"])

        # --- LOGIC KI SHURUAT ---
        self.entries = {}
        self.process = None
        self.log_queue = queue.Queue() # Queue to hold log messages

        # --- GUI KA NIRMAN ---
        main_pad = ttk.Frame(root, padding="25")
        main_pad.pack(fill="both", expand=True)

        # HEADER SECTION
        header_frame = ttk.Frame(main_pad)
        header_frame.pack(fill="x", pady=(0, 15))
        ttk.Label(header_frame, text=f"TweakioPY WAAI", font=("Segoe UI", 14, "bold"), foreground="white").pack(side="left")
        ttk.Button(header_frame, text="✖ Close App", command=self.on_close, style="Stop.TButton").pack(side="right")
        self.btn_logout = ttk.Button(header_frame, text="⚠ Logout", command=self.logout_session, style="Warning.TButton")
        self.btn_logout.pack(side="right", padx=(0, 10))

        # EDITOR SECTION
        editor_card = ttk.LabelFrame(main_pad, text=" Configuration ", padding="15")
        editor_card.pack(fill="both", expand=True, pady=(0, 20))
        self.body = ScrollableFrame(editor_card)
        self.body.pack(fill="both", expand=True)
        
        controls_frame = ttk.Frame(editor_card, style='Card.TFrame')
        controls_frame.pack(fill="x", pady=(15, 0))
        ttk.Button(controls_frame, text="⟳ Reload", command=self.load_env_file).pack(side="left")
        ttk.Button(controls_frame, text="Save Changes", command=self.save_env_file, style="Save.TButton").pack(side="right")

        # RUNNER SECTION
        runner_card = ttk.LabelFrame(main_pad, text=" Process Control ", padding="15")
        runner_card.pack(fill="x")
        runner_card.columnconfigure(1, weight=1)
        self.status_indicator = ttk.Label(runner_card, text="●", font=("Arial", 16), foreground=COLORS["danger"], background=COLORS["bg_sec"])
        self.status_indicator.grid(row=0, column=0, padx=(0, 10))
        self.status_text = ttk.Label(runner_card, text="Stopped", font=("Segoe UI", 11), background=COLORS["bg_sec"])
        self.status_text.grid(row=0, column=1, sticky="w")
        self.btn_run = ttk.Button(runner_card, text="▶ Start Script", command=self.toggle_script, style="Action.TButton")
        self.btn_run.grid(row=0, column=2)

        # --- LOGS SECTION (NEW) ---
        logs_card = ttk.LabelFrame(main_pad, text=" Console Output ", padding="10")
        logs_card.pack(fill="x", pady=(20, 0))
        
        # We use a standard tk.Text widget because ttk doesn't have a multi-line text input
        # We manually style it to match the theme
        self.log_text = tk.Text(logs_card, height=10, state="disabled", 
                                bg=COLORS["input_bg"], fg=COLORS["fg_text"],
                                insertbackground="white", # Cursor color
                                borderwidth=0, highlightthickness=0,
                                font=("Consolas", 9))
        self.log_text.pack(side="left", fill="both", expand=True)
        
        log_scroll = ttk.Scrollbar(logs_card, orient="vertical", command=self.log_text.yview)
        log_scroll.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=log_scroll.set)

        # Events
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_env_file()
        
        # Start the loop that watches for new logs
        self.check_log_queue()

    def check_log_queue(self):
        """Checks the queue for new output lines and updates the GUI."""
        while not self.log_queue.empty():
            line = self.log_queue.get_nowait()
            self.log_text.config(state="normal") # Enable editing to append
            self.log_text.insert("end", line)
            self.log_text.see("end") # Auto-scroll to bottom
            self.log_text.config(state="disabled") # Disable editing again
        
        # Schedule next check in 100ms
        self.root.after(100, self.check_log_queue)

    def reader_thread(self, process):
        """Runs in a background thread to read process output."""
        try:
            # Iterates over stdout as lines are produced
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.log_queue.put(line)
                else:
                    break
        except Exception:
            pass
        finally:
            process.stdout.close()

    def load_env_file(self):
        for widget in self.body.scrollable_frame.winfo_children(): widget.destroy()
        self.entries = {}
        if not os.path.exists(ENV_FILE):
            ttk.Label(self.body.scrollable_frame, text="File not found.", foreground="red").pack()
            return
        try:
            with open(ENV_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"): continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        row = ttk.Frame(self.body.scrollable_frame, style='Card.TFrame')
                        row.pack(fill="x", pady=4)
                        ttk.Label(row, text=key, width=22, font=("Consolas", 10), background=COLORS["bg_sec"], foreground=COLORS["accent"]).pack(side="left")
                        entry = ttk.Entry(row)
                        entry.insert(0, value)
                        entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
                        self.entries[key] = entry
        except Exception as e: messagebox.showerror("Error", str(e))

    def save_env_file(self):
        try:
            with open(ENV_FILE, "w") as f:
                for key, entry in self.entries.items(): f.write(f"{key}={entry.get()}\n")
            messagebox.showinfo("Saved", "Configuration updated successfully.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def logout_session(self):
        if not os.path.exists(LOGOUT_DIR):
            messagebox.showinfo("Logout", "No active session found.")
            return
        if messagebox.askyesno("Confirm Logout", f"Delete session data?\n\nTarget: {LOGOUT_DIR}"):
            try:
                shutil.rmtree(LOGOUT_DIR)
                messagebox.showinfo("Success", "Session cleared.")
            except Exception as e: messagebox.showerror("Error", str(e))

    def toggle_script(self):
        if self.process is None:
            # START
            if not os.path.exists(SCRIPT_TO_RUN):
                messagebox.showerror("Error", f"{SCRIPT_TO_RUN} missing.")
                return
            try:
                # Capture output (stdout) and errors (stderr)
                # bufsize=1 means line-buffered (updates immediately)
                self.process = subprocess.Popen(
                    [sys.executable, SCRIPT_TO_RUN],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, 
                    text=True,
                    bufsize=1
                )
                
                # Start background thread to read output
                t = threading.Thread(target=self.reader_thread, args=(self.process,), daemon=True)
                t.start()
                
                self.btn_run.config(text="■ Stop Script", style="Stop.TButton")
                self.status_indicator.config(foreground=COLORS["success"])
                self.status_text.config(text=f"Running (PID: {self.process.pid})", foreground=COLORS["success"])
                self.btn_logout.config(state="disabled")
                
                # Add separator in logs
                self.log_queue.put(f"--- Started {SCRIPT_TO_RUN} ---\n")
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            # STOP
            self.process.terminate()
            self.process = None
            
            self.btn_run.config(text="▶ Start Script", style="Action.TButton")
            self.status_indicator.config(foreground=COLORS["danger"])
            self.status_text.config(text="Stopped", foreground=COLORS["fg_text"])
            self.btn_logout.config(state="normal")
            
            self.log_queue.put("--- Script Stopped ---\n")

    def on_close(self):
        if self.process: self.process.kill()
        self.root.destroy()

if __name__ == "__main__":
    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, "w") as f: f.write("API_KEY=12345\nDB_HOST=localhost\nDEBUG=True")
    if not os.path.exists(SCRIPT_TO_RUN):
        with open(SCRIPT_TO_RUN, "w") as f: f.write("import time\nprint('Worker started...')\nwhile True:\n    print('Working...'); time.sleep(1)")
    dummy_session = os.path.join(".", "Whatsapp", "Wa_Session")
    if not os.path.exists(dummy_session): os.makedirs(dummy_session)

    root = tk.Tk()
    app = EnvManagerApp(root)
    root.mainloop()