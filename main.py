import os
import tkinter as tk
from tkinter import messagebox

# File initialization logic
FILE_PATH = 'data.txt'  # The path to your data file
try:
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'w') as f:
            f.write('')  # Initialize the file if it doesn't exist
except Exception as e:
    messagebox.showerror('File Error', f'Error initializing the file: {e}')

class ChatApp:
    def __init__(self, master):
        self.master = master
        master.title('Chat Application')

        # GUI Layout - Widgets stacked vertically
        self.label = tk.Label(master, text='Chat Application')
        self.label.pack()  # Stack label at the top

        self.text_area = tk.Text(master, height=10, width=50)
        self.text_area.pack()  # Stack text area next

        self.entry = tk.Entry(master)
        self.entry.pack()  # Stack entry at the bottom

        self.send_button = tk.Button(master, text='Send', command=self.send_message)
        self.send_button.pack()  # Stack button below the entry

    def send_message(self):
        message = self.entry.get()
        if message:
            self.text_area.insert(tk.END, f'You: {message}\n')
            self.entry.delete(0, tk.END)
        else:
            messagebox.showwarning('Input Error', 'Please enter a message.')

if __name__ == '__main__':
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()