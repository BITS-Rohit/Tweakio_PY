"""Starting Point of the Program with Interface for easy usage"""
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
    "bg_sec": "#252526",
    "fg_text": "#d4d4d4",
    "accent": "#007acc",
    "success": "#4caf50",
    "danger": "#f44336",
    "warning": "#ff9800",
    "input_bg": "#3c3c3c",
    "input_fg": "#ffffff",
    "border": "#3e3e42"
}

class UndoEntry(tk.Entry):
    """A tk.Entry subclass that supports Ctrl+Z (Undo), Ctrl+Y (Redo) and Custom Styling."""
    def __init__(self, master=None, **kwargs):
        # --- Custom Styling for Visibility ---
        # Set default colors if not provided
        if 'bg' not in kwargs: kwargs['bg'] = COLORS["input_bg"]
        if 'fg' not in kwargs: kwargs['fg'] = COLORS["input_fg"]
        if 'insertbackground' not in kwargs: kwargs['insertbackground'] = COLORS["accent"] # Noticeable Cursor Color

        # Flat modern look with border
        if 'relief' not in kwargs: kwargs['relief'] = "flat"
        if 'highlightthickness' not in kwargs: kwargs['highlightthickness'] = 1
        if 'highlightbackground' not in kwargs: kwargs['highlightbackground'] = COLORS["border"]
        if 'highlightcolor' not in kwargs: kwargs['highlightcolor'] = COLORS["accent"]

        super().__init__(master, **kwargs)

        # Stack to store text states: [(text, cursor_position)]
        self._stack = [("", 0)]
        self._stack_index = 0
        self._is_undoing = False

        # Track changes via StringVar trace to catch typing, pasting, and deleting
        self.var = kwargs.get('textvariable', tk.StringVar())
        self.configure(textvariable=self.var)
        self.var.trace_add('write', self._on_change)

        # Bind Keys
        self.bind('<Control-z>', self.undo)
        self.bind('<Control-y>', self.redo)

    def _on_change(self, *args):
        """Called whenever the text variable changes."""
        if self._is_undoing:
            return

        current_text = self.var.get()

        # Don't save if it's identical to the current state
        if self._stack_index < len(self._stack):
            last_text, _ = self._stack[self._stack_index]
            if current_text == last_text:
                return

        # Truncate stack if branching from middle
        if self._stack_index < len(self._stack) - 1:
            self._stack = self._stack[:self._stack_index + 1]

        # Save new state
        self._stack.append((current_text, self.index(tk.INSERT)))
        self._stack_index += 1

        # Limit stack size
        if len(self._stack) > 100:
            self._stack.pop(0)
            self._stack_index -= 1

    def undo(self, event=None):
        """Perform Undo."""
        if self._stack_index > 0:
            self._is_undoing = True
            self._stack_index -= 1
            text, cursor = self._stack[self._stack_index]
            self.var.set(text)
            self.icursor(cursor)
            self._is_undoing = False
        return "break"

    def redo(self, event=None):
        """Perform Redo."""
        if self._stack_index < len(self._stack) - 1:
            self._is_undoing = True
            self._stack_index += 1
            text, cursor = self._stack[self._stack_index]
            self.var.set(text)
            self.icursor(cursor)
            self._is_undoing = False
        return "break"

