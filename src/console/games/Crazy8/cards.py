import pygame
import random
import os

class Card:
    def __init__(self, image, name, suit):
        self.image = image
        self.name = name
        self.suit = suit

    def is_special(self):
        return self.name in ['7', '8', '2', 'J', 'A'] or self.name.lower() == 'joker'

class Cards:
    def __init__(self, x, y, back_card):
        self.x = x
        self.y = y
        self.back_card = back_card
        self.top_card = None
        self.deck = []
        self.special_cards = []
        self.normal_cards = []

    def load_cards(self, base_dir):
        suits = ['hearts', 'diamonds', 'clovers', 'spades']
        for suit in suits:
            suit_dir = os.path.join(base_dir, "cards", suit)
            for filename in os.listdir(suit_dir):
                if filename.endswith(".png"):
                    name = filename.split('.')[0]  # Remove the .png extension
                    image_path = os.path.join(suit_dir, filename)
                    image = pygame.image.load(image_path).convert_alpha()
                    image = pygame.transform.scale(image, (int(pygame.display.get_surface().get_width() / 10), int(pygame.display.get_surface().get_height() / 5)))
                    card = Card(image, name, suit)
                    self.deck.append(card)
                    if card.is_special():
                        self.special_cards.append(card)
                    else:
                        self.normal_cards.append(card)

    def shuffle_and_select(self):
        random.shuffle(self.deck)
        self.top_card = self.deck.pop(0)

    def draw_cards(self, surface):
        if self.back_card:
            surface.blit(self.back_card, (self.x, self.y))
        
        if self.top_card:
            surface.blit(self.top_card.image, (475, 300))
        
        # Draw player's cards (example)
        for i, card in enumerate(self.deck[:8]):  # Draw first 8 cards as player's hand
            x = 690 + (i % 3) * 100
            y = 0 + (i // 3) * 100
            surface.blit(card.image, (x, y))

 


class Player():
    def __init__(self,player_data):
        self.players = player_data
        self.current_player = 0
        self.is_turn = [False] * len(player_data)
        self.is_turn[0] = True
        
    def next_turn(self):
        self.is_turn[self.current_player] = False
        self.current_player = (self.current_player + 1) % len(self.players)
        self.is_turn[self.current_player] = True
        

    def skip_turn(self):
        self.next_turn()

    def draw_skip_input(self, surface):
        font = pygame.font.Font(None, 24)
        text = font.render(f"Player {self.players[self.current_player]}, would you like to skip this turn? (Y/N)", True, (0,0,0))
        surface.blit(text, (50,500))
        


    def game_logic(players, cards, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    players.skip_turn()
                elif event.key == pygame.K_n:
                    # Handle playing a card
                    pass
                # Add more key handlers for special card actions

    def draw_game(surface, players, cards):
        cards.draw_cards(surface)
        if players.is_turn[players.current_player]:
            players.draw_skip_input(surface)

    def handle_special_card(card, players, cards):
        if card.name == '7':
            players.reverse_order()
        elif card.name == '8':
            # Allow current player to draw again
            pass
        elif card.name == '2':
            # Make next player draw two cards
            pass
        elif card.name.lower() == 'joker':
            # Make next player draw five cards
            pass
        elif card.name == 'J':
            players.skip_next_player()
        elif card.name == 'A':
            # Block effects and allow demanding a suit
            pass

    # Add this function to the Player class
    def reverse_order(self):
        self.players.reverse()
        self.current_player = (len(self.players) - 1) - self.current_player

    # Add this function to the Player class
    def skip_next_player(self):
        self.next_turn()
        

        

