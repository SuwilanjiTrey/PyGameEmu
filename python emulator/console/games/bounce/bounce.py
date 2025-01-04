import pygame
import tkinter as tk
from PIL import Image, ImageTk
from pygame.math import Vector2
import sqlite3
import os

class Ball:
    def __init__(self, pos, vel):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.radius = 20

    def update(self, dt, width, height):
        self.pos += self.vel * dt
        if self.pos.x - self.radius < 0 or self.pos.x + self.radius > width:
            self.vel.x *= -1
        if self.pos.y - self.radius < 0 or self.pos.y + self.radius > height:
            self.vel.y *= -1

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 0, 0), (int(self.pos.x), int(self.pos.y)), self.radius)

def get_db_path(db_name):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    db_dir = os.path.join(base_dir, 'config', 'db')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, db_name)

def load_config_from_db():
    conn = sqlite3.connect(get_db_path('key_config.db'))
    c = conn.cursor()
    c.execute("SELECT * FROM key_mappings")
    rows = c.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def load_joystick_config_from_db():
    config = {}
    with sqlite3.connect(get_db_path('joystick_config.db')) as conn:
        for joystick_id, action, button in conn.execute("SELECT * FROM joystick_mappings"):
            config.setdefault(joystick_id, {})[action] = button
    return config

def run(frame):
    width, height = 1000, 800
    game_frame = tk.Frame(frame, width=width, height=height)
    game_frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(game_frame, width=width, height=height)
    canvas.pack(fill=tk.BOTH, expand=True)

    control_mapping = {}
    game_running = False
    button_frame = None
    exit_button = None
    ball = None

    def create_exit_button():
        nonlocal exit_button
        exit_button = tk.Button(game_frame, text="Exit Game", command=stop_game)
        exit_button.place(x=10, y=10)

    def stop_game():
        nonlocal game_running
        game_running = False
        pygame.quit()
        game_frame.destroy()
        frame.update()
    # Call the cleanup_game method of the parent GameConsole instance
        #frame.master.cleanup_game()

    def show_menu():
        nonlocal button_frame
        button_frame = tk.Frame(canvas)
        button_frame.place(relx=0.5, rely=0.5, anchor="center")

        keyboard_button = tk.Button(button_frame, text="Keyboard", command=lambda: select_control("keyboard"))
        keyboard_button.pack(side=tk.LEFT, padx=20)

        joystick_button = tk.Button(button_frame, text="Joystick", command=lambda: select_control("joystick"))
        joystick_button.pack(side=tk.RIGHT, padx=20)

    def select_control(control_type):
        control_mapping["type"] = control_type
        button_frame.destroy()
        start_game()

    def start_game():
        nonlocal game_running, ball
        canvas.delete("all")
        create_exit_button()
        
        pygame.init()
        pygame.joystick.init()
        joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for joystick in joysticks:
            joystick.init()

        clock = pygame.time.Clock()
        surface = pygame.Surface((width, height))
        ball = Ball((width // 2, height // 2), (0, 0))
        move_speed = 300
        
        key_config = load_config_from_db()
        joystick_config = load_joystick_config_from_db()
        print("Loaded key configuration:", key_config)
        print("Loaded joystick configuration:", joystick_config)
        
        control_type = control_mapping.get("type", "keyboard")
        print(f"Selected control type: {control_type}")

        game_running = True

        def update():
            if not game_running:
                return

            dt = clock.tick(60) / 1000.0

            handle_events()
            ball.update(dt, width, height)

            surface.fill((255, 255, 255))
            ball.draw(surface)

            pygame_image = pygame.image.tostring(surface, 'RGB')
            pil_image = Image.frombytes('RGB', (width, height), pygame_image)
            tk_image = ImageTk.PhotoImage(pil_image)

            canvas.delete("all")
            canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
            canvas.image = tk_image

            if game_running:
                game_frame.after(16, update)

        def on_key_press(event):
            if control_mapping["type"] != "keyboard":
                return
            key_pressed = event.keysym.upper()
            print(f"Key pressed: {key_pressed}")
            if key_pressed == key_config.get("UP"):
                ball.vel.y = -move_speed
            elif key_pressed == key_config.get("DOWN"):
                ball.vel.y = move_speed
            elif key_pressed == key_config.get("LEFT"):
                ball.vel.x = -move_speed
            elif key_pressed == key_config.get("RIGHT"):
                ball.vel.x = move_speed

        def on_key_release(event):
            if control_mapping["type"] != "keyboard":
                return
            key_released = event.keysym.upper()
            print(f"Key released: {key_released}")
            if key_released in {key_config.get("UP"), key_config.get("DOWN")}:
                ball.vel.y = 0
            elif key_released in {key_config.get("LEFT"), key_config.get("RIGHT")}:
                ball.vel.x = 0

        def handle_events():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stop_game()

            if control_mapping["type"] == "joystick":
                for joystick_id, joystick in enumerate(joysticks):
                    if joystick_id in joystick_config:
                        for action, button in joystick_config[joystick_id].items():
                            if 'ax' in button:
                                axis = int(button[-1])
                                value = joystick.get_axis(axis)
                                if action == 'up' and value < -0.5:
                                    ball.vel.y = -move_speed
                                elif action == 'down' and value > 0.5:
                                    ball.vel.y = move_speed
                                elif action == 'left' and value < -0.5:
                                    ball.vel.x = -move_speed
                                elif action == 'right' and value > 0.5:
                                    ball.vel.x = move_speed
                            elif 'hat' in button:
                                hat = joystick.get_hat(0)
                                if action == 'up' and hat[1] == 1:
                                    ball.vel.y = -move_speed
                                elif action == 'down' and hat[1] == -1:
                                    ball.vel.y = move_speed
                                elif action == 'left' and hat[0] == -1:
                                    ball.vel.x = -move_speed
                                elif action == 'right' and hat[0] == 1:
                                    ball.vel.x = move_speed
                            elif 'action' in button:
                                button_num = int(button.replace('action', ''))
                                if joystick.get_button(button_num):
                                    if action == 'action1':
                                        ball.vel.y = -move_speed
                                    elif action == 'action2':
                                        ball.vel.y = move_speed
                                    elif action == 'action3':
                                        ball.vel.x = -move_speed
                                    elif action == 'action4':
                                        ball.vel.x = move_speed
                            else:
                                try:
                                    button_num = int(button)
                                    if joystick.get_button(button_num):
                                        if action == 'up':
                                            ball.vel.y = -move_speed
                                        elif action == 'down':
                                            ball.vel.y = move_speed
                                        elif action == 'left':
                                            ball.vel.x = -move_speed
                                        elif action == 'right':
                                            ball.vel.x = move_speed
                                except ValueError:
                                    pass

        game_frame.bind("<KeyPress>", on_key_press)
        game_frame.bind("<KeyRelease>", on_key_release)

        game_frame.focus_set()
        update()

    show_menu()

if __name__ == "__main__":
    root = tk.Tk()
    run(root)
    root.mainloop()