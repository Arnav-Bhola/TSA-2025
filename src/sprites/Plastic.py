import pygame
import random

class Plastic(pygame.sprite.Sprite):
    def __init__(self, crab, turtle):
        super().__init__()
        
        # Load the plastic image
        self.image = pygame.image.load("assets/images/plastic.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))  # Resize if needed
        
        self.rect = self.image.get_rect()

        # Spawn from the right side randomly along the Y-axis
        self.rect.x = 800  # Right edge of the screen
        self.rect.y = random.randint(50, 550)  # Random vertical position

        # Randomly choose between Crab or Turtle as the target
        self.target = random.choice([crab, turtle])  

        self.speed = random.randint(1, 3) * 0.5  # Different speeds for variety
        self.health = 20

    def take_damage(self, amount=10):
        self.health -= amount
        if self.health <= 0:
            self.kill()
            return True
        return False

    def update(self):
        """Continuously move the plastic towards the player (crab or turtle)."""
        # Get the target's current position
        target_pos = pygame.Vector2(self.target.rect.centerx, self.target.rect.centery)
        current_pos = pygame.Vector2(self.rect.centerx, self.rect.centery)
        
        # Calculate a new direction towards the moving target
        direction = target_pos - current_pos
        if direction.length() != 0:  # Avoid division by zero
            direction = direction.normalize()
        
        # Move the plastic
        self.rect.x += direction.x * self.speed
        self.rect.y += direction.y * self.speed
        
        # Remove plastic when it moves off-screen
        if self.rect.right < 0:
            self.kill()
