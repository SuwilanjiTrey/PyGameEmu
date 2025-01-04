import pygame
from pygame.math import Vector2
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk
import sqlite3
import os

class Player:
    def __init__(self, pos):
        self.pos = Vector2(pos)
        self.size = 40
        self.color = (0, 255, 0)
        self.speed = 200

    def move(self, direction, dt):
        self.pos += direction * self.speed * dt

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (int(self.pos.x), int(self.pos.y), self.size, self.size))

class ControlTester:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.player = Player((width // 2, height // 2))
        self.font = pygame.font.Font(None, 36)
        self.last_action = None

    def handle_input(self, control_mapping, dt):
        keys = pygame.key.get_pressed()
        direction = Vector2(0, 0)

        if control_mapping['type'] == 'keyboard':
            if control_mapping.get('UP', {}).get('key') and keys[getattr(pygame, control_mapping['UP']['key'])]:
                direction.y -= 1
            if control_mapping.get('DOWN', {}).get('key') and keys[getattr(pygame, control_mapping['DOWN']['key'])]:
                direction.y += 1
            if control_mapping.get('LEFT', {}).get('key') and keys[getattr(pygame, control_mapping['LEFT']['key'])]:
                direction.x -= 1
            if control_mapping.get('RIGHT', {}).get('key') and keys[getattr(pygame, control_mapping['RIGHT']['key'])]:
                direction.x += 1

            if control_mapping.get('action', {}).get('key') and keys[getattr(pygame, control_mapping['action']['key'])]:
                self.last_action = "Action pressed!"
        
        elif control_mapping['type'] == 'joystick':
            joystick = pygame.joystick.Joystick(control_mapping['joystick_id'])
            joystick.init()

            # Assuming axes 0 and 1 are for movement
            direction.x = joystick.get_axis(0)
            direction.y = joystick.get_axis(1)

            if joystick.get_button(control_mapping['action']['button']):
                self.last_action = "Action pressed!"

        if direction.length() > 0:
            direction = direction.normalize()
        self.player.move(direction, dt)

    def update(self, dt):
        self.player.pos.x = max(0, min(self.width - self.player.size, self.player.pos.x))
        self.player.pos.y = max(0, min(self.height - self.player.size, self.player.pos.y))

    def draw(self, surface):
        surface.fill((255, 255, 255))
        self.player.draw(surface)
        if self.last_action:
            text = self.font.render(self.last_action, True, (255, 0, 0))
            surface.blit(text, (10, 10))

def load_control_mapping(control_type):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_folder = os.path.join(base_dir, "config", "db")
    
    control_mapping = {'type': control_type}

    if control_type == 'keyboard':
        db_path = os.path.join(db_folder, "key_config.db")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT action, key FROM key_mappings")
            for action, key in cursor.fetchall():
                control_mapping[action] = {'key': key}
            conn.close()
    
    elif control_type == 'joystick':
        db_path = os.path.join(db_folder, "joystick_config.db")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT joystick_id, action, button FROM joystick_mappings")
            for joystick_id, action, button in cursor.fetchall():
                if 'joystick_id' not in control_mapping:
                    control_mapping['joystick_id'] = joystick_id
                control_mapping[action] = {'button': button}
            conn.close()

    return control_mapping

def run(frame):
    width, height = 800, 600
    canvas = tk.Canvas(frame, width=width, height=height)
    canvas.pack()

    # Ask user for control type
    control_type = simpledialog.askstring("Input", "Choose control type (keyboard/joystick):", 
                                          parent=frame)
    
    if control_type not in ['keyboard', 'joystick']:
        print("Invalid control type. Defaulting to keyboard.")
        control_type = 'keyboard'

    control_mapping = load_control_mapping(control_type)

    pygame.init()
    if control_type == 'joystick':
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            print("No joystick detected. Defaulting to keyboard.")
            control_type = 'keyboard'
            control_mapping = load_control_mapping('keyboard')

    clock = pygame.time.Clock()
    surface = pygame.Surface((width, height))
    game = ControlTester(width, height)

    def update():
        nonlocal surface, canvas

        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        game.handle_input(control_mapping, dt)
        game.update(dt)
        game.draw(surface)

        # Convert Pygame surface to PIL Image
        pygame_image = pygame.image.tostring(surface, 'RGB')
        pil_image = Image.frombytes('RGB', (width, height), pygame_image)

        # Convert PIL Image to ImageTk
        tk_image = ImageTk.PhotoImage(pil_image)

        canvas.delete("all")
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
        canvas.image = tk_image  # Keep a reference

        frame.after(16, update)  # Schedule the next update

    update()  # Start the update loop

# This part is for testing the game standalone
if __name__ == "__main__":
    root = tk.Tk()
    run(root)
    root.mainloop()