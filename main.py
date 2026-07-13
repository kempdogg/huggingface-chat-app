#!/usr/bin/env python3
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, simpledialog, filedialog
from dotenv import load_dotenv
import json
from datetime import datetime
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import threading
from openai import OpenAI
from PIL import Image, ImageTk
import io
import base64
from urllib.parse import urlparse

load_dotenv()

API_KEY = os.getenv('HUGGINGFACE_API_KEY')
HF_TOKEN = os.getenv('HF_TOKEN', '')

SKULL_CROSSBONES = """
    ☠️  ⚠️  DISCLAIMER ⚠️  ☠️
    
    ═══════════════════════════════════════════
    ⚠️  USE AT YOUR OWN RISK  ⚠️
    ═══════════════════════════════════════════
    
    The developer accepts NO responsibility
    for misuse and wrongful actions by this
    tool. Users are solely responsible for
    ensuring their use complies with all
    applicable laws and terms of service.
    
    This tool uses AI models from Hugging Face.
    Always review AI-generated content
    before using it in any context.
    
    ═══════════════════════════════════════════
"""

# Available 6B Parameter Models (CPU Optimized)
AVAILABLE_MODELS = {
    "Phi-2": {
        "model_id": "microsoft/phi-2",
        "description": "Microsoft's compact model - surprisingly powerful",
        "size": "~5GB",
        "ram": "~5GB"
    },
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
    "GLM-4.5V": {
        "model_id": "zai-org/GLM-4.5V:novita",
        "description": "Multi-modal vision+text model - analyze images with AI",
        "size": "~10GB",
        "ram": "~8GB",
        "is_multimodal": True
    }
}

# Default pre-installed models
DEFAULT_MODELS = [
    "Phi-2",
    "OpenElm-6B",
    "Falcon-7B",
]

class HuggingFaceChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Hugging Face Chat App")
        self.root.geometry("1300x950")
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
        self.disclaimer_shown = False
        self.current_image = None
        self.current_image_url = None
        self.openai_client = None
        self.photo_ref = None  # Keep reference to prevent garbage collection
        
        # Initialize OpenAI client for HF router
        if HF_TOKEN:
            self.openai_client = OpenAI(
                base_url="https://router.huggingface.co/v1",
                api_key=HF_TOKEN,
            )
        
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
            font=("Helvetica", 24, "bold"),
            bg="#2d2d2d",
            fg="#00ff00"
        )
        title_label.pack(pady=10)
        
        warning_label = tk.Label(
            header_frame,
            text="⚠️  USE AT YOUR OWN RISK - DEVELOPER ASSUMES NO LIABILITY  ⚠️",
            font=("Helvetica", 13),
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
            font=("Helvetica", 14, "bold"),
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
            font=("Helvetica", 12),
            width=25
        )
        self.model_dropdown.pack(side=tk.LEFT, padx=5)
        self.model_dropdown.bind("<<ComboboxSelected>>", self.on_model_change)
        
        self.model_info_btn = tk.Button(
            model_frame,
            text="ℹ️  Model Info",
            command=self.show_model_info,
            font=("Helvetica", 11, "bold"),
            bg="#0099ff",
            fg="#ffffff",
            activebackground="#0088ee",
            padx=12,
            pady=6
        )
        self.model_info_btn.pack(side=tk.LEFT, padx=5)
        
        self.manage_models_btn = tk.Button(
            model_frame,
            text="⚙️  Manage Models",
            command=self.show_manage_models,
            font=("Helvetica", 11, "bold"),
            bg="#ff6b00",
            fg="#ffffff",
            activebackground="#ff5a00",
            padx=12,
            pady=6
        )
        self.manage_models_btn.pack(side=tk.LEFT, padx=5)
        
        # Custom Model Frame
        custom_model_frame = tk.Frame(main_frame, bg="#2d2d2d")
        custom_model_frame.pack(fill=tk.X, pady=(0, 10))
        
        custom_label = tk.Label(
            custom_model_frame,
            text="🔧 Try Custom Model (HuggingFace ID):",
            font=("Helvetica", 14, "bold"),
            bg="#2d2d2d",
            fg="#00ff00"
        )
        custom_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.custom_model_entry = tk.Entry(
            custom_model_frame,
            font=("Helvetica", 12),
            bg="#0d0d0d",
            fg="#00ff00",
            insertbackground="#00ff00",
            width=35
        )
        self.custom_model_entry.pack(side=tk.LEFT, padx=5)
        self.custom_model_entry.insert(0, "microsoft/phi-2")
        
        load_custom_btn = tk.Button(
            custom_model_frame,
            text="🚀 Load Custom",
            command=self.load_custom_model,
            font=("Helvetica", 11, "bold"),
            bg="#00cc00",
            fg="#000000",
            activebackground="#00bb00",
            padx=12,
            pady=6
        )
        load_custom_btn.pack(side=tk.LEFT, padx=5)
        
        # Model description
        self.model_desc_var = tk.StringVar()
        self.update_model_description()
        desc_label = tk.Label(
            main_frame,
            textvariable=self.model_desc_var,
            font=("Helvetica", 11),
            bg="#1e1e1e",
            fg="#ffff00",
            wraplength=1000
        )
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # Content frame (chat + image side by side)
        content_frame = tk.Frame(main_frame, bg="#1e1e1e")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Chat display area
        chat_frame = tk.Frame(content_frame, bg="#2d2d2d")
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        chat_label = tk.Label(
            chat_frame,
            text="💬 Chat History:",
            font=("Helvetica", 14, "bold"),
            bg="#2d2d2d",
            fg="#00ff00"
        )
        chat_label.pack(anchor="w", padx=5, pady=5)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            height=12,
            font=("Courier", 11),
            bg="#0d0d0d",
            fg="#00ff00",
            insertbackground="#00ff00",
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chat_display.config(state=tk.DISABLED)
        
        # Image display area
        image_frame = tk.Frame(content_frame, bg="#2d2d2d", width=300)
        image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        image_frame.pack_propagate(False)
        
        image_label = tk.Label(
            image_frame,
            text="🖼️  Image Preview:",
            font=("Helvetica", 14, "bold"),
            bg="#2d2d2d",
            fg="#00ff00"
        )
        image_label.pack(anchor="w", padx=5, pady=5)
        
        self.image_display = tk.Label(
            image_frame,
            bg="#0d0d0d",
            fg="#888888",
            text="No image loaded",
            font=("Courier", 11),
            relief=tk.SUNKEN,
            borderwidth=2,
            width=35,
            height=15
        )
        self.image_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Image button frame
        img_btn_frame = tk.Frame(image_frame, bg="#2d2d2d")
        img_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        upload_img_btn = tk.Button(
            img_btn_frame,
            text="📁 Upload",
            command=self.upload_image,
            font=("Helvetica", 9, "bold"),
            bg="#00aa88",
            fg="#ffffff",
            activebackground="#009977",
            padx=8,
            pady=4
        )
        upload_img_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        url_img_btn = tk.Button(
            img_btn_frame,
            text="🔗 URL",
            command=self.load_image_url,
            font=("Helvetica", 9, "bold"),
            bg="#0088aa",
            fg="#ffffff",
            activebackground="#007799",
            padx=8,
            pady=4
        )
        url_img_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        clear_img_btn = tk.Button(
            img_btn_frame,
            text="❌ Clear",
            command=self.clear_image,
            font=("Helvetica", 9, "bold"),
            bg="#aa0000",
            fg="#ffffff",
            activebackground="#990000",
            padx=8,
            pady=4
        )
        clear_img_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Input area
        input_label = tk.Label(
            main_frame,
            text="📝 Your Message:",
            font=("Helvetica", 14, "bold"),
            bg="#1e1e1e",
            fg="#00ff00"
        )
        input_label.pack(anchor="w", pady=(10, 5))
        
        self.input_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            height=4,
            font=("Courier", 12),
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
            font=("Helvetica", 12, "bold"),
            bg="#00ff00",
            fg="#000000",
            activebackground="#00dd00",
            relief=tk.RAISED,
            padx=20,
            pady=10
        )
        send_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(
            button_frame,
            text="🗑️  CLEAR CHAT",
            command=self.clear_chat,
            font=("Helvetica", 12, "bold"),
            bg="#ff6b6b",
            fg="#ffffff",
            activebackground="#ff5555",
            relief=tk.RAISED,
            padx=20,
            pady=10
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        disclaimer_btn = tk.Button(
            button_frame,
            text="⚠️  VIEW DISCLAIMER",
            command=self.show_disclaimer,
            font=("Helvetica", 12, "bold"),
            bg="#ffa500",
            fg="#000000",
            activebackground="#ff9500",
            relief=tk.RAISED,
            padx=20,
            pady=10
        )
        disclaimer_btn.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready | Select a model to start")
        status_bar = tk.Label(
            main_frame,
            textvariable=self.status_var,
            font=("Helvetica", 11),
            bg="#2d2d2d",
            fg="#888888",
            relief=tk.SUNKEN,
            anchor="w"
        )
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        self.refresh_chat_display()
    
    def upload_image(self):
        """Upload image from local file"""
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                img = Image.open(file_path)
                self.current_image = img
                self.current_image_url = None
                self.display_image_preview(img)
                self.status_var.set(f"Image loaded: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def load_image_url(self):
        """Load image from URL"""
        url = simpledialog.askstring("Image URL", "Enter image URL:")
        
        if url:
            try:
                import requests
                response = requests.get(url, timeout=10)
                img = Image.open(io.BytesIO(response.content))
                self.current_image = None
                self.current_image_url = url
                self.display_image_preview(img)
                self.status_var.set(f"Image loaded from URL")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image from URL: {str(e)}")
    
    def display_image_preview(self, img):
        """Display image preview in the UI"""
        try:
            # Resize image to fit in preview area
            img.thumbnail((280, 280), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            self.photo_ref = ImageTk.PhotoImage(img)
            
            self.image_display.config(image=self.photo_ref, text="")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {str(e)}")
    
    def clear_image(self):
        """Clear the loaded image"""
        self.current_image = None
        self.current_image_url = None
        self.image_display.config(image="", text="No image loaded")
        self.photo_ref = None
        self.status_var.set("Image cleared")
    
    def update_model_description(self):
        """Update model description label"""
        if self.current_model and self.current_model in AVAILABLE_MODELS:
            model_info = AVAILABLE_MODELS[self.current_model]
            desc = f"📊 {model_info['description']} | Size: {model_info['size']} | RAM: {model_info['ram']}"
            self.model_desc_var.set(desc)
        else:
            self.model_desc_var.set("No model selected - Install models using 'Manage Models' button or load a custom model")
    
    def on_model_change(self, event):
        """Handle model selection change"""
        self.current_model = self.model_var.get()
        self.update_model_description()
        self.status_var.set(f"Model switched to: {self.current_model}")
    
    def load_custom_model(self):
        """Load a custom model from HuggingFace"""
        custom_id = self.custom_model_entry.get().strip()
        
        if not custom_id:
            messagebox.showwarning("Empty Model ID", "Please enter a valid HuggingFace model ID")
            return
        
        self.current_model = custom_id
        self.model_var.set(custom_id)
        
        # Update description
        if custom_id in AVAILABLE_MODELS:
            self.update_model_description()
        else:
            self.model_desc_var.set(f"Custom Model: {custom_id} (Loading...)")
        
        self.status_var.set(f"Custom model selected: {custom_id}")
        messagebox.showinfo("Custom Model Selected", f"Model '{custom_id}' will be downloaded on first use.\n\nNote: This may take 5-30 minutes depending on model size.")
    
    def show_model_info(self):
        """Show detailed info about current model"""
        if not self.current_model:
            messagebox.showwarning("No Model", "Please select a model first")
            return
        
        model_info = AVAILABLE_MODELS.get(self.current_model, {})
        if model_info:
            multimodal_text = "Yes (Vision+Text)" if model_info.get('is_multimodal') else "No (Text only)"
            info_text = f"""
Model: {self.current_model}
Model ID: {model_info.get('model_id', 'N/A')}

Description:
{model_info.get('description', 'No description')}

Specifications:
• Model Size: {model_info.get('size', 'N/A')}
• RAM Required: {model_info.get('ram', 'N/A')}
• Type: 6B-7B Parameter Models
• Optimization: CPU-optimized
• Multi-modal: {multimodal_text}

Status: Downloaded and ready to use
            """
        else:
            info_text = f"Custom Model: {self.current_model}\n\nThis is a custom model loaded from HuggingFace."
        
        messagebox.showinfo(f"Model Info - {self.current_model}", info_text)
    
    def show_manage_models(self):
        """Show dialog to manage installed models"""
        manage_window = tk.Toplevel(self.root)
        manage_window.title("🤖 Manage Models")
        manage_window.geometry("700x600")
        manage_window.configure(bg="#1e1e1e")
        
        # Instructions
        instr_label = tk.Label(
            manage_window,
            text="Select 6B parameter models to pre-install:",
            font=("Helvetica", 13, "bold"),
            bg="#1e1e1e",
            fg="#00ff00"
        )
        instr_label.pack(padx=10, pady=10)
        
        # Model checkboxes
        self.model_vars = {}
        models_frame = tk.Frame(manage_window, bg="#1e1e1e")
        models_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for model_name, model_info in AVAILABLE_MODELS.items():
            frame = tk.Frame(models_frame, bg="#2d2d2d", relief=tk.SUNKEN, borderwidth=2)
            frame.pack(fill=tk.X, pady=7, padx=5)
            
            var = tk.BooleanVar(value=model_name in self.installed_models)
            self.model_vars[model_name] = var
            
            cb = tk.Checkbutton(
                frame,
                text=f"  {model_name}",
                variable=var,
                font=("Helvetica", 12, "bold"),
                bg="#2d2d2d",
                fg="#00ff00",
                selectcolor="#1e1e1e"
            )
            cb.pack(anchor="w", padx=10, pady=5)
            
            desc_label = tk.Label(
                frame,
                text=f"     {model_info['description']}",
                font=("Helvetica", 11),
                bg="#2d2d2d",
                fg="#ffff00"
            )
            desc_label.pack(anchor="w", padx=20)
            
            details_label = tk.Label(
                frame,
                text=f"     Size: {model_info['size']} | RAM: {model_info['ram']}",
                font=("Helvetica", 10),
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
            font=("Helvetica", 12, "bold"),
            bg="#00ff00",
            fg="#000000",
            padx=20,
            pady=10
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="❌ CANCEL",
            command=manage_window.destroy,
            font=("Helvetica", 12, "bold"),
            bg="#ff6b6b",
            fg="#ffffff",
            padx=20,
            pady=10
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
            
            model_id = self.current_model
            if self.current_model in AVAILABLE_MODELS:
                model_id = AVAILABLE_MODELS[self.current_model]["model_id"]
            
            # Load pipeline for text generation
            self.pipelines[self.current_model] = pipeline(
                "text-generation",
                model=model_id,
                device=-1,
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
    
    def generate_response_local(self, prompt):
        """Generate response using the loaded model (local)"""
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
    
    def generate_response_multimodal(self, text_prompt):
        """Generate response using HF router API with streaming (supports images)"""
        if not self.openai_client:
            return "Error: HF_TOKEN not configured. Set HF_TOKEN in .env file for multi-modal support."
        
        try:
            self.status_var.set("Generating multi-modal response... (streaming)")
            self.root.update()
            
            # Build message content
            content = [
                {
                    "type": "text",
                    "text": text_prompt
                }
            ]
            
            # Add image if present
            if self.current_image_url:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": self.current_image_url
                    }
                })
            elif self.current_image:
                # Convert PIL Image to base64
                buffered = io.BytesIO()
                self.current_image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{img_base64}"
                    }
                })
            
            # Stream the response
            response_text = ""
            stream = self.openai_client.chat.completions.create(
                model="zai-org/GLM-4.5V:novita",
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                stream=True,
                temperature=0.7,
                top_p=0.9,
                max_tokens=500
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    response_text += chunk.choices[0].delta.content
            
            self.status_var.set("Multi-modal response generated")
            return response_text if response_text else "No response received from model."
        
        except Exception as e:
            return f"Error generating multi-modal response: {str(e)}"
    
    def generate_response(self, prompt):
        """Generate response - uses local or multi-modal based on model"""
        if self.current_model in AVAILABLE_MODELS and AVAILABLE_MODELS[self.current_model].get('is_multimodal'):
            return self.generate_response_multimodal(prompt)
        else:
            return self.generate_response_local(prompt)
    
    def send_message(self):
        """Send message and get response"""
        if not self.current_model:
            messagebox.showwarning("No Model", "Please select a model first from the dropdown")
            return
        
        user_input = self.input_text.get("1.0", tk.END).strip()
        
        if not user_input:
            messagebox.showwarning("Empty Message", "Please enter a message before sending.")
            return
        
        # Show disclaimer only once per session
        if not self.disclaimer_shown:
            response = messagebox.askyesno(
                "⚠️  CONFIRM - DISCLAIMER ⚠️",
                SKULL_CROSSBONES + "\n\nDo you accept these terms and wish to continue?"
            )
            
            if not response:
                return
            
            self.disclaimer_shown = True
        
        # Add user message
        self.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat(),
            "model": self.current_model,
            "has_image": self.current_image is not None or self.current_image_url is not None
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
            has_image = message.get("has_image", False)
            if timestamp:
                timestamp = timestamp.split("T")[1][:5]
            
            if message["role"] == "user":
                img_indicator = " 🖼️ " if has_image else " "
                self.chat_display.insert(tk.END, f"[{timestamp}] YOU:{img_indicator}", "user")
                self.chat_display.insert(tk.END, f"{message['content']}\n\n")
            else:
                self.chat_display.insert(tk.END, f"[{timestamp}] {model}: ", "assistant")
                self.chat_display.insert(tk.END, f"{message['content']}\n\n")
        
        self.chat_display.tag_config("user", foreground="#00ff00", font=("Courier", 11, "bold"))
        self.chat_display.tag_config("assistant", foreground="#ffaa00", font=("Courier", 11, "bold"))
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
