import threading
import tkinter as tk
from tkinter import ttk, messagebox

from .logic import TranslatorService
from .languages_config import LANG_MAP

# Class to implement the UI for the Voice to Voice Translator application
class VoiceToVoiceTranslatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Voice2Voice Translator")

        self._setup_dark_theme()

        # Create Logic Service
        self.service = TranslatorService()

        self._build_gui()

    def _build_gui(self):
        main = ttk.Frame(self.root, padding=10)
        main.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Language Selection

        ttk.Label(main, text = "Source Language:").grid(row=0, column=0, sticky="w")
        ttk.Label(main, text = "Target Language:").grid(row=0, column=1, sticky="w")

        # Build lists from LANG_MAP

        self.lang_keys = list(LANG_MAP.keys())
        self.lang_labels = [LANG_MAP[k]["ui_label"] for k in self.lang_keys]

        self.source_var = tk.StringVar()
        self.target_var = tk.StringVar()

        self.source_combo = ttk.Combobox(
        main,
        textvariable=self.source_var,
        values=self.lang_labels,
        state="readonly",
        style="Dark.TCombobox"
        )
        self.target_combo = ttk.Combobox(
            main,
            textvariable=self.target_var,
            values=self.lang_labels,
            state="readonly",
            style="Dark.TCombobox"
        )

        self.source_combo.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.target_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)

        # Text Areas

        ttk.Label(main, text = "Recognized Text:").grid(row=2, column=0, sticky="w", pady=(10,0))
        ttk.Label(main, text = "Translated Text:").grid(row=2, column=1, sticky="w", pady=(10,0))

        self.source_text = tk.Text(
            main,
            height=5,
            wrap="word",
            bg="#1e1e1e",          # dark background
            fg="#ffffff",          # white text
            insertbackground="#ffffff"  # white cursor
        )
        self.translated_text = tk.Text(
            main,
            height=5,
            wrap="word",
            bg="#1e1e1e",
            fg="#ffffff",
            insertbackground="#ffffff"
        )

        self.source_text.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        self.translated_text.grid(row=3, column=1, sticky="nsew", padx=5, pady=5)

        main.rowconfigure(3, weight=1)

        # Button and Status

        self.record_button = ttk.Button(main, text = "Record & Translate", command=self._on_record_clicked)

        self.record_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.status_var = tk.StringVar(value="Ready.")
        self.status_label = ttk.Label(main, textvariable=self.status_var)
        self.status_label.grid(row=5, column=0, columnspan=2, sticky="w")

    def _on_record_clicked(self):
        self.record_button.config(state="disabled") # Disable button during processing
        self.status_var.set("Starting...")

        # map selected labels -> canonical keys
        try:
            src_label = self.source_var.get()
            tgt_label = self.target_var.get()
            src_key = self.lang_keys[self.lang_labels.index(src_label)]
            tgt_key = self.lang_keys[self.lang_labels.index(tgt_label)]
        except ValueError:
            messagebox.showerror("Error", "Please select both languages.")
            self.record_button.config(state="normal")
            self.status_var.set("Ready.")
            return

        callbacks = {
            "on_status": self._cb_status,
            "on_source_text": self._cb_source_text,
            "on_translated_text": self._cb_translated_text,
            "on_error": self._cb_error,
        }

        thread = threading.Thread(
            target=self.service.run_pipeline,
            args=(src_key, tgt_key, callbacks),
            daemon=True,
        )

        thread.start()

    # Callback handlers to update the UI

    def _cb_status(self, msg: str):
        self.root.after(0, lambda: self.status_var.set(msg))

    def _cb_source_text(self, text: str):
        def update():
            self.source_text.delete("1.0", tk.END)
            self.source_text.insert(tk.END, text)
        self.root.after(0, update)

    def _cb_translated_text(self, text: str):
        def update():
            self.translated_text.delete("1.0", tk.END)
            self.translated_text.insert(tk.END, text)
            self.record_button.config(state="normal") # Re-enable button
        self.root.after(0, update)

    def _cb_error(self, msg: str):
        def show():
            messagebox.showerror("Error", msg)
            self.record_button.config(state="normal")
            self.status_var.set("Error.")
        self.root.after(0, show)

    # Style setup

    def _setup_dark_theme(self):
        style = ttk.Style(self.root)

        # Use a platform-appropriate base theme
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        bg = "#2b2b2b"
        fg = "#ffffff"
        accent = "#3c78d8"

        # General background
        self.root.configure(bg=bg)
        style.configure(".", background=bg, foreground=fg)

        # Frames
        style.configure("TFrame", background=bg)

        # Labels
        style.configure("TLabel", background=bg, foreground=fg)

        # Buttons
        style.configure(
            "TButton",
            background="#3a3a3a",
            foreground=fg,
            padding=6,
        )
        style.map(
            "TButton",
            background=[("active", "#505050")],
        )

        # Combobox
        style.configure(
        "Dark.TCombobox",
        foreground=fg,
        background="#3a3a3a",      # arrow-button area
        fieldbackground="#3a3a3a", # text-entry area
        bordercolor="#3a3a3a",
        lightcolor="#3a3a3a",
        darkcolor="#3a3a3a",
        arrowcolor=fg,
        )
        style.map(
            "Dark.TCombobox",
            foreground=[("readonly", fg), ("active", fg)],
            fieldbackground=[("readonly", "#3a3a3a"), ("active", "#505050")],
            background=[("active", "#505050")],
        )

        # Dark dropdown list part
        self.root.option_add("*TCombobox*Listbox.background", "#3a3a3a")
        self.root.option_add("*TCombobox*Listbox.foreground", fg)
    
