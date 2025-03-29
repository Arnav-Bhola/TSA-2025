import pygame
import random

class Plastic(pygame.sprite.Sprite):
    def __init__(self, crab, turtle, screen, wave_number):
        super().__init__()

        # Load the plastic image
        self.image = pygame.image.load("assets/images/plastic.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))  # Resize the image

        # Define the main rectangle (positioning and rendering)
        self.rect = self.image.get_rect()

        # Spawn from the right side randomly along the Y-axis
        screen_width = screen.get_width()
        self.rect.x = screen_width - 100 # Right edge of the screen
        self.rect.y = random.randint(50, 550)  # Random vertical position

        # Create a smaller hitbox (shrink by 20%) and center it
        hitbox_width = int(self.rect.width * 0.5)
        hitbox_height = int(self.rect.height * 0.5)
        self.hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.update_hitbox()  # Ensure it starts centered

        # Randomly choose between Crab or Turtle as the target
        self.target = crab

        self.speed = random.randint(1, 3) * (wave_number / 7)  # Different speeds for 
        if self.speed < 1: self.speed = 1
        self.health = 100
        
        # Blinking effect variables
        self.blinking = False  # Whether the plastic is blinking
        self.blink_time = 0  # Time when the blinking effect started
        self.blink_duration = 500  # Duration of blinking effect in milliseconds
        self.visible = True  # Whether the plastic is visible during blinking

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def take_damage(self, amount=10):
        self.health -= amount
        if self.health <= 0:
            self.kill()
            return True
        
        # Start blinking effect when taking damage
        self.blinking = True
        self.blink_time = pygame.time.get_ticks()  # Record the time the damage was taken
        return False

    def update(self, screen):
        """Move the plastic towards the target and update hitbox."""

        # Handle blinking effect (same as before)
        if self.blinking:
            elapsed_time = pygame.time.get_ticks() - self.blink_time
            if elapsed_time > self.blink_duration:
                self.blinking = False
                self.visible = True
            else:
                self.visible = not self.visible
                if self.visible:
                    bright_surface = self.image.copy()
                    bright_surface.fill((255, 255, 255, 60), special_flags=pygame.BLEND_ADD)
                    screen.blit(bright_surface, self.rect)
                    return
                else:
                    return

        # Calculate direction to the target
        target_pos = pygame.Vector2(self.target.rect.centerx, self.target.rect.centery)
        current_pos = pygame.Vector2(self.rect.centerx, self.rect.centery)
        direction = target_pos - current_pos

        # Ensure direction is valid and normalized
        if direction.length() > 1:
            direction = direction.normalize()
        else:
            # Apply a small nudge towards the target to prevent getting stuck
            direction = pygame.Vector2(random.choice([-1, 1]), random.choice([-1, 1])).normalize()

        # Move the plastic
        self.rect.x += direction[0] * self.speed
        self.rect.y += direction[1] * self.speed

        pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2) 

        # Update hitbox
        self.update_hitbox()

        # Remove plastic when it moves off-screen
        if self.rect.right < 0:  # Check if the plastic is off-screen
            self.kill()

        # Draw the plastic
        if self.visible:
            screen.blit(self.image, self.rect)

class PlasticBoss(Plastic):
    def __init__(self, crab, turtle, screen, wave_number, plastic_group):
        # Initialize the parent Plastic class with all required parameters
        super().__init__(crab, turtle, screen, wave_number)
        
        # Store references to the players
        self.crab = crab
        self.turtle = turtle
        self.wave_number = wave_number
        self.plastic_group= plastic_group
        
        # Boss-specific attributes
        self.health = 100 + (wave_number * 50)  # Boss has more health
        self.size = 100  # Bigger size for boss
        self.spawn_timer = 0
        self.spawn_interval = 5000  # Spawn minions every 3 seconds
        
        # Create boss image
        self.image = pygame.image.load("assets/images/monster.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.rect = self.image.get_rect()
        self.original_image = self.image.copy()
        self.speed = 1  # Slower movement
        
        # Set initial position (you might want to customize this)
        self.rect.centerx = random.randint(100, screen.get_width() - 100)
        self.rect.centery = random.randint(100, screen.get_height() - 100)
        
    def update(self, screen):
        super().update(screen)
        current_time = pygame.time.get_ticks()
        
        # Spawn minions at regular intervals
        if current_time - self.spawn_timer > self.spawn_interval:
            self.spawn_minions(screen)
            self.spawn_timer = current_time
            
    def spawn_minions(self, screen):
        # Spawn 2-4 regular plastic enemies around the boss
        minion_count = 2 + (self.health % 3)  # Random between 2-4
        
        for _ in range(minion_count):
            # Create minion near the boss
            minion = Plastic(self.crab, self.turtle, screen, self.wave_number)
            minion.rect.centerx = self.rect.centerx + random.randint(-50, 50)
            minion.rect.centery = self.rect.centery + random.randint(-50, 50)
            self.plastic_group.add(minion)