import pygame
import sys
import sqlite3
import os

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Keyboard Configuration")


def display_text(screen, text, position, font_size=20, color=(0, 255, 255)):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def draw_grid(screen, width, height, cell_size=20):
    for x in range(0, width, cell_size):
        pygame.draw.line(screen, (100, 100, 100), (x, 0), (x, height))
        display_text(screen, str(x), (x, 0), font_size=15, color= BLACK)
    for y in range(0, height, cell_size):
        pygame.draw.line(screen, (100, 100, 100), (0, y), (width, y))
        display_text(screen, str(y), (0, y), font_size=15, color= BLACK)


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LIGHT_BLUE = (173, 216, 230)

# Font
font = pygame.font.Font(None, 26)

# Keyboard layout (simplified)
keys = [
    ['1','2','3','4','5','6','7','8','9','0'],
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    ['LShft','Z', 'X', 'C', 'V', 'B', 'N', 'M','RShft']
]
spacebtn = ['SPACE']

Arrowkeys = [
    ['UP'], 
    ['LEFT','DOWN', 'RIGHT']
]

# Game actions
game_actions = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'SPACE']


# Key configuration
key_config = {}

# Done button
done_button = pygame.Rect(WIDTH - 120, HEIGHT - 60, 100, 40)

# Function to get the database path
def get_db_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the main Python file
    db_dir = os.path.join(base_dir, 'db')  # Create 'db' directory path
    os.makedirs(db_dir, exist_ok=True)  # Create 'db' directory if it doesn't exist
    db_path = os.path.join(db_dir, 'key_config.db')  # Define the database file path
    return db_path

# Database setup
def setup_database():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS key_mappings
                 (action TEXT PRIMARY KEY, key TEXT)''')
    conn.commit()
    conn.close()

def save_config_to_db():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    for action, key in key_config.items():
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


#drawing functions

def draw_keyboard():
    start_x, start_y = 100, 50  # Starting position for the keyboard
    key_size = 50
    spacing = 10
    
    for i, row in enumerate(keys):
        for j, key in enumerate(row):
            x = start_x + j * (key_size + spacing)
            y = start_y + i * (key_size + spacing)
            
            color = RED if key in key_config.values() else GRAY
            pygame.draw.rect(screen, color, (x, y, key_size, key_size))
            text = font.render(key, True, BLACK)
            screen.blit(text, (x + key_size//2 - text.get_width()//2, y + key_size//2 - text.get_height()//2))


def draw_space():
    x, y = 220, 300
    key_size = 30
    width = 300  # Make the space bar wider
    
    key = spacebtn[0]
    color = RED if key in key_config.values() else GRAY
    pygame.draw.rect(screen, color, (x, y, width, key_size))
    text = font.render(key, True, BLACK)
    screen.blit(text, (x + width//2 - text.get_width()//2, y + key_size//2 - text.get_height()//2))



def draw_arrow_keys():
    start_x, start_y = 590, 240
    key_size = 45
    spacing = 10
    
    for i, row in enumerate(Arrowkeys):
        for j, key in enumerate(row):
            x = start_x + j * (key_size + spacing)
            y = start_y + i * (key_size + spacing)
            
            if key == 'UP':
                x = start_x + key_size + spacing  # Center the UP key
            
            color = RED if key in key_config.values() else GRAY
            pygame.draw.rect(screen, color, (x, y, key_size, key_size))
            text = font.render(key, True, BLACK)
            screen.blit(text, (x + key_size//2 - text.get_width()//2, y + key_size//2 - text.get_height()//2))

def draw_config_panel():
    x, y = 780, 0
    width, height = 420, 600
    pygame.draw.rect(screen, LIGHT_BLUE, (x, y, width, height))
    
    title = font.render("Configuration Panel", True, BLACK)
    screen.blit(title, (x + 10, y + 10))
    
    for i, action in enumerate(game_actions):
        action_y = y + 50 + i * 40
        text = font.render(f"{action}: {key_config.get(action, 'Not Set')}", True, BLACK)
        screen.blit(text, (x + 10, action_y))

def draw_done_button():
    pygame.draw.rect(screen, GREEN, done_button)
    text = font.render("DONE", True, BLACK)
    screen.blit(text, (done_button.centerx - text.get_width() // 2, done_button.centery - text.get_height() // 2))

def get_clicked_key(pos):
    # Check main keyboard
    start_x, start_y = 100, 50
    key_size = 50
    spacing = 10
    for i, row in enumerate(keys):
        for j, key in enumerate(row):
            x = start_x + j * (key_size + spacing)
            y = start_y + i * (key_size + spacing)
            if pygame.Rect(x, y, key_size, key_size).collidepoint(pos):
                return key

            # Check arrow keys
    start_x, start_y = 590, 240
    key_size = 45
    spacing = 10
    for i, row in enumerate(Arrowkeys):
        for j, key in enumerate(row):
            x = start_x + j * (key_size + spacing)
            y = start_y + i * (key_size + spacing)
            if key == 'UP':
                x = start_x + key_size + spacing  # Center the UP key
            if pygame.Rect(x, y, key_size, key_size).collidepoint(pos):
                return key
            
    # Check space button
    space_x, space_y = 220, 300
    space_width = 300
    if pygame.Rect(space_x, space_y, space_width, key_size).collidepoint(pos):
        return spacebtn[0]
    

    return None

def configure_key(action):
    print(f"Please press a key to configure for {action}...")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key).upper()
                key_config[action] = key_name
                print(f"Button configured for {action}: {key_name}")
                waiting = False
                break

def display_config_summary():
    print("\nFinal Key Configuration:")
    for action, key in key_config.items():
        print(f"{action}: {key}")

def main():
    setup_database()
    global key_config
    key_config = load_config_from_db()
    
    configuring = False
    current_action = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_config_to_db()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if done_button.collidepoint(event.pos):
                    save_config_to_db()
                    display_config_summary()
                    pygame.quit()
                    sys.exit()
                elif not configuring:
                    x, y = event.pos
                    if 780 <= x <= 1200:  # Click in config panel
                        action_index = (y - 50) // 40
                        if 0 <= action_index < len(game_actions):
                            current_action = game_actions[action_index]
                            configuring = True
                            configure_key(current_action)
                            configuring = False
                    else:
                        clicked_key = get_clicked_key(event.pos)
                        if clicked_key:
                            configuring = True
                            current_action = clicked_key
                            configure_key(current_action)
                            configuring = False

        screen.fill(WHITE)
        #draw_grid(screen,WIDTH, HEIGHT) #grid for debugging purposes
        draw_keyboard()
        draw_space()
        draw_arrow_keys()
        draw_config_panel()
        draw_done_button()
        

        # Display instructions
        instructions = font.render("Click a key to configure", True, BLACK)
        screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 100))

        pygame.display.flip()

if __name__ == "__main__":
    main()