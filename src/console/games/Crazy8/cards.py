import pygame
import random


class Cards():
    def __init__(self,x,y,card):
        self.x = x
        self.y = y
        self.card = card
        self.shuffle = False
        self.cards = 0

    
    def load_image(self,card):
        back_card = card.subsurface(200,110,10,10)
        return back_card

    def draw_cards(self, surface):
        #img = self.card
        surface.blit(self.card, (self.x,self.y))
        

