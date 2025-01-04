import pygame
import os
from fighter import Fighter
from pygame import mixer

pygame.init()
mixer.init()

WIDTH, HEIGHT = 1000, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("BATTLE ARENA")

# base directory setup
base_dir = os.path.dirname(os.path.abspath(__file__))

# Load images and assets (keeping your existing setup)
bg_image = pygame.image.load(f"{base_dir}\Assets\images\dojo.png").convert_alpha()
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

warrior_sheet = pygame.image.load(f"{base_dir}\Assets\sprite sheet\warior.png").convert_alpha()
wizard_sheet = pygame.image.load(f"{base_dir}\Assets\sprite sheet\evil_wizard.png").convert_alpha()
victory_img = pygame.image.load(f"{base_dir}\Assets\images\\victory_image.png").convert_alpha()

# Define colors
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (128,128,128)

# Existing game setup...
WARRIOR_ANIMATION_STEPS = [7,7,8,7,10,6,8,3]
WIZARD_ANIMATION_STEPS = [8,8,2,7,8,4,8,3]

# Sound setup (keeping your existing setup)
pygame.mixer.music.load(f"{base_dir}\Assets\sound fx\game_music.mp3")
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(-1,0.0,5000)

sword_fx = pygame.mixer.Sound(f"{base_dir}\Assets\sound fx\sword-attack.wav")
sword_fx.set_volume(0.5)
magic_fx = pygame.mixer.Sound(f"{base_dir}\Assets\sound fx\\fire-magic.wav")
magic_fx.set_volume(0.75)

# Fonts
count_font = pygame.font.Font(f"{base_dir}\Assets\\fonts\Write Nice.otf", 80)
score_font = pygame.font.Font(f"{base_dir}\Assets\\fonts\Write Nice.otf", 30)
pause_font = pygame.font.Font(f"{base_dir}\Assets\\fonts\Write Nice.otf", 50)

# Existing functions (draw_text, bg_draw, health_bars)
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x,y))

def bg_draw():
    screen.blit(bg_image, (0,0))

def health_bars(health, x, y): 
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, (255,0,0), (x, y, 400, 30))
    pygame.draw.rect(screen, (255,255,0), (x, y, 400 * ratio, 30))

# Pause menu class
class PauseMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Pause menu options
        self.options = [
            "Resume",
            "Quit to Main Menu"
        ]
        self.selected_option = 0
    
    def draw(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Pause title
        draw_text("PAUSED", pause_font, WHITE, self.screen_width // 2 - 100, self.screen_height // 4)
        
        # Draw menu options
        for i, option in enumerate(self.options):
            color = WHITE if i == self.selected_option else GRAY
            draw_text(option, pause_font, color, self.screen_width // 2 - 100, self.screen_height // 2 + i * 70)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = max(0, self.selected_option - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_option = min(len(self.options) - 1, self.selected_option + 1)
            elif event.key == pygame.K_RETURN:
                return self.selected_option
        return None

def main():
    # Game setup
    # Reuse the existing Pygame display instead of creating a new one
    global screen, WIDTH, HEIGHT

    clock = pygame.time.Clock()
    FPS = 60

    # Game variables
    intro_count = 3
    last_count_update = pygame.time.get_ticks()
    score = [0, 0]
    round_over = False
    ROUND_OVER_COOLDOWN = 4000

    # Fighter setup
    WARRIOR_SIZE = 162
    WIZARD_SIZE = 250
    WARRIOR_SCALE = 4
    WIZARD_SCALE = 3
    WARRIOR_OFFSET = [72, 56]
    WIZARD_OFFSET = [112, 107]
    WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
    WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]

    # Create fighters
    fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
    fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)

    # Pause menu
    pause_menu = PauseMenu(WIDTH, HEIGHT)
    paused = False

    # Game loop
    run = True
    while run:
        clock.tick(FPS)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            # Pause toggle
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                    if paused:
                        # Pause the music when game is paused
                        pygame.mixer.music.pause()
                    else:
                        # Resume the music when game is unpaused
                        pygame.mixer.music.unpause()
            
            # Pause menu input
            if paused:
                menu_action = pause_menu.handle_input(event)
                if menu_action is not None:
                    if menu_action == 0:  # Resume
                        paused = False
                        pygame.mixer.music.unpause()
                    elif menu_action == 1:  # Quit to Main Menu
                        pygame.mixer.music.stop()  # Stop music when quitting
                        return

        # Skip game logic if paused
        if paused:
            # Draw background
            bg_draw()
            
            # Draw fighters
            fighter_1.draw(screen)
            fighter_2.draw(screen)
            
            # Draw pause menu
            pause_menu.draw(screen)
            
            pygame.display.update()
            continue

        # Draw background
        bg_draw()

        # Player stats
        health_bars(fighter_1.health, 20, 20)
        health_bars(fighter_2.health, 580, 20)
        draw_text("P1: " + str(score[0]), score_font, (255,0,0), 20, 60)
        draw_text("P2: " + str(score[1]), score_font, (255,0,0), 880, 60)

        # Countdown
        if intro_count <= 0:
            # Move fighters 
            fighter_1.move(WIDTH, HEIGHT, screen, fighter_2, round_over)
            fighter_2.move(WIDTH, HEIGHT, screen, fighter_1, round_over)
        else:
            # Display count timer
            draw_text(str(intro_count), count_font, (255,0,0), WIDTH / 2, HEIGHT / 3)
            if (pygame.time.get_ticks() - last_count_update) >= 1000:
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()

        fighter_1.update()
        fighter_2.update()

        # Draw fighters
        fighter_1.draw(screen)
        fighter_2.draw(screen)

        # Check for player defeat
        if not round_over:
            if not fighter_1.alive:
                score[1] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
            elif not fighter_2.alive:
                score[0] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
        else:
            screen.blit(victory_img, (WIDTH / 5, HEIGHT /150))
            if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                round_over = False
                intro_count = 3
                fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
                fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)

        # Update display
        pygame.display.update()

    # Exit
    pygame.quit()

# Allow the script to be run directly or imported
if __name__ == '__main__':
    main()