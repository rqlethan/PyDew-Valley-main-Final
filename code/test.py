import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk

class ChatInterface:

    def __init__(self, master):
        self.master = master
        master.title("Chat Interface")

        # Load images for user and bot avatars
        self.load_avatars()

        # Text widget for the chat history
        self.chat_history = tk.Text(master, state='disabled', wrap='word')
        self.chat_history.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Entry widget for typing messages
        self.entry_message = tk.Entry(master)
        self.entry_message.grid(row=1, column=0, sticky="ew")

        # Button to send a message
        button_send = tk.Button(master, text="Send", command=self.send_message)
        button_send.grid(row=1, column=1)

        # Configure grid row/column weights so they adjust on resizing
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

    def load_avatars(self):
        # Replace 'user_avatar.png' and 'bot_avatar.png' with your image paths
        user_image = Image.open('../graphics/user.png')
        self.user_avatar = ImageTk.PhotoImage(user_image.resize((50, 50)))

        bot_image = Image.open('../graphics/ai.png')
        self.bot_avatar = ImageTk.PhotoImage(bot_image.resize((50, 50)))

    def display_message(self, message, sender):
        if not message:  # Don't display empty messages
            return
        
        self.chat_history.config(state='normal')

        # Insert message with appropriate alignment and margins
        if sender == "User":
            # User's messages are right-aligned with avatar on the left
            name_tag = 'user_name'
            msg_tag = 'user_msg'
            img_align = 'right'
            self.chat_history.tag_configure(msg_tag, justify='right', lmargin1=100, rmargin=50)
        else:
            # Bot's messages are left-aligned with avatar on the right
            name_tag = 'bot_name'
            msg_tag = 'bot_msg'
            img_align = 'left'
            self.chat_history.tag_configure(msg_tag, justify='left', lmargin1=50, rmargin=100)
        
        # Insert avatar
        avatar = self.user_avatar if sender == "User" else self.bot_avatar
        self.chat_history.insert(tk.END, '\n ')
        self.chat_history.image_create(tk.END, image=avatar, padx=10, align=img_align)

        # Add username and message text
        self.chat_history.insert(tk.END, ' ' * 5)
        self.chat_history.insert(tk.END, f'{sender}\n', name_tag)
        self.chat_history.insert(tk.END, f'{message}\n', msg_tag)
        
        self.chat_history.yview(tk.END)  # Auto-scroll to the end
        self.chat_history.config(state='disabled')  # Make the history read-only

    def send_message(self):
        message = self.entry_message.get()
        if message:
            self.display_message(message, "User")
            # Placeholder for bot response logic
            bot_response = "Echo: " + message
            self.display_message(bot_response, "Bot")
            self.entry_message.delete(0, tk.END)

# Run the GUI application
root = tk.Tk()
root.geometry("400x500")  # Set the size of the window
chat_interface = ChatInterface(root)
root.mainloop()