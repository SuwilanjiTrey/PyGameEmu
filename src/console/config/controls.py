import pygame

class UniversalController:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.controllers = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for controller in self.controllers:
            controller.init()
        
        self.input_mode = "controller"
        self.keys = {
            'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT,
            'action1': pygame.K_SPACE, 'action2': pygame.K_RETURN, 'action3': pygame.K_a, 'action4': pygame.K_s,
            'action5': pygame.K_d, 'action6': pygame.K_f, 'action7': pygame.K_y, 'action8': pygame.K_u,
            'action9': pygame.K_i, 'action10': pygame.K_o, 'action11': pygame.K_p, 'action12': pygame.K_j,
            'action13': pygame.K_k, 'action14': pygame.K_l, 'axUp': pygame.K_w, 'axDown': pygame.K_s,
            'axleft': pygame.K_a, 'axright': pygame.K_d, 'hatUp': pygame.K_UP, 'hatDown': pygame.K_DOWN,
            'hatleft': pygame.K_LEFT, 'hatright': pygame.K_RIGHT,
        }
        self.inputs = {action: False for action in self.keys}
        self.previous_inputs = self.inputs.copy()
        self.deadzone = 0.1
        self.enabled_joysticks = [True] * len(self.controllers)
    
    def toggle_joystick(self, index):
        if 0 <= index < len(self.enabled_joysticks):
            self.enabled_joysticks[index] = not self.enabled_joysticks[index]
            print(f"Joystick {index} {'enabled' if self.enabled_joysticks[index] else 'disabled'}")
    
    def update(self):
        self.previous_inputs = self.inputs.copy()
        self.inputs = {action: False for action in self.keys}
        
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN and self.enabled_joysticks[event.joy]:
                button = f'action{event.button + 1}'
                if button in self.inputs:
                    self.inputs[button] = True
            elif event.type == pygame.JOYAXISMOTION and self.enabled_joysticks[event.joy]:
                if event.axis == 0:
                    self.inputs['axleft'] = event.value < -self.deadzone
                    self.inputs['axright'] = event.value > self.deadzone
                elif event.axis == 1:
                    self.inputs['axUp'] = event.value < -self.deadzone
                    self.inputs['axDown'] = event.value > self.deadzone
            elif event.type == pygame.JOYHATMOTION and self.enabled_joysticks[event.joy]:
                x, y = event.value
                self.inputs['hatleft'] = x < 0
                self.inputs['hatright'] = x > 0
                self.inputs['hatUp'] = y > 0
                self.inputs['hatDown'] = y < 0
        
        for i, controller in enumerate(self.controllers):
            if self.enabled_joysticks[i]:
                for j in range(controller.get_numbuttons()):
                    if controller.get_button(j):
                        button = f'action{j + 1}'
                        if button in self.inputs:
                            self.inputs[button] = True
                
                for j in range(controller.get_numaxes()):
                    axis_value = controller.get_axis(j)
                    if j == 0:
                        self.inputs['axleft'] |= axis_value < -self.deadzone
                        self.inputs['axright'] |= axis_value > self.deadzone
                    elif j == 1:
                        self.inputs['axUp'] |= axis_value < -self.deadzone
                        self.inputs['axDown'] |= axis_value > self.deadzone

                for hat_index in range(controller.get_numhats()):
                    hat_x, hat_y = controller.get_hat(hat_index)
                    self.inputs['hatleft'] |= hat_x < 0
                    self.inputs['hatright'] |= hat_x > 0
                    self.inputs['hatUp'] |= hat_y > 0
                    self.inputs['hatDown'] |= hat_y < 0
        
        if self.input_mode == "keyboard":
            keys = pygame.key.get_pressed()
            for action, key in self.keys.items():
                self.inputs[action] = keys[key]
    
    def get_input(self):
        return self.inputs
    
    def get_button_down(self, action):
        return self.inputs[action] and not self.previous_inputs[action]
