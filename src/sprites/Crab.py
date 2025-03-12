import pygame
import math

class Crab(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        original_image = pygame.image.load("assets/images/crab.png").convert_alpha()

        # Scale the image to a smaller size (adjust the values as needed)
        self.original_image = pygame.transform.scale(original_image, (120, 120))  
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(200, 200))

        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 3

    def update(self, keys):
        # Movement handling
        if keys[pygame.K_w]:
            self.pos.y -= self.speed
        if keys[pygame.K_s]:
            self.pos.y += self.speed
        if keys[pygame.K_a]:
            self.pos.x -= self.speed
        if keys[pygame.K_d]:
            self.pos.x += self.speed

        # Prevent going out of screen
        screen_width, screen_height = 800, 600  # Screen dimensions
        self.pos.x = max(0, min(screen_width - self.rect.width, self.pos.x))
        self.pos.y = max(0, min(screen_height - self.rect.height, self.pos.y))

        # Rotate towards movement direction
        movement_vector = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]:
            movement_vector = pygame.Vector2(self.pos.x - self.rect.centerx, self.pos.y - self.rect.centery)
            if movement_vector.length() > 0:
                angle = math.degrees(math.atan2(-movement_vector.y, movement_vector.x))
                self.image = pygame.transform.rotate(self.original_image, angle + 270)

        self.rect = self.image.get_rect(center=self.pos)
