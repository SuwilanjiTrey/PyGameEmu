import tkinter as tk
from tkinter import filedialog, messagebox
import importlib.util
import os
import sys
import subprocess
import sqlite3

class GameConsole:
    def __init__(self, master):
        self.master = master
        self.master.title("Python Game Console")
        self.master.geometry("800x600")

        self.game_frame = tk.Frame(self.master)
        self.game_frame.pack(fill=tk.BOTH, expand=True)

        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Load Game", command=self.load_game)

        self.config_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Config", menu=self.config_menu)

        self.current_game = None
        self.keyboard_config = None
        self.joystick_config = None

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_folder = os.path.join(self.base_dir, "config")
        self.db_folder = os.path.join(self.base_dir, "config", "db")

        # Ensure config folder exists
        if not os.path.exists(self.config_folder):
            os.makedirs(self.config_folder)

        self.config_menu.add_command(label="Keyboard Config", command=self.open_keyboard_config)
        self.config_menu.add_command(label="Joystick Config", command=self.open_joystick_config)

        # Load control configurations
        self.control_mapping = self.load_control_mapping()

        self.master.bind("<Key>", self.on_key_press)

    def on_key_press(self, event):
        print(f"Key pressed: {event.keysym}")

    def load_game(self):
        game_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if game_path:
            self.run_game(game_path)

    def run_game(self, game_path):
        if self.current_game:
            self.game_frame.destroy()
            self.game_frame = tk.Frame(self.master)
            self.game_frame.pack(fill=tk.BOTH, expand=True)

        spec = importlib.util.spec_from_file_location("game_module", game_path)
        game_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(game_module)

        if hasattr(game_module, 'run'):
            # Pass the control mapping to the game
            game_module.run(self.game_frame)
        else:
            print("The game module doesn't have a 'run' function.")

    def open_keyboard_config(self):
        keyboard_config_path = os.path.join(self.config_folder, "keyboardConfig.py")
        if os.path.exists(keyboard_config_path):
            subprocess.Popen([sys.executable, keyboard_config_path])
        else:
            messagebox.showerror("Error", "Keyboard configuration file not found.")

    def open_joystick_config(self):
        joystick_config_path = os.path.join(self.config_folder, "joystick_config.py")
        if os.path.exists(joystick_config_path):
            subprocess.Popen([sys.executable, joystick_config_path])
        else:
            messagebox.showerror("Error", "Joystick configuration file not found.")

    def load_control_mapping(self):
        control_mapping = {}

        # Load keyboard mappings
        keyboard_db_path = os.path.join(self.db_folder, "key_config.db")
        if os.path.exists(keyboard_db_path):
            conn = sqlite3.connect(keyboard_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT action, key FROM key_mappings")
            for action, key in cursor.fetchall():
                control_mapping[action] = {"type": "keyboard", "key": key}
            conn.close()

        # Load joystick mappings
        joystick_db_path = os.path.join(self.config_folder, "joystick_config.db")
        if os.path.exists(joystick_db_path):
            conn = sqlite3.connect(joystick_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT joystick_id, action, button FROM joystick_mappings")
            for joystick_id, action, button in cursor.fetchall():
                control_mapping[action] = {"type": "joystick", "joystick_id": joystick_id, "button": button}
            conn.close()

        return control_mapping

if __name__ == "__main__":
    root = tk.Tk()
    console = GameConsole(root)
    root.mainloop()
