import pygame
import os
from pathlib import Path

class ScreenWrapper:
    def __init__(self, pygame_surface):
        self._surface = pygame_surface
        self.draw = DrawingHandler(pygame_surface)
        self._image_cache = {}  # Cache for loaded images
        
    def _load_image(self, image_name):
        if image_name in self._image_cache:
            return self._image_cache[image_name]
            
        possible_paths = [
            Path(image_name),
            Path('images') / image_name,
            Path('images') / f"{image_name}.png",
            Path('images') / f"{image_name}.jpg",
            Path('assets') / 'images' / image_name,
            Path('assets') / 'images' / f"{image_name}.png",
            Path('assets') / 'images' / f"{image_name}.jpg",
        ]
        
        image_path = None
        for path in possible_paths:
            if path.exists():
                image_path = str(path)
                break
                
        if not image_path:
            raise FileNotFoundError(f"Could not find image: {image_name}")
            
        try:
            image = pygame.image.load(image_path).convert_alpha()
            self._image_cache[image_name] = image
            return image
        except pygame.error as e:
            print(f"Error loading image {image_path}: {e}")
            raise

    def blit(self, source, *args, **kwargs):
        if isinstance(source, str):
            # If source is a string (image name), load the image
            surface = self._load_image(source)
        else:
            # If source is already a surface, use it directly
            surface = source
        return self._surface.blit(surface, *args, **kwargs)

    def clear(self):
        self._surface.fill((0, 0, 0))

    def __getattr__(self, name):
        return getattr(self._surface, name)

class DrawingHandler:
    def __init__(self, screen):
        self.screen = screen
        self._default_font = pygame.font.Font(None, 36)
    
    def line(self, start_pos, end_pos, color=(255,255,255)):
        """Draw a line on the screen"""
        pygame.draw.line(self.screen, color, start_pos, end_pos)
    
    def text(self, text, *, topleft=None, color=(255, 255, 255), fontsize=36):
        """Draw text on the screen"""
        font = pygame.font.Font(None, fontsize)
        text_surface = font.render(str(text), True, color)
        if topleft:
            self.screen.blit(text_surface, topleft)
        else:
            self.screen.blit(text_surface, (0, 0))

class PygameZeroWrapper:
    def __init__(self, screen, game_path):
        self.screen = ScreenWrapper(screen)
        self.game_path = Path(game_path)
        self.game_dir = self.game_path.parent
        self.actors = {}
        self._setup_environment()
    
    def _setup_environment(self):
        """Set up the Pygame Zero environment"""
        self.keyboard = KeyboardHandler()
        self.mouse = MouseHandler()
    
    def is_pgzero_game(self, code_content):
        """Check if the game uses Pygame Zero features"""
        pgzero_indicators = [
            'Actor(',
            'actor =',
            'actors =',
            'screen.draw',
            'keyboard.',
            'pgzero',
            'def draw():',
            'def update():'
        ]
        return any(indicator in code_content for indicator in pgzero_indicators)
    
    def create_namespace(self):
        """Create a namespace for running the Pygame Zero game"""
        return {
            'Actor': self.Actor,
            'screen': self.screen,
            'keyboard': self.keyboard,
            'mouse': self.mouse,
            'music': MusicHandler(),
            'sounds': SoundHandler(self.game_dir),
            'clock': ClockHandler()
        }

    def Actor(self, image_name, **kwargs):
        """Pygame Zero Actor compatibility class with keyword argument support"""
        actor_id = len(self.actors)
        
        class ActorWrapper:
            def __init__(self, wrapper, image_name, actor_id, **kwargs):
                self.wrapper = wrapper
                self.actor_id = actor_id
                self._images = {}  # Store multiple images
                self._current_image_name = image_name
                self._scale = 1.0
                
                # Initialize position
                self.x = 0
                self.y = 0
                
                # Handle pos parameter if provided
                if 'pos' in kwargs:
                    self.x, self.y = kwargs['pos']
                elif 'center' in kwargs:
                    self.x, self.y = kwargs['center']
                elif 'topleft' in kwargs:
                    self.x, self.y = kwargs['topleft']
                    
                # Load the image after position is set
                self._load_image(image_name)
                
                # Handle anchor if provided
                if 'anchor' in kwargs:
                    self._handle_anchor(kwargs['anchor'])
            
            def _handle_anchor(self, anchor):
                """Handle anchor point for the actor"""
                if isinstance(anchor, tuple):
                    anchor_x, anchor_y = anchor
                    self.x += self.rect.width * anchor_x
                    self.y += self.rect.height * anchor_y
                elif isinstance(anchor, str):
                    # Handle string-based anchors (e.g., 'center', 'topleft', etc.)
                    if anchor == 'center':
                        pass  # Default behavior is center
                    elif anchor == 'topleft':
                        self.x += self.rect.width / 2
                        self.y += self.rect.height / 2
                    # Add more anchor points as needed
            
            def _load_image(self, image_name):
                if image_name in self._images:
                    return
                
                possible_paths = [
                    Path(image_name),
                    Path('images') / image_name,
                    Path('images') / f"{image_name}.png",
                    Path('images') / f"{image_name}.jpg",
                    Path('assets') / 'images' / image_name,
                    Path('assets') / 'images' / f"{image_name}.png",
                    Path('assets') / 'images' / f"{image_name}.jpg",
                ]
                
                image_path = None
                for path in possible_paths:
                    if path.exists():
                        image_path = str(path)
                        break
                
                if not image_path:
                    raise FileNotFoundError(f"Could not find image: {image_name}")
                
                try:
                    self._images[image_name] = pygame.image.load(image_path).convert_alpha()
                except pygame.error as e:
                    print(f"Error loading image {image_path}: {e}")
                    raise
                
                self._update_image()
            
            def _update_image(self):
                self._orig_image = self._images[self._current_image_name]
                if self._scale != 1.0:
                    new_size = (
                        int(self._orig_image.get_width() * self._scale),
                        int(self._orig_image.get_height() * self._scale)
                    )
                    self._image = pygame.transform.scale(self._orig_image, new_size)
                else:
                    self._image = self._orig_image
                self.rect = self._image.get_rect()
                self.rect.center = (self.x, self.y)
            
            @property
            def image(self):
                return self._current_image_name
            
            @image.setter
            def image(self, new_image_name):
                if new_image_name != self._current_image_name:
                    self._load_image(new_image_name)
                    self._current_image_name = new_image_name
                    self._update_image()
            
            @property
            def scale(self):
                return self._scale
            
            @scale.setter
            def scale(self, value):
                if self._scale != value:
                    self._scale = value
                    self._update_image()
            
            def draw(self):
                self.rect.center = (self.x, self.y)
                self.wrapper.screen.blit(self._image, self.rect)
            
            def colliderect(self, other):
                return self.rect.colliderect(other.rect)
            
            def collidepoint(self, pos):
                return self.rect.collidepoint(pos)
            
            @property
            def pos(self):
                return (self.x, self.y)
            
            @pos.setter
            def pos(self, value):
                self.x, self.y = value
            
            # Add all the rect properties
            @property
            def left(self): return self.rect.left
            @property
            def right(self): return self.rect.right
            @property
            def top(self): return self.rect.top
            @property
            def bottom(self): return self.rect.bottom
            @property
            def width(self): return self.rect.width
            @property
            def height(self): return self.rect.height
            @property
            def center(self): return self.rect.center
            
            @center.setter
            def center(self, value):
                self.x, self.y = value
                self.rect.center = value

        actor = ActorWrapper(self, image_name, actor_id, **kwargs)
        self.actors[actor_id] = actor
        return actor
    
    def update(self):
        """Update all game components"""
        self.keyboard.update()
        self.mouse.update()

