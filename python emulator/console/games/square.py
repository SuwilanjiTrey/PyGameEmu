import pygame
import tkinter as tk
from PIL import Image, ImageTk

class JoystickGame:
    def __init__(self, root):
        self.root = root
        self.width = 800
        self.height = 600
        self.init_ui()
        self.init_pygame()

    def init_ui(self):
        self.game_frame = tk.Frame(self.root, width=self.width, height=self.height)
        self.game_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.game_frame, width=self.width, height=self.height)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.exit_button = tk.Button(self.game_frame, text="Exit Game", command=self.stop_game)
        self.exit_button.place(x=10, y=10)

    def init_pygame(self):
        pygame.init()
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for joystick in self.joysticks:
            joystick.init()
        print(f"Number of joysticks detected: {len(self.joysticks)}")

        self.clock = pygame.time.Clock()
        self.surface = pygame.Surface((self.width, self.height))
        self.running = True

        self.square_pos = [self.width // 2, self.height // 2]
        self.square_size = 50
        self.square_vel = [0, 0]
        self.move_speed = 300

        self.update()
        self.handle_pygame_events()

    def update(self):
        if not self.running:
            return

        dt = self.clock.tick(60) / 1000.0

        self.square_pos[0] += self.square_vel[0] * dt
        self.square_pos[1] += self.square_vel[1] * dt

        if self.square_pos[0] < 0:
            self.square_pos[0] = 0
        elif self.square_pos[0] + self.square_size > self.width:
            self.square_pos[0] = self.width - self.square_size
        if self.square_pos[1] < 0:
            self.square_pos[1] = 0
        elif self.square_pos[1] + self.square_size > self.height:
            self.square_pos[1] = self.height - self.square_size

        self.surface.fill((255, 255, 255))
        pygame.draw.rect(self.surface, (0, 0, 255), (*self.square_pos, self.square_size, self.square_size))

        pygame_image = pygame.image.tostring(self.surface, 'RGB')
        pil_image = Image.frombytes('RGB', (self.width, self.height), pygame_image)
        tk_image = ImageTk.PhotoImage(pil_image)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
        self.canvas.image = tk_image

        if self.running:
            self.root.after(16, self.update)

    def handle_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                self.on_joy_axis_motion(event)
            elif event.type == pygame.JOYHATMOTION:
                self.on_joy_hat_motion(event)
            elif event.type == pygame.JOYBUTTONDOWN:
                self.on_joy_button_down(event)
            elif event.type == pygame.JOYBUTTONUP:
                self.on_joy_button_up(event)

        if self.running:
            self.root.after(16, self.handle_pygame_events)

    def on_joy_axis_motion(self, event):
        print(f"Joystick axis motion: Axis {event.axis}, Value {event.value}")
        if event.axis == 0:  # Typically the left-right axis
            self.square_vel[0] = self.move_speed * event.value
        elif event.axis == 1:  # Typically the up-down axis
            self.square_vel[1] = self.move_speed * event.value

    def on_joy_hat_motion(self, event):
        print(f"Joystick hat motion: Value {event.value}")
        x, y = event.value
        self.square_vel[0] = self.move_speed * x
        self.square_vel[1] = -self.move_speed * y

    def on_joy_button_down(self, event):
        print(f"Joystick button down: Button {event.button}")

    def on_joy_button_up(self, event):
        print(f"Joystick button up: Button {event.button}")

    def stop_game(self):
        self.running = False
        pygame.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    game = JoystickGame(root)
    root.mainloop()
