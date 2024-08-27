import pygame

class Fighter():
    #constructors
    def __init__(self,player ,x, y, flip ,data,sprite_sheet, animation_steps, sound_fx):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 5 #5 = idle, 7 = run, 6=jump,  1 & 2= attack, 4 = attack 2, 8 = hit, 6 = death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x , y, 80, 180 ))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attack_sound = sound_fx
        self.hit = False
        self.health = 100
        self.alive = True

    def load_images(self, sprite_sheet, animation_steps):
        animation_list=[]
        for y, animation in enumerate(animation_steps):
        
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y* self.size, self.size, self.size)
                newscale = pygame.transform.scale(temp_img,(self.size * self.image_scale, self.size * self.image_scale))
                temp_img_list.append(newscale)
            animation_list.append(temp_img_list)
            #print(animation_list)
        return animation_list

    def move(self, screen_width, screen_height, surface, target, round_over):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        #get keypresses
        key = pygame.key.get_pressed()

        #can only perform other actions if not currently attacking
        if self.attacking == False and self.alive == True and round_over == False:

            #check if player 1
            if self.player == 1:
                #movement
                if key[pygame.K_a]:    #check key presses
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.running = True
                #jump
                if key[pygame.K_w] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True

                #attack
                if key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(target)
                    #determine which attck type was used
                    if key[pygame.K_r]:
                        self.attack_type = 1
                    if key[pygame.K_t]:
                        self.attack_type = 2


            #check if player 1
            if self.player == 2:
                #movement
                if key[pygame.K_LEFT]:    #check key presses
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True
                #jump
                if key[pygame.K_UP] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True

                #attack
                if key[pygame.K_KP1] or key[pygame.K_KP2]:
                    self.attack(target)
                    #determine which attck type was used
                    if key[pygame.K_KP1]:
                        self.attack_type = 1
                    if key[pygame.K_KP2]:
                        self.attack_type = 2




        #apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        #ENSURE PLAYER STAYS ON SCREEN
        if self.rect.left + dx < 0:
            dx = 0 -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right

        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom


        #ENSURE PLAYERS FACE EACH OTHER
        if target.rect.centerx > self.rect.centerx:
            self.flip = False

        else:
            self.flip = True

        #apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.rect.x += dx
        self.rect.y += dy


    def update(self):
        if self.health <= 0:
            self.health = 0
            #death
            self.alive = False
            self.update_action(3)
        #check what action the player is performing
        elif self.hit == True:
            self.update_action(7) #hit
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(0) #attck 1
            elif self.attack_type == 2:
                self.update_action(1)    #attack 2  
        elif self.jump == True:
            self.update_action(5) #jump      
        elif self.running == True:
            self.update_action(6) #run
        else:
            self.update_action(4) #idle




        cooldown = 50
        #update image
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
            #check if the animation has finished
            if self.frame_index >= len(self.animation_list[self.action]):
                 #if the player is dead, end the animation
                if self.alive == False:
                    self.frame_index = len(self.animation_list[self.action]) - 1
                else:
                 
                 #check if an attack was executed
                    if self.attacking:
                    # End the attack
                        self.attacking = False
                        self.attack_cooldown = 20
                    
                    self.frame_index = 0
                    if self.action == 7:  # If hit animation is complete
                        self.hit = False
                        # if player is in the middle of attack , then the attcak is stopped
                        self.attacking = False
                        self.attack_cooldown = 20
                
                

    def attack(self, target):
        if self.attack_cooldown == 0:
 
            #execute attack
            self.attack_sound.play()
            self.attacking = True
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
            
            #check for colllision
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True
            #pygame.draw.rect(surface, (0,255,0), attacking_rect)

   
    def update_action(self, new_action):
        #check if the new action is different from the previous one
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
    
    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        #pygame.draw.rect(surface, (255, 0, 0), self.rect)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale))) 