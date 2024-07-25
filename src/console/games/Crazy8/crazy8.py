import pygame
import os
from cards import Cards, Player

pygame.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

base_dir = os.path.dirname(os.path.abspath(__file__))
background = pygame.image.load(os.path.join(base_dir, "cards", "board.jpg")).convert_alpha()
background = pygame.transform.scale(background, (WIDTH / 1.5, HEIGHT))

back_card = pygame.image.load(os.path.join(base_dir, "cards", "back.png")).convert_alpha()
back_card = pygame.transform.scale(back_card, (int(WIDTH / 10), int(HEIGHT / 5)))

# Colors
GREEN = (0, 128, 0)

# Initialize Cards
cards = Cards(275, HEIGHT / 2.5, back_card)
cards.load_cards(base_dir)
cards.shuffle_and_select()

# Initialize Players
player_list = [1, 2, 3, 4]
players = Player(player_list)

def draw_bg():
    screen.blit(background, (0, 0))

run = True
while run:
    screen.fill(GREEN)
    draw_bg()

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            run = False

    Player.game_logic(players, cards, events)
    Player.draw_game(screen, players, cards)

    # Example of handling a special card (you would do this when a card is played)
    if cards.top_card and cards.top_card.is_special():
        Player.handle_special_card(cards.top_card, players, cards)

    pygame.display.update()

pygame.quit()
