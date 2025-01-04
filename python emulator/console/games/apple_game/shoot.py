#shoot.py
import random
from random import randint
import pygame 



pygame.init()

WIDTH = 800
HEIGHT= 600
GRID_SIZE = 50


background_image = pygame.image.load('images/basic.png')
# Scale the background image to fill the screen
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

#sprites
apple = Actor("apple1")  #the actor in this case is the image
tree = Actor("tree")



#resizing
tree.scale = 0.5
apple.scale = 0.2
#background.pos = (WIDTH // 2, HEIGHT //2)



#

#players = [Actor("player1"), Actor("player2")]

#player_select = int(input("choose your player 1 or 2: "))

player =  Actor("player2")    #players[player_select - 1]

player.scale = 0.5


#draw a grid for propper plotting
def grid():
	for x in range(0, 800, 50):    #vertical lines
	
		screen.draw.line((x,0), (x, 600), color=(200, 200, 200))
		if x < WIDTH:  # Don't draw number at the right edge
            		screen.draw.text(str(x), (x + 5, 5), fontsize=20, color=(150, 150, 150))
		
	for y in range(0, 600, 50):    #horizontal lines
		screen.draw.line((0,y), (800, y), color=(200, 200, 200))
		if y < HEIGHT:  # Don't draw number at the bottom edge
            		screen.draw.text(str(y), (5, y + 5), fontsize=20, color=(150, 150, 150))


def draw():
	screen.blit(background_image, (0, 0)) #screen.clear() #this clears the screen
	#background.draw()
	grid()
	#tree.draw()
	#apple.draw()	#this draws the apple on the screen
	#player.draw()
	
	
	

#place the apple

def place_apple():
	tree.x = 550
	tree.y = 220
	apple.x = randint(400, 700)
	apple.y = randint(50, 200)


place_apple()


def place_actor():
	player.x = 100
	player.y = 450

place_actor()



#dealing with clicks

def on_mouse_down(pos):
	if apple.collidepoint(pos):  #this function checks if the curser is on the same position as the apple
		print("good shot!!")
		place_apple()

	else:
		print("you missed!!")
		#quit()   #this command quits the game by stopping the program completely


def update(): ####	move the player 
	if keyboard.left:
		player.x = player.x - 5
	elif keyboard.right:
		player.x = player.x + 5