import pygame
import sys
import sqlite3
import os
from controls import UniversalController

pygame.init()

WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Joystick Configuration")
controller = UniversalController()

WHITE, BLACK, GRAY, RED, GREEN, LIGHT_BLUE = (255, 255, 255), (0, 0, 0), (200, 200, 200), (255, 0, 0), (0, 255, 0), (173, 216, 230)

font = pygame.font.Font(None, 26)

game_actions = ['up', 'down', 'left', 'right', 'action1', 'action2', 'action3', 'action4', 'action5', 'action6',
                'action7', 'action8', 'action9', 'action10', 'action11', 'action12', 'action13', 'action14',
                'axUp', 'axDown', 'axleft', 'axright']

joystick_config = {}
done_button = pygame.Rect(WIDTH - 120, HEIGHT - 60, 100, 40)

def get_db_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(base_dir, 'db')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'joystick_config.db')

def setup_database():
    with sqlite3.connect(get_db_path()) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS joystick_mappings
                     (joystick_id INTEGER, action TEXT, button INTEGER, 
                     PRIMARY KEY (joystick_id, action))''')

def save_config_to_db():
    with sqlite3.connect(get_db_path()) as conn:
        conn.executemany("INSERT OR REPLACE INTO joystick_mappings VALUES (?, ?, ?)",
                         [(joystick_id, action, button) 
                          for joystick_id, mappings in joystick_config.items() 
                          for action, button in mappings.items()])

def load_config_from_db():
    config = {}
    with sqlite3.connect(get_db_path()) as conn:
        for joystick_id, action, button in conn.execute("SELECT * FROM joystick_mappings"):
            config.setdefault(joystick_id, {})[action] = button
    return config

def initialize_joysticks():
    pygame.joystick.init()
    return [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

def draw_grid(surface, width, height, cell_size=20):
    for x in range(0, width, cell_size):
        pygame.draw.line(surface, GRAY, (x, 0), (x, height))
        if x % 100 == 0:
            display_text(surface, str(x), (x, 0), font_size=15, color=BLACK)
    for y in range(0, height, cell_size):
        pygame.draw.line(surface, GRAY, (0, y), (width, y))
        if y % 100 == 0:
            display_text(surface, str(y), (0, y), font_size=15, color=BLACK)

def display_text(surface, text, position, font_size=20, color=BLACK):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)


TOGGLE_BUTTON_WIDTH = 60
TOGGLE_BUTTON_HEIGHT = 30

def draw_toggle_button(screen, x, y, width, height, text, is_on):
    color = GREEN if is_on else RED
    pygame.draw.rect(screen, color, (x, y, width, height))
    font = pygame.font.Font(None, 24)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surf, text_rect)

def draw_custom_picture():
    image_path = os.path.join(os.path.dirname(__file__), "img", "cool controller.png")
    try:
        controller_img = pygame.image.load(image_path)
        controller_img = pygame.transform.scale(controller_img, (550, 350))
        screen.blit(controller_img, (300, 100))
        for joystick_id in range(len(joysticks)):
            draw_joystick_buttons(screen, joystick_id)
    except pygame.error as e:
        print(f"Error loading image: {e}")
        pygame.draw.rect(screen, LIGHT_BLUE, (300, 100, 550, 350))
        display_text(screen, "Custom Controller Image", (400, 250), font_size=40)

def draw_custom_picture_top():
    image_path = os.path.join(os.path.dirname(__file__), "img", "controller top.png")
    try:
        controller_img = pygame.image.load(image_path)
        controller_img = pygame.transform.scale(controller_img, (450, 350))
        screen.blit(controller_img, (360, 350))
        for joystick_id in range(len(joysticks)):
            draw_joystick_buttons(screen, joystick_id)
    except pygame.error as e:
        print(f"Error loading image: {e}")
        pygame.draw.rect(screen, LIGHT_BLUE, (300, 100, 550, 350))
        display_text(screen, "Custom Controller Image", (400, 250), font_size=40)



def draw_joystick_buttons(surface, joystick_id):
    inputs = controller.get_input()
    button_positions = {
        'action1': (500 + 215, 230 - 48), 'action2': (550 + 200, 215), 'action3': (500 + 215, 248), 'action4': (450 + 228, 215),
        'action5': (480, 510), 'action6': (700, 510),
        'action7': (460, 540), 'action8': (720, 540),
        'action9': (540, 218), 'action10': (610, 218),
        'axUp': (200 + 300, 220 + 30), 'axDown': (200 + 300, 280 + 30), 'axleft': (170 + 300, 250 + 30), 'axright': (230 + 300, 250 + 30),
        'hatUp': (435, 190), 'hatDown': (435, 240), 'hatleft': (400, 215), 'hatright': (470, 215)
    }
    for action, position in button_positions.items():
        if inputs.get(action, False):
            pygame.draw.circle(surface, GREEN, position, 10)

def draw_config_panel(joystick_id, x, y, width, height):
    pygame.draw.rect(screen, LIGHT_BLUE, (x, y, width, height))
    display_text(screen, f"Joystick {joystick_id} Configuration Panel", (x + 10, y + 10), color=BLACK)
    
    if joystick_id < len(joysticks):
        joystick_y = y + 50
        #display_text(screen, f"Joystick {joystick_id}: {joysticks[joystick_id].get_name()}", (x + 10, joystick_y), color=BLACK)
        
        # Draw toggle button
        toggle_x = x + width - TOGGLE_BUTTON_WIDTH - 10
        toggle_y = joystick_y
        draw_toggle_button(screen, toggle_x, toggle_y, TOGGLE_BUTTON_WIDTH, TOGGLE_BUTTON_HEIGHT, 
                           "ON" if controller.enabled_joysticks[joystick_id] else "OFF", 
                           controller.enabled_joysticks[joystick_id])
        
        for j, action in enumerate(game_actions):
            action_y = joystick_y + 40 + j * 30
            button = joystick_config.get(joystick_id, {}).get(action, "Not Set")
            text = f"{action}: Button {button}" if button != "Not Set" else f"{action}: {button}"
            display_text(screen, text, (x + 20, action_y), color=BLACK)

def draw_done_button():
    pygame.draw.rect(screen, GREEN, done_button)
    text = font.render("DONE", True, BLACK)
    screen.blit(text, (done_button.centerx - text.get_width() // 2, done_button.centery - text.get_height() // 2))

def main():
    global joystick_config, joysticks
    
    setup_database()
    joysticks = initialize_joysticks()
    if not joysticks:
        print("No joysticks detected. Exiting.")
        return

    joystick_config = load_config_from_db()

    configuring = False
    current_joystick = None
    current_action = None

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_config_to_db()
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if done_button.collidepoint(event.pos):
                    save_config_to_db()
                    pygame.quit()
                    sys.exit()
                elif 260 <= event.pos[0] <= 940:
                    pass
                else:
                    x, y = event.pos
                    joystick_index = 1 if x < 260 else 0
                    if joystick_index < len(joysticks):
                        # Check if toggle button was clicked
                        toggle_x = (0 if joystick_index == 1 else 940) + 260 - TOGGLE_BUTTON_WIDTH - 10
                        toggle_y = 50
                        if toggle_x <= x <= toggle_x + TOGGLE_BUTTON_WIDTH and toggle_y <= y <= toggle_y + TOGGLE_BUTTON_HEIGHT:
                            controller.toggle_joystick(joystick_index)
                        else:
                            panel_y = y - 50  # Adjusted y position calculation
                            action_index = (panel_y - 40) // 30
                            if 0 <= action_index < len(game_actions):
                                current_joystick = joystick_index
                                current_action = game_actions[action_index]
                                configuring = True
                                print(f"Click a button to configure {current_action} for Joystick {current_joystick}")

        controller.update()

        if configuring:
            for action, is_pressed in controller.inputs.items():
                if is_pressed:
                    joystick_config.setdefault(current_joystick, {})[current_action] = action
                    print(f"Joystick {current_joystick}: Mapped {current_action} to {action}")
                    configuring = False
                    break

        screen.fill(WHITE)
        draw_grid(screen, 1200, 600, 20)
        
        draw_custom_picture()
        draw_custom_picture_top()
        draw_config_panel(0, 940, 0, 260, 600)
        draw_config_panel(1, 0, 0, 260, 600)
        draw_done_button()

        if configuring:
            display_text(screen, f"Press a button for {current_action} on Joystick {current_joystick}", (300, HEIGHT - 50), color=RED)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
