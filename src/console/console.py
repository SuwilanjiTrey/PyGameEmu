import os
import sys
import tkinter as tk
from tkinter import filedialog
import pygame
from pygame.locals import *

class PygameFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pygame_running = False
        self.pygame_frame = tk.Frame(self)
        self.pygame_frame.pack(fill=tk.BOTH, expand=True)
        
        self.embed = tk.Frame(self.pygame_frame, width=800, height=600)  # Set the dimensions
        self.embed.pack()
        
        self.embed_id = self.embed.winfo_id()
        os.environ['SDL_WINDOWID'] = str(self.embed_id)
        
        pygame.display.init()
        self.screen = pygame.display.set_mode((800, 600))

    def start_pygame(self, game_path):
        self.pygame_running = True
        self.run_game(game_path)

    def run_game(self, game_path):
        # Import the game module dynamically
        game_module = __import__(game_path)
        game_module.main(self.screen)  # Assuming each game has a main(screen) function

        # Handle events in a loop
        while self.pygame_running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.pygame_running = False
                game_module.handle_event(event)
            
            game_module.update()
            pygame.display.flip()
            pygame.time.Clock().tick(30)

def select_game():
    game_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
    if game_path:
        game_name = os.path.basename(game_path).replace('.py', '')
        sys.path.insert(0, os.path.dirname(game_path))
        frame.start_pygame(game_name)

def main():
    root = tk.Tk()
    root.title("Pygame Console")
    root.geometry("1024x768")
    
    global frame
    frame = PygameFrame(root)
    frame.pack(fill=tk.BOTH, expand=True)
    
    menu = tk.Menu(root)
    root.config(menu=menu)
    file_menu = tk.Menu(menu)
    menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Open Game", command=select_game)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    
    root.mainloop()

if __name__ == "__main__":
    main()