class KeyboardHandler:
    def __init__(self):
        self.keys = {}
        # Add common key attributes
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.space = False
        
    def update(self):
        keys = pygame.key.get_pressed()
        self.left = keys[pygame.K_LEFT]
        self.right = keys[pygame.K_RIGHT]
        self.up = keys[pygame.K_UP]
        self.down = keys[pygame.K_DOWN]
        self.space = keys[pygame.K_SPACE]

class MouseHandler:
    def __init__(self):
        self.pos = (0, 0)
        self.buttons = [False, False, False]
        
    def update(self):
        self.pos = pygame.mouse.get_pos()
        self.buttons = pygame.mouse.get_pressed()

class MusicHandler:
    def play(self, name):
        pass
    
    def stop(self):
        pygame.mixer.music.stop()

class SoundHandler:
    def __init__(self, game_dir):
        self.game_dir = game_dir
        self.sounds = {}
    
    def play(self, name):
        if name not in self.sounds:
            path = self.game_dir / 'sounds' / f"{name}.wav"
            if path.exists():
                self.sounds[name] = pygame.mixer.Sound(str(path))
        if name in self.sounds:
            self.sounds[name].play()

class ClockHandler:
    def __init__(self):
        self._scheduled = []
    
    def schedule(self, callback, delay):
        """Schedule a one-time callback after delay seconds"""
        current_time = pygame.time.get_ticks()
        self._scheduled.append({
            'callback': callback,
            'time': current_time + (delay * 1000),
            'repeat': False,
            'delay': delay
        })
    
    def schedule_interval(self, callback, interval):
        """Schedule a callback to be run every interval seconds"""
        current_time = pygame.time.get_ticks()
        self._scheduled.append({
            'callback': callback,
            'time': current_time + (interval * 1000),
            'repeat': True,
            'delay': interval
        })
    
    def schedule_unique(self, callback, delay):
        """Schedule a callback, removing any previous instances of it first"""
        current_time = pygame.time.get_ticks()
        # Remove any existing callbacks of the same function
        self._scheduled = [s for s in self._scheduled if s['callback'] != callback]
        self._scheduled.append({
            'callback': callback,
            'time': current_time + (delay * 1000),
            'repeat': False,
            'delay': delay
        })
    
    def unschedule(self, callback):
        """Remove all instances of callback from the schedule"""
        self._scheduled = [s for s in self._scheduled if s['callback'] != callback]
    
    def update(self):
        """Update the clock and run any callbacks that are due"""
        current_time = pygame.time.get_ticks()
        for task in self._scheduled[:]:  # Create a copy of the list to safely modify during iteration
            if current_time >= task['time']:
                try:
                    task['callback']()
                except Exception as e:
                    print(f"Error in scheduled callback: {e}")
                
                if task['repeat']:
                    # For repeating tasks, schedule the next occurrence
                    task['time'] = current_time + (task['delay'] * 1000)
                else:
                    # For one-time tasks, remove them from the schedule
                    self._scheduled.remove(task)