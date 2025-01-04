import pygame
import cv2
import sys
import os
import json
from tkinter import filedialog
import tkinter as tk
from pathlib import Path


class Button:
    def __init__(self, x, y, image_path, hover_image_path=None, scale=(0, 0), callback=None):
        # Load and resize images
        original_image = pygame.image.load(image_path)
        original_hover = pygame.image.load(hover_image_path) if hover_image_path else original_image
        
        self.image = pygame.transform.scale(original_image, scale)
        self.hover_image = pygame.transform.scale(original_hover, scale)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.current_image = self.image
        self.callback = callback
    
    def draw(self, surface):
        surface.blit(self.current_image, self.rect)
    
    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_image(self, is_hover):
        self.current_image = self.hover_image if is_hover else self.image
    
    def handle_click(self, pos):
        if self.is_hovered(pos) and self.callback:
            self.callback()

class GameCache:
    def __init__(self):
        self.cache_file = "game_cache.json"
        self.games = self.load_cache()
    
    def load_cache(self):
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.games, f, indent=4)
    
    def add_game(self, name, path):
        # Check if game already exists
        for game in self.games:
            if game['path'] == path:
                return
        
        self.games.append({
            'name': name,
            'path': path
        })
        self.save_cache()
    
    def remove_game(self, path):
        self.games = [game for game in self.games if game['path'] != path]
        self.save_cache()




class NavigationDrawer:
    def __init__(self, screen_width, screen_height, game_cache):
        self.width = 300
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = -self.width
        self.open = False
        self.game_cache = game_cache
        
        # Drawer background
        self.surface = pygame.Surface((self.width, screen_height), pygame.SRCALPHA)
        self.surface.fill((50, 50, 50, 200))
        
        # Back button
        self.back_button = pygame.Rect(10, 10, 280, 30)
        
        # Add More button
        self.add_more_button = pygame.Rect(10, 50, 280, 30)
        
        # Grid settings
        self.grid_start_y = 90
        self.grid_cols = 3
        self.game_width = 85  # Width of each game tile
        self.game_height = 85  # Height of each game tile
        self.spacing = 10  # Space between tiles
        
        # Game thumbnails cache
        self.thumbnails = {}
        
        # Create buttons from cache
        self.update_buttons()
        self.load_thumbnails()
    
    def load_thumbnails(self):
        for game in self.game_cache.games:
            game_dir = os.path.dirname(game['path'])
            # Try to load thumbnail from common image formats
            for ext in ['.png', '.jpg', '.jpeg']:
                thumbnail_path = os.path.join(game_dir, 'thumbnail' + ext)
                if os.path.exists(thumbnail_path):
                    try:
                        image = pygame.image.load(thumbnail_path)
                        self.thumbnails[game['path']] = pygame.transform.scale(image, (self.game_width - 10, self.game_width - 10))
                        break
                    except:
                        continue
            
            # If no thumbnail found, create a default colored rectangle
            if game['path'] not in self.thumbnails:
                surf = pygame.Surface((self.game_width - 10, self.game_width - 10))
                surf.fill((100, 100, 150))
                self.thumbnails[game['path']] = surf
    
    def update_buttons(self):
        self.buttons = []
        games_per_row = self.grid_cols
        
        for i, game in enumerate(self.game_cache.games):
            row = i // games_per_row
            col = i % games_per_row
            
            x = self.spacing + col * (self.game_width + self.spacing)
            y = self.grid_start_y + row * (self.game_height + self.spacing)
            
            btn = pygame.Rect(x, y, self.game_width, self.game_height)
            self.buttons.append({
                'rect': btn,
                'name': game['name'],
                'path': game['path']
            })


    def draw(self, screen):
        # Draw drawer
        self.surface.fill((50, 50, 50, 200))
        
        # Draw back button
        pygame.draw.rect(self.surface, (100, 100, 100, 200), self.back_button)
        small_font = pygame.font.Font(None, 24)
        text = small_font.render("← Back", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.back_button.center)
        self.surface.blit(text, text_rect)
        
        # Draw Add More button
        pygame.draw.rect(self.surface, (100, 150, 100, 200), self.add_more_button)
        text = small_font.render("+ Add More Games", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.add_more_button.center)
        self.surface.blit(text, text_rect)
        
        # Draw game buttons in grid
        for btn in self.buttons:
            # Draw button background
            pygame.draw.rect(self.surface, (70, 70, 70, 200), btn['rect'])
            
            # Draw thumbnail
            thumbnail = self.thumbnails.get(btn['path'])
            if thumbnail:
                thumb_rect = thumbnail.get_rect(center=(
                    btn['rect'].centerx,
                    btn['rect'].centery - 10
                ))
                self.surface.blit(thumbnail, thumb_rect)
            
            # Draw game name
            text = small_font.render(btn['name'][:10] + ('...' if len(btn['name']) > 10 else ''), 
                                   True, (255, 255, 255))
            text_rect = text.get_rect(centerx=btn['rect'].centerx,
                                    bottom=btn['rect'].bottom - 5)
            self.surface.blit(text, text_rect)
        
        screen.blit(self.surface, (self.x, 0))

        
    
    def update(self):
        if self.open and self.x < 0:
            self.x += 20
        elif not self.open and self.x > -self.width:
            self.x -= 20
        
        self.x = max(-self.width, min(0, self.x))
    
    def toggle(self):
        self.open = not self.open
    
    def handle_click(self, pos):
        local_pos = (pos[0] - self.x, pos[1])
        
        # Check if back button was clicked
        if self.back_button.collidepoint(local_pos):
            self.toggle()
            return None
            
        # Check if Add More button was clicked
        if self.add_more_button.collidepoint(local_pos):
            return "add_more"
            
        # Check if game buttons were clicked
        for btn in self.buttons:
            if btn['rect'].collidepoint(local_pos):
                return btn
        return None