class ScrollableFrame(ttk.Frame):
    """Scrollable frame: Vertical + Horizontal Scrollbars."""

    def __init__(self, container, *args, vbar_width=14, hbar_height=14, **kwargs):
        super().__init__(container, *args, **kwargs)

        # --- Layout grid ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Canvas
        self.canvas = tk.Canvas(self, bg=COLORS["bg_sec"], highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Vertical Scrollbar
        self.scroll_y = tk.Scrollbar(self, command=self.canvas.yview, width=vbar_width)
        self.scroll_y.grid(row=0, column=1, sticky="ns")

        # Horizontal Scrollbar
        self.scroll_x = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview, width=hbar_height)
        self.scroll_x.grid(row=1, column=0, sticky="ew")

        # Attach scrollbars
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        # Actual content frame inside canvas
        self.inner = ttk.Frame(self.canvas, style="Card.TFrame")

        # Create window with tags to find it later
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw", tags="inner_frame")

        # Bind events
        self.inner.bind("<Configure>", self._on_frame_resize)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self._bind_mousewheel(self.canvas)
        self._bind_mousewheel(self.inner)

    def _on_frame_resize(self, event):
        """Update scroll region when inner content changes size."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        """Force the inner frame to match the canvas width, unless content is wider."""
        canvas_width = event.width
        inner_req_width = self.inner.winfo_reqwidth()

        # Grow to fill canvas, but allow expanding beyond if content needs it
        new_width = max(canvas_width, inner_req_width)
        self.canvas.itemconfig(self.window_id, width=new_width)

    def _bind_mousewheel(self, widget):
        widget.bind_all("<MouseWheel>", self._on_mousewheel)  # Windows/macOS
        widget.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))  # Linux up
        widget.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))  # Linux down

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class EnvManagerApp:
    """Env Manager APP for the easy ENV change and right"""

    def __init__(self, root):
        self.root = root
        self.root.title("Environment Manager")
        self.root.geometry("950x950")  # Increased height for log box
        self.root.configure(bg=COLORS["bg_main"])

        # --- STYLE KA ENGINE ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background=COLORS["bg_main"], foreground=COLORS["fg_text"], font=("Segoe UI", 10))

        self.style.configure('TLabelframe', background=COLORS["bg_sec"], bordercolor=COLORS["border"])
        self.style.configure('TLabelframe.Label', background=COLORS["bg_sec"], foreground=COLORS["accent"],
                             font=("Segoe UI", 11, "bold"))
        self.style.configure('TButton', background=COLORS["bg_sec"], foreground=COLORS["fg_text"], borderwidth=1,
                             bordercolor=COLORS["border"], focuscolor="none")
        self.style.map('TButton', background=[('active', '#3e3e42'), ('disabled', COLORS["bg_sec"])],
                       foreground=[('active', 'white'), ('disabled', '#666666')])

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

        # --- Start Logic ---
        self.entries = {}
        self.process = None
        self.log_queue = queue.Queue()

        # --- Construct GUI ---
        main_pad = ttk.Frame(root, padding="25")
        main_pad.pack(fill="both", expand=True)

        # HEADER SECTION
        header_frame = ttk.Frame(main_pad)
        header_frame.pack(fill="x", pady=(0, 15))
        ttk.Label(header_frame, text=f"TweakioPY WAAI", font=("Segoe UI", 14, "bold"), foreground="white").pack(
            side="left")
        ttk.Button(header_frame, text="✖ Close App", command=self.on_close, style="Stop.TButton").pack(side="right")
        self.btn_logout = ttk.Button(header_frame, text="⚠ Logout", command=self.logout_session,
                                     style="Warning.TButton")
        self.btn_logout.pack(side="right", padx=(0, 10))

        # EDITOR SECTION
        editor_card = ttk.LabelFrame(main_pad, text=" Configuration ", padding="15")
        editor_card.pack(fill="both", expand=True, pady=(0, 20))
        self.body = ScrollableFrame(editor_card)
        self.body.pack(fill="both", expand=True)

        controls_frame = ttk.Frame(editor_card, style='Card.TFrame')
        controls_frame.pack(fill="x", pady=(15, 0))
        ttk.Button(controls_frame, text="⟳ Reload", command=self.load_env_file).pack(side="left")
        ttk.Button(controls_frame, text="Save Changes", command=self.save_env_file, style="Save.TButton").pack(
            side="right")

        # RUNNER SECTION
        runner_card = ttk.LabelFrame(main_pad, text=" Process Control ", padding="15")
        runner_card.pack(fill="x")
        runner_card.columnconfigure(1, weight=1)
        self.status_indicator = ttk.Label(runner_card, text="●", font=("Arial", 16), foreground=COLORS["danger"],
                                          background=COLORS["bg_sec"])
        self.status_indicator.grid(row=0, column=0, padx=(0, 10))
        self.status_text = ttk.Label(runner_card, text="Stopped", font=("Segoe UI", 11), background=COLORS["bg_sec"])
        self.status_text.grid(row=0, column=1, sticky="w")
        self.btn_run = ttk.Button(runner_card, text="▶ Start Script", command=self.toggle_script,
                                  style="Action.TButton")
        self.btn_run.grid(row=0, column=2)

        # --- LOGS SECTION (NEW) ---
        logs_card = ttk.LabelFrame(main_pad, text=" Console Output ", padding="10")
        logs_card.pack(fill="x", pady=(20, 0))

        # Toolbar inside Logs Card for Clear Button
        logs_toolbar = ttk.Frame(logs_card, style="Card.TFrame")
        logs_toolbar.pack(fill="x", pady=(0, 5))

        # Clear Button (Right Aligned)
        ttk.Button(logs_toolbar, text="🗑 Clear Logs", command=self.clear_logs, style="Warning.TButton").pack(side="right")

        self.log_text = tk.Text(logs_card, height=20, undo=True, maxundo=-1, state="disabled", bg=COLORS["input_bg"],
                                fg=COLORS["fg_text"], insertbackground="white", borderwidth=0, highlightthickness=0,
                                font=("Consolas", 9))

        self.log_text.pack(side="left", fill="both", expand=True)

        log_scroll = ttk.Scrollbar(logs_card, command=self.log_text.yview)
        log_scroll.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=log_scroll.set)

        # Events
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_env_file()

        # Start the loop that watches for new logs
        self.check_log_queue()

    def clear_logs(self):
        """Clears the log text widget."""
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def check_log_queue(self):
        """Checks the queue for new output lines and updates the GUI."""
        if not self.log_queue.empty():
            # Detect if user is scrolled to the bottom (allow 1% tolerance for float inaccuracies)
            # yview() returns (top, bottom). if bottom is > 0.99, we consider it at the end.
            is_at_bottom = self.log_text.yview()[1] > 0.99

            self.log_text.config(state="normal")  # Enable editing to append

            while not self.log_queue.empty():
                line = self.log_queue.get_nowait()
                self.log_text.insert("end", line)

            # Only scroll to end if we were ALREADY at the end
            if is_at_bottom:
                self.log_text.see("end")

            self.log_text.config(state="disabled")  # Disable editing again

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
            if process.stdout:
                process.stdout.close()

    def load_env_file(self):
        """Loads ENV"""
        for widget in self.body.inner.winfo_children():
            widget.destroy()

        self.entries = {}

        if not os.path.exists(ENV_FILE):
            ttk.Label(self.body.inner, text="File not found.", foreground="red").pack()
            return

        try:
            with open(ENV_FILE) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    if "=" in line:
                        key, value = line.split("=", 1)

                        row = ttk.Frame(self.body.inner, style='Card.TFrame')
                        row.pack(fill="x", pady=4)

                        ttk.Label(row, text=key, width=22, font=("Consolas", 10),
                                  background=COLORS["bg_sec"], foreground=COLORS["accent"]).pack(side="left")

                        # UPDATED: Now using the tk.Entry subclass with custom styles
                        entry = UndoEntry(row, cursor="xterm")
                        # Note: We removed entry.configure(style="TEntry") because it's no longer a ttk widget

                        # Initialize stack manually
                        entry.var.set(value)
                        entry._stack = [(value, 0)]
                        entry._stack_index = 0

                        entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
                        self.entries[key] = entry

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_env_file(self):
        """Save Env to the File"""
        try:
            with open(ENV_FILE, "w") as f:
                for key, entry in self.entries.items(): f.write(f"{key}={entry.get()}\n")
            messagebox.showinfo("Saved", "Configuration updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    @staticmethod
    def logout_session():
        """Log Out Session."""
        if not os.path.exists(LOGOUT_DIR):
            messagebox.showinfo("Logout", "No active session found.")
            return
        if messagebox.askyesno("Confirm Logout", f"Delete session data?\n\nTarget: {LOGOUT_DIR}"):
            try:
                shutil.rmtree(LOGOUT_DIR)
                messagebox.showinfo("Success", "Session cleared.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def toggle_script(self):
        """Toggle Script Mode"""
        if self.process is None:
            # START
            if not os.path.exists(SCRIPT_TO_RUN):
                messagebox.showerror("Error", f"{SCRIPT_TO_RUN} missing.")
                return
            try:
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
        """Gracefully shut off"""
        if self.process: self.process.kill()
        self.root.destroy()


if __name__ == "__main__":
    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, "w") as f: f.write("API_KEY=12345\nDB_HOST=localhost\nDEBUG=True")
    if not os.path.exists(SCRIPT_TO_RUN):
        with open(SCRIPT_TO_RUN, "w") as f: f.write(
            "import time\nprint('Worker started...')\nwhile True:\n    print('Working...'); time.sleep(1)")
    dummy_session = os.path.join(".", "Whatsapp", "Wa_Session")
    if not os.path.exists(dummy_session): os.makedirs(dummy_session)

    root = tk.Tk()
    app = EnvManagerApp(root)
    root.mainloop()