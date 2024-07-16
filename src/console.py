import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import importlib.util
import os
import sys
import subprocess
import sqlite3
import pygame
from PIL import Image, ImageTk
import cv2
import psutil

class GameConsole:
    def __init__(self, master):
        self.master = master
        self.master.title("Python Game Console")
        self.master.geometry("1000x800")

        self.game_frame = tk.Frame(self.master)
        self.game_frame.pack(fill=tk.BOTH, expand=True)

        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Load Game", command=self.load_game)

        self.config_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Config", menu=self.config_menu)

        self.debug_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Debug", menu=self.debug_menu)
        self.debug_menu.add_command(label="Toggle Input Debug", command=self.toggle_debug)

        self.current_game = None
        self.keyboard_config = None
        self.joystick_config = None
        self.current_process = None

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_folder = os.path.join(self.base_dir, "config")
        self.db_folder = os.path.join(self.base_dir, "config", "db")

        if not os.path.exists(self.config_folder):
            os.makedirs(self.config_folder)

        self.config_menu.add_command(label="Keyboard Config", command=self.open_keyboard_config)
        self.config_menu.add_command(label="Joystick Config", command=self.open_joystick_config)

        self.control_mapping = self.load_control_mapping()

        self.master.bind("<Key>", self.on_key_press)
        self.master.bind("<KeyRelease>", self.on_key_release)

        self.debug_active = False

        pygame.init()
        pygame.joystick.init()

        self.poll_joysticks()

        # Video labels
        self.startup_video_label = tk.Label(self.master)
        self.startup_video_label.pack(fill=tk.BOTH, expand=True)
        
        self.background_video_label = tk.Label(self.master)
        self.background_video_label.pack(fill=tk.BOTH, expand=True)
        self.background_video_label.lower()  # Put it behind the startup video

        self.master.bind("<Configure>", self.on_resize)

        self.play_startup_video()

    def play_startup_video(self):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        startup_video_path = os.path.join(base_dir, 'config', 'img', 'Py-GAME EMU.mp4')
        
        self.startup_cap = cv2.VideoCapture(startup_video_path)
        self.startup_video_width = int(self.startup_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.startup_video_height = int(self.startup_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.update_startup_video_frame()

    def update_startup_video_frame(self):
        ret, frame = self.startup_cap.read()
        if ret:
            frame = cv2.resize(frame, (self.master.winfo_width(), self.master.winfo_height()))
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.startup_video_label.imgtk = imgtk
            self.startup_video_label.configure(image=imgtk)
            self.master.after(33, self.update_startup_video_frame)  # About 30 FPS
        else:
            self.startup_cap.release()
            self.startup_video_label.pack_forget()
            self.play_background_video()

    def play_background_video(self):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        background_video_path = os.path.join(base_dir, 'config', 'img', 'background.mp4')
        
        self.background_cap = cv2.VideoCapture(background_video_path)
        self.background_video_width = int(self.background_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.background_video_height = int(self.background_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.update_background_video_frame()

    def update_background_video_frame(self):
        ret, frame = self.background_cap.read()
        if ret:
            frame = cv2.resize(frame, (self.master.winfo_width(), self.master.winfo_height()))
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.background_video_label.imgtk = imgtk
            self.background_video_label.configure(image=imgtk)
        else:
            self.background_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to the beginning of the video

        self.master.after(15, self.update_background_video_frame)  # About 30 FPS

    def on_resize(self, event):
        self.startup_video_width = event.width
        self.startup_video_height = event.height
        self.background_video_width = event.width
        self.background_video_height = event.height

 

    def on_key_press(self, event):
        if self.debug_active:
            print(f"Key pressed: {event.keysym}")

    def on_key_release(self, event):
        if self.debug_active:
            print(f"Key released: {event.keysym}")

    def poll_joysticks(self):
        if self.debug_active:
            for i in range(pygame.joystick.get_count()):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                
                for event in pygame.event.get():
                    if event.type == pygame.JOYBUTTONDOWN:
                        print(f"Joystick {event.joy} button {event.button} pressed")
                    elif event.type == pygame.JOYBUTTONUP:
                        print(f"Joystick {event.joy} button {event.button} released")
                    elif event.type == pygame.JOYAXISMOTION:
                        print(f"Joystick {event.joy} axis {event.axis} value: {event.value:.2f}")
                    elif event.type == pygame.JOYHATMOTION:
                        print(f"Joystick {event.joy} hat {event.hat} value: {event.value}")

        self.master.after(10, self.poll_joysticks)  # Poll every 10ms

    def load_game(self):
        game_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if game_path:
            self.run_game(game_path)

    def run_game(self, game_path):
        # Stop the background video
        if hasattr(self, 'video_after_id'):
            self.master.after_cancel(self.video_after_id)

        # Clear the background
        if self.background_video_label:
            self.background_video_label.pack_forget()
            self.background_video_label.destroy()
            self.background_video_label = None

        if hasattr(self, 'cap'):
            self.cap.release()

        if self.current_game:
            self.game_frame.destroy()
        
        self.game_frame = tk.Frame(self.master)
        self.game_frame.pack(fill=tk.BOTH, expand=True)

        spec = importlib.util.spec_from_file_location("game_module", game_path)
        game_module = importlib.util.module_from_spec(spec)
        sys.modules["game_module"] = game_module
        spec.loader.exec_module(game_module)

        if hasattr(game_module, 'run'):
            game_module.run(self.game_frame)
        else:
            print("The game module doesn't have a 'run' function.")

        self.current_game = game_path

    def open_keyboard_config(self):
        self.close_current_process()
        keyboard_config_path = os.path.join(self.config_folder, "keyboardConfig.py")
        if os.path.exists(keyboard_config_path):
            self.current_process = subprocess.Popen([sys.executable, keyboard_config_path])
            self.master.after(100, self.check_process)
        else:
            messagebox.showerror("Error", "Keyboard configuration file not found.")

    def open_joystick_config(self):
        self.close_current_process()
        joystick_config_path = os.path.join(self.config_folder, "joystick_config.py")
        if os.path.exists(joystick_config_path):
            self.current_process = subprocess.Popen([sys.executable, joystick_config_path])
            self.master.after(100, self.check_process)
        else:
            messagebox.showerror("Error", "Joystick configuration file not found.")

    def check_process(self):
        if self.current_process and self.current_process.poll() is None:
            self.master.after(100, self.check_process)
        else:
            self.close_current_process()

    def close_current_process(self):
        if self.current_process:
            try:
                parent = psutil.Process(self.current_process.pid)
                children = parent.children(recursive=True)
                for child in children:
                    child.terminate()
                    child.wait(timeout=5)
                parent.terminate()
                parent.wait(timeout=5)
            except psutil.NoSuchProcess:
                pass
            except psutil.TimeoutExpired:
                print("Timeout while terminating process. Force killing.")
                for child in children:
                    child.kill()
                parent.kill()
            finally:
                self.current_process = None
        
        import gc
        gc.collect()

    def load_control_mapping(self):
        control_mapping = {}

        keyboard_db_path = os.path.join(self.db_folder, "key_config.db")
        if os.path.exists(keyboard_db_path):
            conn = sqlite3.connect(keyboard_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT action, key FROM key_mappings")
            for action, key in cursor.fetchall():
                control_mapping[action] = {"type": "keyboard", "key": key}
            conn.close()

        joystick_db_path = os.path.join(self.config_folder, "joystick_config.db")
        if os.path.exists(joystick_db_path):
            conn = sqlite3.connect(joystick_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT joystick_id, action, button FROM joystick_mappings")
            for joystick_id, action, button in cursor.fetchall():
                control_mapping[action] = {"type": "joystick", "joystick_id": joystick_id, "button": button}
            conn.close()

        return control_mapping

    def toggle_debug(self):
        self.debug_active = not self.debug_active
        print(f"Debugging {'enabled' if self.debug_active else 'disabled'}")

if __name__ == "__main__":
    root = tk.Tk()
    console = GameConsole(root)
    root.mainloop()