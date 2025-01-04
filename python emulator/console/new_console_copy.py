import pygame
import cv2
import sys
import os

class Button:
    def __init__(self, x, y, image_path, hover_image_path=None, scale=(0, 0)):
        # Load and resize images
        original_image = pygame.image.load(image_path)
        original_hover = pygame.image.load(hover_image_path) if hover_image_path else original_image
        
        self.image = pygame.transform.scale(original_image, scale)
        self.hover_image = pygame.transform.scale(original_hover, scale)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.current_image = self.image
    
    def draw(self, surface):
        surface.blit(self.current_image, self.rect)
    
    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_image(self, is_hover):
        self.current_image = self.hover_image if is_hover else self.image

class NavigationDrawer:
    def __init__(self, screen_width, screen_height):
        self.width = 300
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = -self.width
        self.open = False
        
        # Drawer background
        self.surface = pygame.Surface((self.width, screen_height), pygame.SRCALPHA)
        self.surface.fill((50, 50, 50, 200))  # Semi-transparent dark gray
        
        # Drawer buttons
        self.buttons = self.create_drawer_buttons()
    
    def create_drawer_buttons(self):
        buttons = []
        game_paths = [
            r'games\stick\Main.py',
            r'games\apple_game\shoot.py',
            r'games\garden\happy_garden.py',
            r'games\sleeping dragons\dragons.py'
        ]
        for i, path in enumerate(game_paths):
            btn = pygame.Rect(10, 50 + i*60, 280, 50)
            buttons.append({
                'rect': btn, 
                'name': f'Game {i+1}', 
                'path': path
            })
        return buttons
    
    def draw(self, screen):
        # Draw drawer
        self.surface.fill((50, 50, 50, 200))
        
        # Draw buttons
        font = pygame.font.Font(None, 36)
        for btn in self.buttons:
            pygame.draw.rect(self.surface, (100, 100, 100, 200), btn['rect'])
            text = font.render(btn['name'], True, (255, 255, 255))
            text_rect = text.get_rect(center=btn['rect'].center)
            self.surface.blit(text, text_rect)
        
        screen.blit(self.surface, (self.x, 0))
    
    def update(self):
        # Smooth drawer animation
        if self.open and self.x < 0:
            self.x += 20
        elif not self.open and self.x > -self.width:
            self.x -= 20
        
        self.x = max(-self.width, min(0, self.x))
    
    def toggle(self):
        self.open = not self.open
    
    def handle_click(self, pos):
        # Adjust position relative to drawer
        local_pos = (pos[0] - self.x, pos[1])
        for btn in self.buttons:
            if btn['rect'].collidepoint(local_pos):
                return btn
        return None

class PygameVideoEmulator:
    def __init__(self, video_path):
        pygame.init()
        pygame.display.set_caption('Pygame Video Emulator')
        
         # Add PygameZero wrapper
        self.pgzero_wrapper = None
        self.current_game_dir = None
        # Screen setup
        self.screen_width = 1020
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Video setup
        self.video_path = video_path
        self.video_capture = cv2.VideoCapture(video_path)
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        
        # Flags
        self.playing_video = True
        self.paused = False
        
        # Navigation drawer
        self.drawer = NavigationDrawer(self.screen_width, self.screen_height)
        
        # Overlay for fade effect
        self.overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.overlay_alpha = 0
        
        # Buttons
        self.setup_buttons()
    
    def setup_buttons(self):
        # Define button positions and image paths
        button_configs = [
            {
                'x': 0, 
                'y': 10, 
                'image': r'config\img\open_file.png', 
                'hover': r'config\img\open_file2.png'
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
        
        # Create buttons
        self.buttons = [
            Button(
                config['x'], 
                config['y'], 
                config.get('image', r'config\img\default.png'), 
                config.get('hover', r'config\img\default2.png'),
                scale=(50, 40)  # Customizable button size
            ) for config in button_configs
        ]
    
    def run(self):
        while True:
            # Get mouse position
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Open/close drawer
                    if event.button == 1:  # Left mouse button
                        # Check drawer buttons
                        clicked_button = self.drawer.handle_click(event.pos)
                        if clicked_button:
                            self.load_game(clicked_button['path'])
                        
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
            # Play loading video
            loading_video = r"config/img/loading.mp4"
            if os.path.exists(loading_video):
                self.play_loading_video(loading_video)
            
            # Get the directory of the main game file
            game_dir = os.path.dirname(os.path.abspath(game_path))
            
            # Add the game's directory to Python's module search path
            sys.path.insert(0, game_dir)
            
            # Read the game file contents
            with open(game_path, 'r') as file:
                game_code = file.read()
            
            # Initialize the PygameZero wrapper
            from pgzero_compat import PygameZeroWrapper
            self.pgzero_wrapper = PygameZeroWrapper(self.screen, game_path)
            
            # Check if it's a Pygame Zero game
            if self.pgzero_wrapper.is_pgzero_game(game_code):
                print("Loading as Pygame Zero game...")
                
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
                    
                    pygame.display.flip()
                    clock.tick(60)
            
            else:
                print("Loading as regular Pygame game...")
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
            
            # Remove the game directory from sys.path
            sys.path.pop(0)
            
        except Exception as e:
            print(f"Error loading game: {e}")
            import traceback
            traceback.print_exc()
    
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
    #basedir = os.file.path((__file__))

    #video_path = os.path.join(basedir, "", "", "", "")
    
    video_path = r"config/img/play-game.mp4"
    
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        return
    
    emulator = PygameVideoEmulator(video_path)
    emulator.run()

if __name__ == '__main__':
    main()