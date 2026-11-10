#!/usr/bin/env python3
"""A small Tkinter UI for selecting and downloading Hugging Face GGUF models."""

import json
import queue
import re
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox, ttk
from urllib.parse import quote, urlparse

APP_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = APP_ROOT / "models_config.json"
SETUP_SCRIPT = APP_ROOT / "scripts" / "setup_install.py"
HF_MODELS_URL = "https://huggingface.co/models?library=gguf&sort=downloads"
BG = "#1e1e1e"
PANEL = "#2d2d2d"
FG = "#f2f2f2"
ACCENT = "#00cc88"


class ModelManager:
    def __init__(self, root):
        self.root = root
        root.title("Hugging Face GGUF Model Manager")
        root.geometry("760x650")
        root.minsize(620, 480)
        root.configure(bg=BG)
        self.jobs = queue.Queue()
        self.vars = {}
        self.models = self.read_models()
        self.build_ui()
        self.refresh_models()
        self.root.after(150, self.poll_jobs)

    def read_models(self):
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return data.get("models", [])
        except (OSError, json.JSONDecodeError):
            return []

    def save_models(self):
        CONFIG_PATH.write_text(
            json.dumps({"models": self.models}, indent=2) + "\n", encoding="utf-8"
        )

    def build_ui(self):
        title = tk.Label(
            self.root, text="Hugging Face GGUF Models", bg=BG, fg=ACCENT,
            font=("Helvetica", 20, "bold")
        )
        title.pack(anchor="w", padx=18, pady=(16, 2))
        tk.Label(
            self.root,
            text="Choose models to download locally, or add a GGUF repository from Hugging Face.",
            bg=BG, fg=FG, wraplength=700, justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 12))

        top_buttons = tk.Frame(self.root, bg=BG)
        top_buttons.pack(fill="x", padx=18, pady=(0, 10))
        tk.Button(
            top_buttons, text="Browse GGUF models on Hugging Face", command=self.open_hf,
            bg="#2878c8", fg="white", padx=10, pady=6
        ).pack(side="left")

        add_frame = tk.LabelFrame(
            self.root, text="Add a custom model", bg=PANEL, fg=FG,
            padx=10, pady=8
        )
        add_frame.pack(fill="x", padx=18, pady=(0, 10))
        tk.Label(
            add_frame, text="Repository ID or URL", bg=PANEL, fg=FG
        ).grid(row=0, column=0, sticky="w")
        self.repo_entry = tk.Entry(add_frame, width=54)
        self.repo_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(3, 5))
        self.repo_entry.insert(0, "owner/model-GGUF")
        tk.Button(
            add_frame, text="Add", command=self.add_model, bg=ACCENT, fg="#111111",
            padx=16, pady=4
        ).grid(row=1, column=1, sticky="e", pady=(3, 5))
        tk.Label(
            add_frame,
            text="Optional exact filename (leave blank to choose the first .gguf file):",
            bg=PANEL, fg=FG
        ).grid(row=2, column=0, sticky="w", pady=(3, 0))
        self.filename_entry = tk.Entry(add_frame, width=54)
        self.filename_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(3, 0))
        add_frame.columnconfigure(0, weight=1)

        list_frame = tk.LabelFrame(
            self.root, text="Selected models (downloads can be several GB)",
            bg=PANEL, fg=FG, padx=8, pady=8
        )
        list_frame.pack(fill="both", expand=True, padx=18, pady=(0, 10))
        self.model_list = tk.Frame(list_frame, bg=PANEL)
        self.model_list.pack(fill="both", expand=True)

        actions = tk.Frame(self.root, bg=BG)
        actions.pack(fill="x", padx=18, pady=(0, 8))
        self.download_button = tk.Button(
            actions, text="Download selected models", command=self.download_selected,
            bg=ACCENT, fg="#111111", font=("Helvetica", 11, "bold"), padx=12, pady=7
        )
        self.download_button.pack(side="left")
        tk.Button(
            actions, text="Close", command=self.root.destroy, padx=12, pady=7
        ).pack(side="right")

        self.status = tk.StringVar(value="Ready")
        tk.Label(
            self.root, textvariable=self.status, bg="#111111", fg=FG,
            anchor="w", padx=10, pady=6
        ).pack(fill="x", side="bottom")

    def open_hf(self):
        webbrowser.open(HF_MODELS_URL)

    @staticmethod
    def parse_repo(value):
        value = value.strip()
        if value.startswith(("https://", "http://")):
            parsed = urlparse(value)
            if parsed.hostname not in {"huggingface.co", "www.huggingface.co"}:
                raise ValueError("Please enter a huggingface.co model page URL.")
            parts = [part for part in parsed.path.split("/") if part]
            if len(parts) < 2 or parts[0] in {"models", "datasets", "spaces"}:
                raise ValueError("Use a model URL like https://huggingface.co/owner/model.")
            repo_id = "/".join(parts[:2])
        else:
            repo_id = value.strip("/")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo_id):
            raise ValueError("Enter a model repository as owner/model or paste its Hugging Face URL.")
        return repo_id

    def add_model(self):
        try:
            repo_id = self.parse_repo(self.repo_entry.get())
        except ValueError as exc:
            messagebox.showerror("Invalid model", str(exc), parent=self.root)
            return
        if any(model.get("repo_id", "").casefold() == repo_id.casefold() for model in self.models):
            messagebox.showinfo("Already added", f"{repo_id} is already in your model list.", parent=self.root)
            return

        filename = self.filename_entry.get().strip() or None
        key = re.sub(r"[^a-z0-9]+", "_", repo_id.lower()).strip("_")
        self.models.append({
            "key": key,
            "name": repo_id.rsplit("/", 1)[-1],
            "repo_id": repo_id,
            "filename": filename,
            "local_path": None,
            "auto_install": True,
        })
        self.save_models()
        self.repo_entry.delete(0, tk.END)
        self.filename_entry.delete(0, tk.END)
        self.refresh_models()
        self.status.set(f"Added {repo_id}. It is selected for download.")

    def refresh_models(self):
        for child in self.model_list.winfo_children():
            child.destroy()
        self.vars.clear()
        if not self.models:
            tk.Label(
                self.model_list, text="No models yet. Add one using its Hugging Face model page URL or owner/model ID.",
                bg=PANEL, fg=FG, wraplength=650, justify="left"
            ).pack(anchor="w", pady=5)
            return

        for index, model in enumerate(self.models):
            row = tk.Frame(self.model_list, bg=PANEL)
            row.pack(fill="x", anchor="w", pady=3)
            selected = tk.BooleanVar(value=bool(model.get("auto_install", False)))
            self.vars[index] = selected
            tk.Checkbutton(
                row, text=model.get("name") or model.get("repo_id", "Unknown model"),
                variable=selected, command=self.selection_changed,
                bg=PANEL, fg=FG, selectcolor=BG, activebackground=PANEL,
                activeforeground=FG, anchor="w"
            ).pack(side="left", fill="x", expand=True)
            tk.Label(
                row, text=model.get("repo_id", ""), bg=PANEL, fg="#b8b8b8"
            ).pack(side="left", padx=8)
            path = model.get("local_path")
            tk.Label(
                row, text="Downloaded" if path and (APP_ROOT / path).exists() else "Not downloaded",
                bg=PANEL, fg=ACCENT if path and (APP_ROOT / path).exists() else "#f0b35a"
            ).pack(side="right", padx=5)

    def selection_changed(self):
        for index, variable in self.vars.items():
            self.models[index]["auto_install"] = variable.get()
        self.save_models()

    def download_selected(self):
        self.selection_changed()
        if not any(model.get("auto_install") for model in self.models):
            messagebox.showwarning("No models selected", "Select at least one model to download.", parent=self.root)
            return
        self.download_button.configure(state="disabled")
        self.status.set("Downloading selected GGUF models. Large files may take a while...")
        threading.Thread(target=self.run_download, daemon=True).start()

    def run_download(self):
        try:
            process = subprocess.Popen(
                [sys.executable, str(SETUP_SCRIPT)], cwd=APP_ROOT,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            for line in process.stdout:
                self.jobs.put(("log", line.rstrip()))
            code = process.wait()
            self.jobs.put(("done", code))
        except Exception as exc:
            self.jobs.put(("error", str(exc)))

    def poll_jobs(self):
        try:
            while True:
                kind, value = self.jobs.get_nowait()
                if kind == "log":
                    self.status.set(value[:180])
                elif kind == "done":
                    self.download_button.configure(state="normal")
                    self.models = self.read_models()
                    self.refresh_models()
                    if value == 0:
                        self.status.set("Selected models are downloaded and ready.")
                        messagebox.showinfo("Download complete", "All selected GGUF models are downloaded.", parent=self.root)
                    else:
                        self.status.set("A model download failed. Check access, HF_TOKEN, internet, and disk space.")
                        messagebox.showerror(
                            "Download failed",
                            "At least one selected model could not be downloaded. Check the terminal output, model access, HF_TOKEN for gated models, and free disk space.",
                            parent=self.root,
                        )
                elif kind == "error":
                    self.download_button.configure(state="normal")
                    self.status.set("Could not start the model downloader.")
                    messagebox.showerror("Download error", value, parent=self.root)
        except queue.Empty:
            pass
        self.root.after(150, self.poll_jobs)


def main():
    root = tk.Tk()
    ModelManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
