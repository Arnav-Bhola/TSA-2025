import pygame
import random

class Plastic(pygame.sprite.Sprite):
    def __init__(self, crab, turtle):
        super().__init__()

        # Load the plastic image
        self.image = pygame.image.load("assets/images/plastic.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))  # Resize the image

        # Define the main rectangle (positioning and rendering)
        self.rect = self.image.get_rect()

        # Spawn from the right side randomly along the Y-axis
        self.rect.x = 800  # Right edge of the screen
        self.rect.y = random.randint(50, 550)  # Random vertical position

        # Create a smaller hitbox (shrink by 20%) and center it
        hitbox_width = int(self.rect.width * 0.5)
        hitbox_height = int(self.rect.height * 0.5)
        self.hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.update_hitbox()  # Ensure it starts centered

        # Randomly choose between Crab or Turtle as the target
        self.target = random.choice([crab, turtle])

        self.speed = random.randint(1, 3) * 0.5  # Different speeds for variety
        self.health = 20
        
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
        # Handle blinking effect
        if self.blinking:
            # Check how much time has passed since blinking started
            elapsed_time = pygame.time.get_ticks() - self.blink_time
            if elapsed_time > self.blink_duration:
                # End the blinking effect after the duration
                self.blinking = False
                self.visible = True  # Ensure it's visible again
            else:
                # Alternate visibility for blinking effect
                self.visible = not self.visible

                # Apply brightness effect during blinking
                if self.visible:
                    # Make the plastic brighter by filling with semi-transparent white
                    bright_surface = self.image.copy()
                    bright_surface.fill((255, 255, 255, 60), special_flags=pygame.BLEND_ADD)
                    screen.blit(bright_surface, self.rect)
                    return  # Only draw the brightened version while blinking
                else:
                    return  # If not visible, don't draw the sprite

        # Normal movement and drawing logic if not blinking
        target_pos = pygame.Vector2(self.target.rect.centerx, self.target.rect.centery)
        current_pos = pygame.Vector2(self.rect.centerx, self.rect.centery)

        # Calculate movement direction
        direction = target_pos - current_pos
        if direction.length() != 0:  # Avoid division by zero
            direction = direction.normalize()

        # Move the plastic
        self.rect.x += direction.x * self.speed
        self.rect.y += direction.y * self.speed

        # Update hitbox position to stay centered
        self.update_hitbox()

        # Remove plastic when it moves off-screen
        if self.rect.right < 0:
            self.kill()

        # Draw the plastic only if it's visible
        if self.visible:
            screen.blit(self.image, self.rect)
