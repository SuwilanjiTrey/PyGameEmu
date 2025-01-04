import tkinter as tk
import pygame
import sys
import sqlite3
import os

# Initialize Pygame
pygame.init()

# Database setup for joystick configuration
def get_db_path():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_dir = os.path.join(base_dir, 'config', 'db')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'joystick_config.db')

def load_joystick_config_from_db():
    config = {}
    with sqlite3.connect(get_db_path()) as conn:
        for joystick_id, action, button in conn.execute("SELECT * FROM joystick_mappings"):
            config.setdefault(joystick_id, {})[action] = button
    return config

# Main game logic
def start_game():
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game Window")

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    player_pos = [WIDTH // 2, HEIGHT // 2]
    player_speed = 5

    joystick_config = load_joystick_config_from_db()

    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    for joystick in joysticks:
        joystick.init()

    running = True
    while running:
        screen.fill(WHITE)
        pygame.draw.circle(screen, BLACK, player_pos, 20)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

        # Handle joystick input
        for joystick_id, joystick in enumerate(joysticks):
            if joystick_id in joystick_config:
                for action, button in joystick_config[joystick_id].items():
                    if 'ax' in button:
                        axis = int(button[-1])
                        value = joystick.get_axis(axis)
                        if action == 'up' and value < -0.5:
                            player_pos[1] -= player_speed
                        elif action == 'down' and value > 0.5:
                            player_pos[1] += player_speed
                        elif action == 'left' and value < -0.5:
                            player_pos[0] -= player_speed
                        elif action == 'right' and value > 0.5:
                            player_pos[0] += player_speed
                    elif 'hat' in button:
                        hat = joystick.get_hat(0)
                        if action == 'up' and hat[1] == 1:
                            player_pos[1] -= player_speed
                        elif action == 'down' and hat[1] == -1:
                            player_pos[1] += player_speed
                        elif action == 'left' and hat[0] == -1:
                            player_pos[0] -= player_speed
                        elif action == 'right' and hat[0] == 1:
                            player_pos[0] += player_speed
                    elif 'action' in button:
                        button_num = int(button.replace('action', ''))
                        if joystick.get_button(button_num):
                            if action == 'action1':
                                player_pos[1] -= player_speed
                            elif action == 'action2':
                                player_pos[1] += player_speed
                            elif action == 'action3':
                                player_pos[0] -= player_speed
                            elif action == 'action4':
                                player_pos[0] += player_speed
                    else:
                        try:
                            button_num = int(button)
                            if joystick.get_button(button_num):
                                if action == 'up':
                                    player_pos[1] -= player_speed
                                elif action == 'down':
                                    player_pos[1] += player_speed
                                elif action == 'left':
                                    player_pos[0] -= player_speed
                                elif action == 'right':
                                    player_pos[0] += player_speed
                        except ValueError:
                            pass

# Tkinter main window
root = tk.Tk()
root.title("Game Launcher")

start_button = tk.Button(root, text="Start Game", command=start_game)
start_button.pack(pady=20)

root.mainloop()
