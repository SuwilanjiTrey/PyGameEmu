import tkinter as tk
from tkinter import messagebox
import pygame
import sys
import sqlite3
import os

# Initialize Pygame
pygame.init()

# Database setup for keyboard configuration
def get_db_path():
    # Get the base directory one level up from the current file
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_dir = os.path.join(base_dir, 'config', 'db')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'key_config.db')


def setup_database():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS key_mappings
                 (action TEXT PRIMARY KEY, key TEXT)''')
    conn.commit()
    conn.close()

def save_config_to_db(config):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    for action, key in config.items():
        c.execute("INSERT OR REPLACE INTO key_mappings VALUES (?, ?)", (action, key))
    conn.commit()
    conn.close()

def load_config_from_db():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("SELECT * FROM key_mappings")
    rows = c.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

# Function to get the pygame key constant
def get_pygame_key(key):
    # Map arrow keys to Pygame constants
    if key == 'UP':
        return pygame.K_UP
    elif key == 'DOWN':
        return pygame.K_DOWN
    elif key == 'LEFT':
        return pygame.K_LEFT
    elif key == 'RIGHT':
        return pygame.K_RIGHT
    else:
        # Convert other keys to Pygame format
        return getattr(pygame, f'K_{key.lower()}', None)

# Keyboard configuration module using Pygame
def configure_keyboard():
    WIDTH, HEIGHT = 600, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Keyboard Configuration")

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GRAY = (200, 200, 200)

    font = pygame.font.Font(None, 36)

    game_actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    key_config = load_config_from_db()

    done_button = pygame.Rect(WIDTH - 120, HEIGHT - 60, 100, 40)

    def draw_config_panel():
        screen.fill(WHITE)
        for i, action in enumerate(game_actions):
            y = 50 + i * 50
            text = font.render(f"{action}: {key_config.get(action, 'Not Set')}", True, BLACK)
            screen.blit(text, (50, y))
        pygame.draw.rect(screen, (0, 255, 0), done_button)
        done_text = font.render("DONE", True, BLACK)
        screen.blit(done_text, (done_button.x + 20, done_button.y + 10))
        pygame.display.flip()

    def configure_key(action):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    key_name = pygame.key.name(event.key).upper()
                    key_config[action] = key_name
                    waiting = False

    running = True
    configuring = False
    current_action = None

    while running:
        draw_config_panel()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_config_to_db(key_config)
                pygame.quit()
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if done_button.collidepoint(event.pos):
                    save_config_to_db(key_config)
                    pygame.quit()
                    running = False
                else:
                    for i, action in enumerate(game_actions):
                        if 50 + i * 50 <= event.pos[1] <= 50 + i * 50 + 40:
                            current_action = action
                            configuring = True
                            break
            if configuring:
                configure_key(current_action)
                configuring = False

# Main game logic
def start_game():
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game Window")

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    font = pygame.font.Font(None, 36)

    player_pos = [WIDTH // 2, HEIGHT // 2]
    player_speed = 5

    key_config = load_config_from_db()

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

        if keys[get_pygame_key(key_config.get("UP", ""))]:
            player_pos[1] -= player_speed
        if keys[get_pygame_key(key_config.get("DOWN", ""))]:
            player_pos[1] += player_speed
        if keys[get_pygame_key(key_config.get("LEFT", ""))]:
            player_pos[0] -= player_speed
        if keys[get_pygame_key(key_config.get("RIGHT", ""))]:
            player_pos[0] += player_speed

# Tkinter main window
root = tk.Tk()
root.title("Game Launcher")

start_button = tk.Button(root, text="Start Game", command=start_game)
start_button.pack(pady=20)

config_button = tk.Button(root, text="Config", command=configure_keyboard)
config_button.pack(pady=20)

root.mainloop()
