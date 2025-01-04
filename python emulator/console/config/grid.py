import pygame
import math
import os

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Physics Simulation")

# Define colors for easy use throughout the program
WHITE, BLACK, GRAY, RED, GREEN, BLUE, YELLOW = (255, 255, 255), (0, 0, 0), (200, 200, 200), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)

# Set up font for text display
font = pygame.font.Font(None, 26)

def display_text(surface, text, position, font_size=20, color=BLACK):
    """Render and display text on the given surface."""
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

def draw_grid(surface, width, height, cell_size=20):
    """Draw a grid on the given surface with labels every 100 pixels."""
    for x in range(0, width, cell_size):
        pygame.draw.line(surface, GRAY, (x, 0), (x, height))
        if x % 100 == 0:
            display_text(surface, str(x), (x, 0), font_size=15, color=WHITE)
    for y in range(0, height, cell_size):
        pygame.draw.line(surface, GRAY, (0, y), (width, y))
        if y % 100 == 0:
            display_text(surface, str(y), (0, y), font_size=15, color=WHITE)

class PhysicsObject:
    """Base class for all physics objects in the simulation."""
    def __init__(self, x, y, color=RED):
        self.x = x  # x-coordinate
        self.y = y  # y-coordinate
        self.vx = 0  # velocity in x-direction
        self.vy = 0  # velocity in y-direction
        self.ax = 0  # acceleration in x-direction
        self.ay = 0  # acceleration in y-direction
        self.color = color

    def update(self, dt):
        """Update position and velocity based on acceleration and time step."""
        self.vx += self.ax * dt  # v = v0 + a*t
        self.vy += self.ay * dt
        self.x += self.vx * dt  # x = x0 + v*t
        self.y += self.vy * dt

    def draw(self, surface):
        """Draw the object on the given surface."""
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 5)

class ProjectileMotion(PhysicsObject):
    """Class for simulating projectile motion."""
    def __init__(self, x, y, v0, angle):
        super().__init__(x, y, BLUE)
        self.v0 = v0  # initial velocity
        self.angle = math.radians(angle)  # convert angle to radians
        self.vx = v0 * math.cos(self.angle)  # initial x-velocity
        self.vy = -v0 * math.sin(self.angle)  # initial y-velocity (negative because y increases downwards)
        self.ay = 9.8  # acceleration due to gravity
        self.path = [(x, y)]  # list to store the path of the projectile

    def update(self, dt):
        """Update projectile position and store its path."""
        super().update(dt)
        self.path.append((self.x, self.y))
        if self.y > HEIGHT:  # stop the projectile at the bottom of the screen
            self.y = HEIGHT
            self.vy = 0
        if self.x > WIDTH:  # stop the projectile at the bottom of the screen
            self.x = WIDTH
            self.vy = 0

    def draw(self, surface):
        """Draw the projectile and its path."""
        super().draw(surface)
        if len(self.path) > 1:
            pygame.draw.lines(surface, self.color, False, self.path, 2)

class CircularMotion(PhysicsObject):
    """Class for simulating circular motion."""
    def __init__(self, x, y, radius, angular_velocity):
        super().__init__(x, y, GREEN)
        self.center_x = x  # x-coordinate of the center
        self.center_y = y  # y-coordinate of the center
        self.radius = radius
        self.angular_velocity = angular_velocity  # in radians per second
        self.angle = 0  # current angle

    def update(self, dt):
        """Update position based on angular velocity."""
        self.angle += self.angular_velocity * dt
        self.x = self.center_x + self.radius * math.cos(self.angle)
        self.y = self.center_y + self.radius * math.sin(self.angle)

class linearMotion(PhysicsObject):
    def __init__(self, x, y):
        super().__init__(x, y, GREEN)
        #self.vx = 1000  # Constant velocity
        self.vy = -100


class MovableImage:
    """Class for a movable image on the screen."""
    def __init__(self, image_path, x, y):
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self, surface):
        """Draw the image on the given surface."""
        surface.blit(self.image, self.rect)

    def move(self, dx, dy):
        """Move the image by the given amount."""
        self.rect.x += dx
        self.rect.y += dy

def main():
    clock = pygame.time.Clock()
    running = True
    
    objects = []  # list to store all physics objects
    simulation_mode = None  # current simulation mode

    # Load the movable image
    image_path = os.path.join(os.path.dirname(__file__), "img", "car.png")
    movable_image = MovableImage(image_path, WIDTH // 2, HEIGHT // 2)

    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds (1/60 fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x, y = pygame.mouse.get_pos()
                    if simulation_mode == "projectile":
                        objects.append(ProjectileMotion(x, y, 200, 45))  # Initial velocity 200, angle 45 degrees
                    elif simulation_mode == "circular":
                        objects.append(CircularMotion(x, y, 100, 2))  # Radius 100, angular velocity 2 rad/s
                    elif simulation_mode == "linear":
                        objects.append(linearMotion(x,y))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    simulation_mode = "projectile"
                elif event.key == pygame.K_c:
                    simulation_mode = "circular"
                elif event.key == pygame.K_l:
                    simulation_mode = "linear"
                elif event.key == pygame.K_SPACE:
                    objects.clear()  # Clear all physics objects

        # Move the image with arrow keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            movable_image.move(-5, 0)
        if keys[pygame.K_RIGHT]:
            movable_image.move(5, 0)
        if keys[pygame.K_UP]:
            movable_image.move(0, -5)
        if keys[pygame.K_DOWN]:
            movable_image.move(0, 5)

        # Clear the screen and draw the grid
        screen.fill(WHITE)
        draw_grid(screen, WIDTH, HEIGHT, 20)

        # Update and draw all physics objects
        for obj in objects:
            obj.update(dt)
            obj.draw(screen)

        # Draw the movable image
        movable_image.draw(screen)

        # Display instructions and current mode
        display_text(screen, "Press 'P' for Projectile Motion", (10, 10))
        display_text(screen, "Press 'C' for Circular Motion", (10, 40))
        display_text(screen, "Press 'L' for Linear Motion", (10, 70))
        display_text(screen, "Press 'SPACE' to Clear", (10, 100))

        display_text(screen, "Use Arrow Keys to Move Image", (10, 130))
        display_text(screen, f"Current Mode: {simulation_mode}", (10, 160))

        # Update the display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()