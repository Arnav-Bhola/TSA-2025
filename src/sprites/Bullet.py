import pygame
import math

class TurtleBullet(pygame.sprite.Sprite):
    """Bullet class for shooting towards mouse cursor."""
    def __init__(self, start_pos, target_pos):
        super().__init__()
        
        # Load and scale bullet image
        original_image = pygame.image.load("assets/images/web.png").convert_alpha()
        self.original_image = pygame.transform.scale(original_image, (30, 30))

        # Calculate angle between crab and mouse
        self.angle = math.degrees(math.atan2(target_pos[1] - start_pos[1], target_pos[0] - start_pos[0]))

        # Rotate bullet image
        self.image = pygame.transform.rotate(self.original_image, -self.angle + 135)
        self.rect = self.image.get_rect(center=start_pos)

        # Define speed and direction
        self.speed = 7
        self.velocity = pygame.Vector2(math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))) * self.speed

    def update(self):
        """Move the bullet in the calculated direction."""
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Remove bullet if it leaves the screen
        if not (0 <= self.rect.x <= 800 and 0 <= self.rect.y <= 600):
            self.kill()

class CrabBullet(pygame.sprite.Sprite):
    def __init__(self, position, direction):
        super().__init__()
        
        # Load the bullet image
        original_image = pygame.image.load("assets/images/crab_scute.png").convert_alpha()
        self.original_image = pygame.transform.scale(original_image, (30, 30))  # Resize if needed
        
        # Calculate angle to rotate the bullet in the shooting direction
        angle = math.degrees(math.atan2(-direction.y, direction.x))
        self.image = pygame.transform.rotate(self.original_image, angle + 270)
        
        self.rect = self.image.get_rect(center=position)
        
        self.speed = 7
        self.velocity = direction * self.speed  # Set velocity based on direction

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Remove bullet if it goes off screen
        if self.rect.right < 0 or self.rect.left > 800 or self.rect.top > 600 or self.rect.bottom < 0:
            self.kill()
    
    