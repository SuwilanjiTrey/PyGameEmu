import pygame
import os

from cards import Cards


pygame.init()

WIDTH, HEIGHT = 1000, 600
CENTER_X = WIDTH / 2
CENTER_Y = HEIGHT / 2

screen = pygame.display.set_mode((WIDTH, HEIGHT))

#try to draw the background
base_dir = os.path.dirname(os.path.abspath(__file__))
background = pygame.image.load(f"{base_dir}\cards\\board.jpg").convert_alpha()
background = pygame.transform.scale(background, (WIDTH / 1.5, HEIGHT))

back_card = pygame.image.load(f"{base_dir}\cards\\back.png").convert_alpha()
back_card = pygame.transform.scale(back_card, (int(WIDTH /10), int(HEIGHT/5)))

Ace_card_heart = pygame.image.load(f"{base_dir}\cards\hearts\hearts (A).png").convert_alpha()
Ace_card_heart = pygame.transform.scale(Ace_card_heart, (int(WIDTH /10), int(HEIGHT/5)))

Ace_card_clover = pygame.image.load(f"{base_dir}\cards\clovers\clover (A).png").convert_alpha()
Ace_card_clover = pygame.transform.scale(Ace_card_clover, (int(WIDTH /10), int(HEIGHT/5)))

Ace_card_diamond = pygame.image.load(f"{base_dir}\cards\diamonds\diamond (A).png").convert_alpha()
Ace_card_diamond = pygame.transform.scale(Ace_card_diamond, (int(WIDTH /10), int(HEIGHT/5)))

Ace_card_spade = pygame.image.load(f"{base_dir}\cards\spades\spade (A).png").convert_alpha()
Ace_card_spade = pygame.transform.scale(Ace_card_spade, (int(WIDTH /10), int(HEIGHT/5)))

#define the colors
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

card_back = Cards(275,HEIGHT / 2.5,back_card)
spade = Cards(0,HEIGHT / 2.5,Ace_card_spade)
diamond = Cards(WIDTH / 1.5,HEIGHT / 2.5,Ace_card_diamond)
heart = Cards(0,HEIGHT / 10,Ace_card_heart)
clover = Cards(WIDTH / 5,HEIGHT / 1.5,Ace_card_clover)

def draw_bg():
    screen.blit(background, (0,0))
    

run = True
while run:
    draw_bg()

    card_back.draw_cards(screen)
    spade.draw_cards(screen)
    diamond.draw_cards(screen)
    heart.draw_cards(screen)
    clover.draw_cards(screen)
    #event handler 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    #update display
    pygame.display.update()

pygame.quit()