class PygameVideoEmulator:
    def __init__(self, video_path):
        pygame.init()
        pygame.display.set_caption('Pygame Video Emulator')
        
        # Initialize game cache
        self.game_cache = GameCache()
        
        # Screen setup
        self.screen_width = 1020
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Video setup
        self.video_path = video_path
        self.video_capture = cv2.VideoCapture(video_path)
        
        self.clock = pygame.time.Clock()
        self.playing_video = True
        self.paused = False
        
        # Navigation drawer
        self.drawer = NavigationDrawer(self.screen_width, self.screen_height, self.game_cache)
        
        # Overlay
        self.overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.overlay_alpha = 0
        
        # Initialize Tkinter for file dialog
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()  # Hide the Tkinter window
        
        # Setup buttons
        self.setup_buttons()
    
    def setup_buttons(self):
        button_configs = [
            {
                'x': 0,
                'y': 10,
                'image': r'config\img\open_file.png',

                'hover': r'config\img\open_file2.png'
                #'callback': self.add_new_game
            },
            {
                'x': 70,
                'y': 10,
                'image': r'config\img\settings.png',
                'hover': r'config\img\settings2.png'
            },
            {
                'x': 140,
                'y': 10,
                'image': r'config\img\about.png',
                'hover': r'config\img\about2.png'
            }
        ]
        
        self.buttons = [
            Button(
                config['x'],
                config['y'],
                config.get('image', r'config\img\default.png'),
                config.get('hover', r'config\img\default2.png'),
                scale=(50, 40),
                callback=config.get('callback')
            ) for config in button_configs
        ]
    
    def add_new_game(self):
        # Open file dialog to select game file
        file_path = filedialog.askopenfilename(
            title="Select Game File",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            # Get game name from file name
            game_name = Path(file_path).stem
            
            # Add to cache
            self.game_cache.add_game(game_name, file_path)
            
            # Update drawer buttons
            self.drawer.update_buttons()
    
    
    
    def run(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        # Handle button clicks
                        for button in self.buttons:
                            button.handle_click(mouse_pos)
                        
                        # Check drawer buttons
                        clicked_item = self.drawer.handle_click(event.pos)
                        if clicked_item == "add_more":
                            self.add_new_game()
                        elif clicked_item:  # It's a game button
                            self.load_game(clicked_item['path'])
                        
                        # Toggle drawer if clicked on edge
                        if mouse_pos[0] < 50 or self.drawer.x > 0:
                            self.drawer.toggle()
                
                # Button hover effects
                for button in self.buttons:
                    button.update_image(button.is_hovered(mouse_pos))
            
            # Update drawer
            self.drawer.update()
            
            if not self.paused:
                # Read video frame
                ret, frame = self.video_capture.read()
                
                if not ret:
                    # Restart video if it ends
                    self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                # Convert OpenCV frame to Pygame surface
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                
                # Scale frame to screen size
                frame = pygame.transform.scale(frame, (self.screen_width, self.screen_height))
                
                # Draw frame
                self.screen.blit(frame, (0, 0))
                
                # Draw buttons
                for button in self.buttons:
                    button.draw(self.screen)
                
                # Draw navigation drawer
                self.drawer.draw(self.screen)
                
                # Fade overlay
                if self.drawer.open:
                    self.overlay_alpha = min(150, self.overlay_alpha + 10)
                else:
                    self.overlay_alpha = max(0, self.overlay_alpha - 10)
                
                self.overlay.fill((0, 0, 0, self.overlay_alpha))
                self.screen.blit(self.overlay, (0, 0))
                
                pygame.display.flip()
            
            # Control frame rate
            self.clock.tick(30)
    
    def load_game(self, game_path):
        print(f"Loading game: {game_path}")
        try:
            if not os.path.exists(game_path):
                print(f"Game file not found: {game_path}")
                self.game_cache.remove_game(game_path)
                self.drawer.update_buttons()
                return
            else:
                # Play loading video
                loading_video = r"config/img/loading.mp4"
                if os.path.exists(loading_video):
                    self.play_loading_video(loading_video)
            
            # Get the directory of the main game file
            self.current_game_dir = os.path.dirname(os.path.abspath(game_path))
            
            # Add the game's directory to Python's module search path
            sys.path.insert(0, self.current_game_dir)
            
            # Change working directory to game directory
            original_cwd = os.getcwd()
            os.chdir(self.current_game_dir)
            
            # Read the game file contents
            with open(game_path, 'r') as file:
                game_code = file.read()
            
            # Initialize the PygameZero wrapper
            from pgzero_compat import PygameZeroWrapper
            self.pgzero_wrapper = PygameZeroWrapper(self.screen, game_path)
            
            try:
                if self.pgzero_wrapper.is_pgzero_game(game_code):
                    print("Loading as Pygame Zero game...")
                    self._run_pgzero_game(game_code, game_path)
                else:
                    print("Loading as regular Pygame game...")
                    self._run_pygame_game(game_code, game_path)
            finally:
                # Restore original working directory
                os.chdir(original_cwd)
                # Remove the game directory from sys.path
                sys.path.pop(0)
                
        except Exception as e:
            print(f"Error loading game: {e}")
            import traceback
            traceback.print_exc()
    
    def _run_pgzero_game(self, game_code, game_path):
        # Create namespace with Pygame Zero compatibility
        namespace = self.pgzero_wrapper.create_namespace()
        namespace.update({
            '__name__': '__main__',
            '__file__': game_path,
            '__package__': None,
            'WIDTH': self.screen_width,
            'HEIGHT': self.screen_height,
        })
        
        # Execute the game code in the Pygame Zero compatible environment
        exec(game_code, namespace)
        
        # Start the game loop
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if 'on_mouse_down' in namespace:
                        namespace['on_mouse_down'](pos)
            
            # Update game state
            self.pgzero_wrapper.update()
            if 'update' in namespace:
                namespace['update']()
            
            # Draw frame
            if 'draw' in namespace:
                namespace['draw']()

            if 'clock' in namespace:
                namespace['clock'].update()
            
            pygame.display.flip()
            clock.tick(60)
    
    def _run_pygame_game(self, game_code, game_path):
        # Create global variables to share with the game
        global_namespace = {
            '__name__': '__main__',
            '__file__': game_path,
            '__package__': None,
            'screen': self.screen,
            'WIDTH': self.screen_width,
            'HEIGHT': self.screen_height
        }
        
        # Execute the game script
        exec(game_code, global_namespace)
    
    def play_loading_video(self, video_path):
        # Temporary video playback for loading
        video_capture = cv2.VideoCapture(video_path)
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break
            
            # Convert frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            frame = pygame.transform.scale(frame, (self.screen_width, self.screen_height))
            
            # Draw frame
            self.screen.blit(frame, (0, 0))
            pygame.display.flip()
            self.clock.tick(30)
        
        video_capture.release()
    
    def cleanup(self):
        self.video_capture.release()
        pygame.quit()
        sys.exit()

def main():
    video_path = r"config/img/play-game.mp4"
    
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        return
    
    emulator = PygameVideoEmulator(video_path)
    emulator.run()

if __name__ == '__main__':
    main()