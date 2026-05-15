import os
import requests
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('HUGGINGFACE_API_KEY')
API_URL = 'https://router.huggingface.co'

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

class HuggingFaceChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Hugging Face Chat App")
        self.root.geometry("900x700")
        self.root.configure(bg="#1e1e1e")
        
        # Chat history
        self.chat_history = []
        self.session_file = "chat_history.json"
        self.load_chat_history()
        
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
            height=15,
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
            height=4,
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
        
        # Style for buttons
        self.setup_button_styles()
        
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
        self.status_var = tk.StringVar(value="Ready | API: Connected" if API_KEY else "Ready | ⚠️  API Key not found")
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
        
    def setup_button_styles(self):
        """Setup button styling"""
        pass
    
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
    
    def call_inference_api(self, prompt):
        """Call the Hugging Face Inference API"""
        if not API_KEY:
            return "Error: HUGGINGFACE_API_KEY not set in .env file"
        
        try:
            headers = {'Authorization': f'Bearer {API_KEY}'}
            data = {
                "inputs": prompt,
                "parameters": {}
            }
            response = requests.post(API_URL, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], dict) and 'generated_text' in result[0]:
                        return result[0]['generated_text']
                return str(result)
            else:
                return f"API Error: {response.status_code} - {response.text}"
        except requests.exceptions.Timeout:
            return "Error: Request timed out. Try a shorter prompt."
        except Exception as e:
            return f"Error calling API: {str(e)}"
    
    def send_message(self):
        """Send message and get response from API"""
        user_input = self.input_text.get("1.0", tk.END).strip()
        
        if not user_input:
            messagebox.showwarning("Empty Message", "Please enter a message before sending.")
            return
        
        # Show disclaimer before sending
        response = messagebox.askyesno(
            "⚠️  CONFIRM - DISCLAIMER ⚠️",
            SKULL_CROSSBONES + "\n\nDo you accept these terms and wish to continue?"
        )
        
        if not response:
            return
        
        # Add user message to history
        self.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        self.status_var.set("Loading... Please wait")
        self.root.update()
        
        # Get AI response
        ai_response = self.call_inference_api(user_input)
        
        # Add AI response to history
        self.chat_history.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save and refresh
        self.save_chat_history()
        self.refresh_chat_display()
        self.input_text.delete("1.0", tk.END)
        self.status_var.set("Ready")
    
    def refresh_chat_display(self):
        """Refresh the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        
        for message in self.chat_history:
            timestamp = message.get("timestamp", "")
            if timestamp:
                timestamp = timestamp.split("T")[1][:5]  # HH:MM format
            
            if message["role"] == "user":
                self.chat_display.insert(tk.END, f"[{timestamp}] YOU: ", "user")
                self.chat_display.insert(tk.END, f"{message['content']}\n\n")
            else:
                self.chat_display.insert(tk.END, f"[{timestamp}] AI: ", "assistant")
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
    if not API_KEY:
        messagebox.showerror(
            "Missing API Key",
            "HUGGINGFACE_API_KEY not found in .env file.\n\n"
            "Please create a .env file with:\nHUGGINGFACE_API_KEY=your_key_here"
        )
    
    root = tk.Tk()
    app = HuggingFaceChatApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
