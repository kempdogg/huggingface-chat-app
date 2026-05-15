#!/usr/bin/env python3
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, simpledialog
from dotenv import load_dotenv
import json
from datetime import datetime
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import threading

load_dotenv()

API_KEY = os.getenv('HUGGINGFACE_API_KEY')
HF_TOKEN = os.getenv('HF_TOKEN', '')

SKULL_CROSSBONES = """
    ☠️  ⚠️  DISCLAIMER ⚠️  ☠️
    
    ═══════════════════════════════════
    ⚠️  USE AT YOUR OWN RISK  ⚠️
    ═══════════════════════════════════
    
    The developer accepts NO responsibility
    for misuse and wrongful actions by this
    tool. Users are solely responsible for
    ensuring their use complies with all
    applicable laws and terms of service.
    
    This tool uses AI models from Hugging Face.
    Always review AI-generated content
    before using it in any context.
    
    ═══════════════════════════════════
"""

# Available 6B Parameter Models (CPU Optimized)
AVAILABLE_MODELS = {
    "OpenElm-6B": {
        "model_id": "apple/OpenELM-6B",
        "description": "Apple's efficient language model - great for general tasks",
        "size": "~12GB",
        "ram": "~6GB"
    },
    "Mistral-7B-Instruct": {
        "model_id": "mistralai/Mistral-7B-Instruct-v0.1",
        "description": "Fast instruction-following model - excellent for tasks",
        "size": "~13GB",
        "ram": "~7GB"
    },
    "Phi-2": {
        "model_id": "microsoft/phi-2",
        "description": "Microsoft's compact model - surprisingly powerful",
        "size": "~5GB",
        "ram": "~5GB"
    },
    "Llama-2-7B": {
        "model_id": "meta-llama/Llama-2-7b-hf",
        "description": "Meta's open-source model - solid general purpose",
        "size": "~13GB",
        "ram": "~7GB"
    },
    "MPT-7B": {
        "model_id": "mosaicml/mpt-7b",
        "description": "MosaicML's efficient model - good for long context",
        "size": "~13GB",
        "ram": "~7GB"
    },
    "Falcon-7B": {
        "model_id": "tiiuae/falcon-7b",
        "description": "UAE's high-performance model - fastest inference",
        "size": "~13GB",
        "ram": "~7GB"
    },
}

# Default pre-installed models
DEFAULT_MODELS = [
    "Phi-2",  # Smallest and fastest
    "OpenElm-6B",  # Balanced performance
    "Falcon-7B",  # Best for speed
]

class HuggingFaceChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Hugging Face Chat App")
        self.root.geometry("1000x750")
        self.root.configure(bg="#1e1e1e")
        
        # Chat history
        self.chat_history = []
        self.session_file = "chat_history.json"
        self.models_file = "models_config.json"
        self.load_chat_history()
        
        # Load model configuration
        self.installed_models = self.load_models_config()
        self.current_model = self.installed_models[0] if self.installed_models else None
        self.pipelines = {}
        self.loading = False
        
        self.setup_ui()
        self.show_disclaimer_on_startup()
        
    def setup_ui(self):
        """Create the GUI interface"""
        
        # Main frame
        main_frame = tk.Frame(self.root, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg="#2d2d2d")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(
            header_frame,
            text="☠️  HUGGING FACE CHAT APP ☠️",
            font=("Helvetica", 18, "bold"),
            bg="#2d2d2d",
            fg="#00ff00"
        )
        title_label.pack(pady=10)
        
        warning_label = tk.Label(
            header_frame,
            text="⚠️  USE AT YOUR OWN RISK - DEVELOPER ASSUMES NO LIABILITY  ⚠️",
            font=("Helvetica", 10),
            bg="#2d2d2d",
            fg="#ff6b6b"
        )
        warning_label.pack(pady=5)
        
        # Model Selection Frame
        model_frame = tk.Frame(main_frame, bg="#2d2d2d")
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        model_label = tk.Label(
            model_frame,
            text="🤖 Select Model:",
            font=("Helvetica", 11, "bold"),
            bg="#2d2d2d",
            fg="#00ff00"
        )
        model_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.model_var = tk.StringVar(value=self.current_model or "No models installed")
        self.model_dropdown = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=self.installed_models,
            state="readonly",
            font=("Helvetica", 10),
            width=25
        )
        self.model_dropdown.pack(side=tk.LEFT, padx=5)
        self.model_dropdown.bind("<<ComboboxSelected>>", self.on_model_change)
        
        self.model_info_btn = tk.Button(
            model_frame,
            text="ℹ️  Model Info",
            command=self.show_model_info,
            font=("Helvetica", 10, "bold"),
            bg="#0099ff",
            fg="#ffffff",
            activebackground="#0088ee",
            padx=10,
            pady=5
        )
        self.model_info_btn.pack(side=tk.LEFT, padx=5)
        
        self.manage_models_btn = tk.Button(
            model_frame,
            text="⚙️  Manage Models",
            command=self.show_manage_models,
            font=("Helvetica", 10, "bold"),
            bg="#ff6b00",
            fg="#ffffff",
            activebackground="#ff5a00",
            padx=10,
            pady=5
        )
        self.manage_models_btn.pack(side=tk.LEFT, padx=5)
        
        # Model description
        self.model_desc_var = tk.StringVar()
        self.update_model_description()
        desc_label = tk.Label(
            main_frame,
            textvariable=self.model_desc_var,
            font=("Helvetica", 9),
            bg="#1e1e1e",
            fg="#888888",
            wraplength=800
        )
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # Chat display area
        chat_frame = tk.Frame(main_frame, bg="#2d2d2d")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        chat_label = tk.Label(
            chat_frame,
            text="Chat History:",
            font=("Helvetica", 12, "bold"),
            bg="#2d2d2d",
            fg="#00ff00"
        )
        chat_label.pack(anchor="w", padx=5, pady=5)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            height=12,
            font=("Courier", 10),
            bg="#0d0d0d",
            fg="#00ff00",
            insertbackground="#00ff00",
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_display.config(state=tk.DISABLED)
        
        # Input area
        input_label = tk.Label(
            main_frame,
            text="Your Message:",
            font=("Helvetica", 11, "bold"),
            bg="#1e1e1e",
            fg="#00ff00"
        )
        input_label.pack(anchor="w", pady=(10, 5))
        
        self.input_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            height=3,
            font=("Courier", 10),
            bg="#0d0d0d",
            fg="#00ff00",
            insertbackground="#00ff00",
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.input_text.pack(fill=tk.X, pady=(0, 10))
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        send_btn = tk.Button(
            button_frame,
            text="💬 SEND CHAT",
            command=self.send_message,
            font=("Helvetica", 11, "bold"),
            bg="#00ff00",
            fg="#000000",
            activebackground="#00dd00",
            relief=tk.RAISED,
            padx=20,
            pady=8
        )
        send_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(
            button_frame,
            text="🗑️  CLEAR CHAT",
            command=self.clear_chat,
            font=("Helvetica", 11, "bold"),
            bg="#ff6b6b",
            fg="#ffffff",
            activebackground="#ff5555",
            relief=tk.RAISED,
            padx=20,
            pady=8
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        disclaimer_btn = tk.Button(
            button_frame,
            text="⚠️  VIEW DISCLAIMER",
            command=self.show_disclaimer,
            font=("Helvetica", 11, "bold"),
            bg="#ffa500",
            fg="#000000",
            activebackground="#ff9500",
            relief=tk.RAISED,
            padx=20,
            pady=8
        )
        disclaimer_btn.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready | Select a model to start")
        status_bar = tk.Label(
            main_frame,
            textvariable=self.status_var,
            font=("Helvetica", 9),
            bg="#2d2d2d",
            fg="#888888",
            relief=tk.SUNKEN,
            anchor="w"
        )
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        self.refresh_chat_display()
        
    def update_model_description(self):
        """Update model description label"""
        if self.current_model and self.current_model in AVAILABLE_MODELS:
            model_info = AVAILABLE_MODELS[self.current_model]
            desc = f"📊 {model_info['description']} | Size: {model_info['size']} | RAM: {model_info['ram']}"
            self.model_desc_var.set(desc)
        else:
            self.model_desc_var.set("No model selected - Install models using 'Manage Models' button")
    
    def on_model_change(self, event):
        """Handle model selection change"""
        self.current_model = self.model_var.get()
        self.update_model_description()
        self.status_var.set(f"Model switched to: {self.current_model}")
    
    def show_model_info(self):
        """Show detailed info about current model"""
        if not self.current_model:
            messagebox.showwarning("No Model", "Please select a model first")
            return
        
        model_info = AVAILABLE_MODELS.get(self.current_model, {})
        info_text = f"""
Model: {self.current_model}
Model ID: {model_info.get('model_id', 'N/A')}

Description:
{model_info.get('description', 'No description')}

Specifications:
• Model Size: {model_info.get('size', 'N/A')}
• RAM Required: {model_info.get('ram', 'N/A')}
• Type: 6B Parameter Models
• Optimization: CPU-optimized

Status: Downloaded and ready to use
        """
        messagebox.showinfo(f"Model Info - {self.current_model}", info_text)
    
    def show_manage_models(self):
        """Show dialog to manage installed models"""
        manage_window = tk.Toplevel(self.root)
        manage_window.title("🤖 Manage Models")
        manage_window.geometry("600x500")
        manage_window.configure(bg="#1e1e1e")
        
        # Instructions
        instr_label = tk.Label(
            manage_window,
            text="Select 6B parameter models to pre-install:",
            font=("Helvetica", 11, "bold"),
            bg="#1e1e1e",
            fg="#00ff00"
        )
        instr_label.pack(padx=10, pady=10)
        
        # Model checkboxes
        self.model_vars = {}
        models_frame = tk.Frame(manage_window, bg="#1e1e1e")
        models_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for model_name, model_info in AVAILABLE_MODELS.items():
            frame = tk.Frame(models_frame, bg="#2d2d2d", relief=tk.SUNKEN, borderwidth=1)
            frame.pack(fill=tk.X, pady=5, padx=5)
            
            var = tk.BooleanVar(value=model_name in self.installed_models)
            self.model_vars[model_name] = var
            
            cb = tk.Checkbutton(
                frame,
                text=f"  {model_name} - {model_info['description']}",
                variable=var,
                font=("Helvetica", 10),
                bg="#2d2d2d",
                fg="#00ff00",
                selectcolor="#1e1e1e"
            )
            cb.pack(anchor="w", padx=10, pady=5)
            
            details_label = tk.Label(
                frame,
                text=f"     Size: {model_info['size']} | RAM: {model_info['ram']}",
                font=("Helvetica", 8),
                bg="#2d2d2d",
                fg="#888888"
            )
            details_label.pack(anchor="w", padx=20)
        
        # Buttons
        button_frame = tk.Frame(manage_window, bg="#1e1e1e")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        save_btn = tk.Button(
            button_frame,
            text="💾 SAVE & INSTALL",
            command=lambda: self.save_model_config(manage_window),
            font=("Helvetica", 11, "bold"),
            bg="#00ff00",
            fg="#000000",
            padx=20,
            pady=8
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="❌ CANCEL",
            command=manage_window.destroy,
            font=("Helvetica", 11, "bold"),
            bg="#ff6b6b",
            fg="#ffffff",
            padx=20,
            pady=8
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def save_model_config(self, window):
        """Save selected models configuration"""
        selected = [name for name, var in self.model_vars.items() if var.get()]
        
        if not selected:
            messagebox.showwarning("No Models", "Please select at least one model")
            return
        
        config = {"installed_models": selected}
        try:
            with open(self.models_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.installed_models = selected
            self.current_model = selected[0]
            self.model_var.set(self.current_model)
            self.model_dropdown.config(values=self.installed_models)
            self.update_model_description()
            
            messagebox.showinfo(
                "Models Saved",
                f"Configuration saved!\n\nSelected models:\n" + "\n".join(selected) +
                "\n\nModels will be downloaded on first use."
            )
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def load_models_config(self):
        """Load models configuration"""
        try:
            if os.path.exists(self.models_file):
                with open(self.models_file, 'r') as f:
                    config = json.load(f)
                    return config.get("installed_models", DEFAULT_MODELS)
        except Exception as e:
            print(f"Error loading models config: {e}")
        
        return DEFAULT_MODELS
    
    def load_model(self):
        """Load the selected model using transformers"""
        if not self.current_model or self.current_model in self.pipelines:
            return True
        
        try:
            self.status_var.set(f"Loading {self.current_model}... This may take a moment")
            self.root.update()
            
            model_id = AVAILABLE_MODELS[self.current_model]["model_id"]
            
            # Load pipeline for text generation
            self.pipelines[self.current_model] = pipeline(
                "text-generation",
                model=model_id,
                device=-1,  # CPU only
                torch_dtype="auto",
                token=HF_TOKEN if HF_TOKEN else None
            )
            
            self.status_var.set(f"Model loaded: {self.current_model}")
            return True
        except Exception as e:
            error_msg = f"Error loading model: {str(e)}"
            self.status_var.set("Ready")
            messagebox.showerror("Model Loading Error", error_msg)
            return False
    
    def generate_response(self, prompt):
        """Generate response using the loaded model"""
        if not self.current_model:
            return "Error: No model selected"
        
        if not self.load_model():
            return "Error: Failed to load model"
        
        try:
            self.status_var.set("Generating response... (this may take a while on CPU)")
            self.root.update()
            
            pipeline_obj = self.pipelines[self.current_model]
            
            # Generate with reasonable parameters
            outputs = pipeline_obj(
                prompt,
                max_length=200,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
            
            response = outputs[0]['generated_text']
            self.status_var.set("Response generated")
            return response
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def send_message(self):
        """Send message and get response"""
        if not self.current_model:
            messagebox.showwarning("No Model", "Please select a model first from the dropdown")
            return
        
        user_input = self.input_text.get("1.0", tk.END).strip()
        
        if not user_input:
            messagebox.showwarning("Empty Message", "Please enter a message before sending.")
            return
        
        # Show disclaimer
        response = messagebox.askyesno(
            "⚠️  CONFIRM - DISCLAIMER ⚠️",
            SKULL_CROSSBONES + "\n\nDo you accept these terms and wish to continue?"
        )
        
        if not response:
            return
        
        # Add user message
        self.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat(),
            "model": self.current_model
        })
        
        # Generate response in a thread to avoid freezing UI
        thread = threading.Thread(target=self._generate_and_display, args=(user_input,))
        thread.daemon = True
        thread.start()
    
    def _generate_and_display(self, prompt):
        """Generate response and display it"""
        ai_response = self.generate_response(prompt)
        
        # Add AI response
        self.chat_history.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat(),
            "model": self.current_model
        })
        
        # Save and refresh
        self.save_chat_history()
        self.refresh_chat_display()
        self.input_text.delete("1.0", tk.END)
    
    def refresh_chat_display(self):
        """Refresh the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        
        for message in self.chat_history:
            timestamp = message.get("timestamp", "")
            model = message.get("model", "")
            if timestamp:
                timestamp = timestamp.split("T")[1][:5]
            
            if message["role"] == "user":
                self.chat_display.insert(tk.END, f"[{timestamp}] YOU: ", "user")
                self.chat_display.insert(tk.END, f"{message['content']}\n\n")
            else:
                self.chat_display.insert(tk.END, f"[{timestamp}] {model}: ", "assistant")
                self.chat_display.insert(tk.END, f"{message['content']}\n\n")
        
        self.chat_display.tag_config("user", foreground="#00ff00", font=("Courier", 10, "bold"))
        self.chat_display.tag_config("assistant", foreground="#ffaa00", font=("Courier", 10, "bold"))
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def clear_chat(self):
        """Clear chat history"""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear all chat history?"):
            self.chat_history = []
            self.save_chat_history()
            self.refresh_chat_display()
            self.status_var.set("Chat cleared")
    
    def show_disclaimer_on_startup(self):
        """Show disclaimer when app starts"""
        messagebox.showwarning(
            "⚠️  DISCLAIMER - USE AT YOUR OWN RISK ⚠️",
            SKULL_CROSSBONES
        )
    
    def show_disclaimer(self):
        """Display the full disclaimer"""
        messagebox.showwarning(
            "⚠️  FULL DISCLAIMER ⚠️",
            SKULL_CROSSBONES
        )
    
    def save_chat_history(self):
        """Save chat history to file"""
        try:
            with open(self.session_file, 'w') as f:
                json.dump(self.chat_history, f, indent=2)
        except Exception as e:
            print(f"Error saving chat history: {e}")
    
    def load_chat_history(self):
        """Load chat history from file"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    self.chat_history = json.load(f)
            else:
                self.chat_history = []
        except Exception as e:
            print(f"Error loading chat history: {e}")
            self.chat_history = []


def main():
    """Main entry point"""
    root = tk.Tk()
    app = HuggingFaceChatApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
