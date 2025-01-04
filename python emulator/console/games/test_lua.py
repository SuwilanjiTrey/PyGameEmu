import tkinter as tk
import subprocess
import os
import signal

class Love2DGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Love2D Game Controller")

        self.start_button = tk.Button(root, text="Start Game", command=self.start_game)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Stop Game", command=self.stop_game)
        self.stop_button.pack()
        self.stop_button.config(state=tk.DISABLED)

        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)

        self.game_process = None

    def start_game(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        lua_file_path = os.path.join(script_dir,"simple_game")
        self.game_process = subprocess.Popen(["love", lua_file_path])
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_game(self):
        if self.game_process:
            self.game_process.send_signal(signal.SIGTERM)
            self.game_process = None
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def key_press(self, event):
        if self.game_process:
            key = event.keysym
            self.send_key_to_game(key, "down")

    def key_release(self, event):
        if self.game_process:
            key = event.keysym
            self.send_key_to_game(key, "up")

    def send_key_to_game(self, key, action):
        # Here you could implement a method to send the keypress to the Love2D game,
        # for instance by using IPC (Inter-process communication) or simulating keypresses.
        # This is a simplified example and won't work out-of-the-box.
        print(f"Send key {key} {action} to game")

if __name__ == "__main__":
    root = tk.Tk()
    app = Love2DGameApp(root)
    root.mainloop()
