import pygame
import os
from fighter import Fighter
from pygame import mixer



pygame.init()
mixer.init()

WIDTH, HEIGHT = 1000, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("BATTLE ARENA")




#
base_dir = os.path.dirname(os.path.abspath(__file__))

bg_image = pygame.image.load(f"{base_dir}\Assets\images\dojo.png").convert_alpha()

bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

#load spritesheets
warrior_sheet = pygame.image.load(f"{base_dir}\Assets\sprite sheet\warior.png").convert_alpha()
wizard_sheet = pygame.image.load(f"{base_dir}\Assets\sprite sheet\evil_wizard.png").convert_alpha()
victory_img = pygame.image.load(f"{base_dir}\Assets\images\\victory_image.png").convert_alpha()


#define number of steps in each animation
WARRIOR_ANIMATION_STEPS = [7,7,8,7,10,6,8,3]
WIZARD_ANIMATION_STEPS = [8,8,2,7,8,4,8,3]
MIDEVIL_WARRIOR_STEPS = []

#sound fx
pygame.mixer.music.load(f"{base_dir}\Assets\sound fx\game_music.mp3")
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(-1,0.0,5000)

sword_fx = pygame.mixer.Sound(f"{base_dir}\Assets\sound fx\sword-attack.wav")
sword_fx.set_volume(0.5)
magic_fx = pygame.mixer.Sound(f"{base_dir}\Assets\sound fx\\fire-magic.wav")
magic_fx.set_volume(0.75)


#SET FRAMERATE
clock = pygame.time.Clock()
FPS = 60

#define colors
YELLOW = (255,255,0) 
RED = (255,0,0)
WHITE = (255,255,255)


#define game variables
intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0,0] #player scores [P1,P2]
round_over = False
ROUND_OVER_COOLDOWN = 4000 




#game loop
#define fighter variables
WARRIOR_SIZE = 162
WIZARD_SIZE = 250
WARRIOR_SCALE = 4
WIZARD_SCALE = 3
WARRIOR_OFFSET = [72, 56]
WIZARD_OFFSET = [112, 107]
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]

count_font = pygame.font.Font(f"{base_dir}\Assets\\fonts\Write Nice.otf", 80)

score_font = pygame.font.Font(f"{base_dir}\Assets\\fonts\Write Nice.otf", 30)

#function for drawing text
def draw_text(text, font, text_color, x,y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x,y))


def bg_draw():
    screen.blit(bg_image, (0,0))


def health_bars(health, x, y): 
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))
    

#create 2 instances of fighters
fighter_1 = Fighter(1,200, 310,False ,WARRIOR_DATA ,warrior_sheet,WARRIOR_ANIMATION_STEPS, sword_fx)
fighter_2 = Fighter(2,700, 310,True ,WIZARD_DATA ,wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)





run = True
while run:
    clock.tick(FPS)

    #draw background
    bg_draw()

    #SHOW PLAYER STATS
    health_bars(fighter_1.health, 20, 20)
    health_bars(fighter_2.health, 580, 20)
    draw_text("P1: " + str(score[0]), score_font, RED, 20, 60)
    draw_text("P2: " + str(score[1]), score_font, RED, 880, 60)
#countdown
    if intro_count <= 0:
        #move fighters 
        fighter_1.move(WIDTH, HEIGHT, screen, fighter_2, round_over)
        fighter_2.move(WIDTH, HEIGHT, screen, fighter_1, round_over)
    else:
        #display count timer
        draw_text(str(intro_count), count_font, RED, WIDTH / 2, HEIGHT / 3)
        if (pygame.time.get_ticks() - last_count_update) >= 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()
            print(intro_count)

    fighter_1.update()
    fighter_2.update()

    #draw fighters
    fighter_1.draw(screen)
    fighter_2.draw(screen)

    #CHECK FOR PLAYER DEFEAT
    if round_over == False:
        if fighter_1.alive == False:
            score[1] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
            print(score)
        elif fighter_2.alive == False:
            score[0] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
            print(score)
    else:
        screen.blit(victory_img, (WIDTH / 5, HEIGHT /150))
        if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
            round_over = False
            intro_count = 3
            fighter_1 = Fighter(1,200, 310,False ,WARRIOR_DATA ,warrior_sheet,WARRIOR_ANIMATION_STEPS, sword_fx)
            fighter_2 = Fighter(2,700, 310,True ,WIZARD_DATA ,wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)

            
    #event handler 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    #update display
    pygame.display.update()

#exit
pygame.quit()