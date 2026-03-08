import tkinter as tk
from tkinter import messagebox

class ChatApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Huggingface Chat App")
        self.frame = tk.Frame(self.master)
        self.frame.pack()

        self.text_area = tk.Text(self.frame, width=60, height=20, bg="gray", fg="white")
        self.text_area.pack(side=tk.LEFT)

        self.input_field = tk.Entry(self.frame, width=40)
        self.input_field.pack(side=tk.LEFT)

        self.send_button = tk.Button(self.frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT)

    def send_message(self):
        message = self.input_field.get()
        with open('models/conversations.txt', 'a') as f:
            f.write(message + '\n')
        self.text_area.insert(tk.END, "You: " + message + "\n")
        self.input_field.delete(0, tk.END)

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.chat_app = ChatApp(self.root)
        self.load_conversations()

    def load_conversations(self):
        with open('models/conversations.txt', 'r') as f:
            conversation_text = f.read()
        self.chat_app.text_area.insert(tk.END, conversation_text)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.run()
