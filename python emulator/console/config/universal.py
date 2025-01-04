import os
import pygame
from controls import UniversalController


WHITE, BLACK, GRAY, RED, GREEN, LIGHT_BLUE = (255, 255, 255), (0, 0, 0), (200, 200, 200), (255, 0, 0), (0, 255, 0), (173, 216, 230)

def display_text(screen, text, position, font_size=30, color=(255, 255, 255)):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def draw_grid(surface, width, height, cell_size=20):
    for x in range(0, width, cell_size):
        pygame.draw.line(surface, GRAY, (x, 0), (x, height))
        if x % 100 == 0:
            display_text(surface, str(x), (x, 0), font_size=15, color=WHITE)
    for y in range(0, height, cell_size):
        pygame.draw.line(surface, GRAY, (0, y), (width, y))
        if y % 100 == 0:
            display_text(surface, str(y), (0, y), font_size=15, color=WHITE)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Universal Controller Configuration")

    controller = UniversalController()

    # Define the absolute path to the image
    image_path = os.path.join("C:\\Users\\mwanji\\Desktop\\programing code\\programing code\\python\\games\\python emulator\\img", "cool controller.png")
    
    # Load and resize the controller image
    try:
        controller_img = pygame.image.load(image_path)
        controller_img = pygame.transform.scale(controller_img, (500, 300))  # Resize to width 500 and height 300
        controller_img_rect = controller_img.get_rect(center=(400, 300))
        print("Image loaded and resized successfully.")
    except pygame.error as e:
        print(f"Error loading image: {e}")
        return

    # Variables to keep track of configuration state
    configuring = False
    current_action = None

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if configuring and current_action:
                    controller.set_key_binding(current_action, event.key)
                    configuring = False
                    current_action = None
                elif event.key == pygame.K_1:
                    controller.set_input_mode("keyboard")
                elif event.key == pygame.K_2:
                    controller.set_input_mode("controller")
                elif event.key == pygame.K_c:
                    configuring = True
                    current_action = 'action1'  # Example: configure 'action1' key

        # Get input state
        inputs = controller.get_input()

        # Clear screen
        screen.fill((0, 0, 0))
        draw_grid(screen, 800, 600, 20)

        # Display mode selection
        display_text(screen, "Press 1 for Keyboard, 2 for Controller", (50, 50))
        display_text(screen, f"Current mode: {controller.input_mode}", (50, 100))

        # Display configuration instructions
        if configuring:
            display_text(screen, f"Press a key to set as {current_action}", (50, 150))
        else:
            display_text(screen, "Press C to configure 'action1' key", (50, 150))

        # Draw controller image
        screen.blit(controller_img, controller_img_rect)


        # Loop through each controller and get their inputs
        for joy in controller.controllers:
            btn_count = joy.get_numbuttons()
            axis_count = joy.get_numaxes()
            hat_count = joy.get_numhats()

            for i in range(min(btn_count, 11)):
                if joy.get_button(i):
                    if inputs[f'action{i+1}']:
                        pygame.draw.circle(screen, (0, 255, 0), (controller_img_rect.left + 450, controller_img_rect.top + 150), 10)

            if hat_count > 0:
                hat_x, hat_y = joy.get_hat(0)
                if hat_x < 0:
                    if inputs['hatleft']:
                        pygame.draw.circle(screen, (0, 255, 0), (200, 150), 10)
                if hat_x > 0:
                    if inputs['hatright']:
                        pygame.draw.circle(screen, (0, 255, 0), (200, 150), 10)
                if hat_y > 0:
                    if inputs['hatUp']:
                        pygame.draw.circle(screen, (0, 255, 0), (200, 150), 10)
                if hat_y < 0:
                    if inputs['hatDown']:
                        pygame.draw.circle(screen, (0, 255, 0), (200, 150), 10)

            if axis_count > 0:
                if joy.get_axis(0) < -0.5:
                    if inputs['axleft']:
                        pygame.draw.circle(screen, (0, 255, 0), (200, 150), 10)
                if joy.get_axis(0) > 0.5:
                    if inputs['axright']:
                        pygame.draw.circle(screen, (0, 255, 0), (200, 150), 10)
            if axis_count > 1:
                if joy.get_axis(1) < -0.5:
                    if inputs['axUp']:
                        pygame.draw.circle(screen, (0, 255, 0), (200, 150), 10)
                if joy.get_axis(1) > 0.5:
                    if inputs['axDown']:
                        pygame.draw.circle(screen, (0, 255, 0), (200, 150), 10)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
