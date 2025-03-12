import pygame
import math

class Turtle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        original_image = pygame.image.load("assets/images/turtle.png").convert_alpha()

        # Scale the image to a smaller size (adjust the values as needed)
        self.original_image = pygame.transform.scale(original_image, (100, 100))  
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(400, 300))

        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 5
        self.stop_distance = 5

    def update(self):
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Calculate direction vector
        direction = pygame.Vector2(mouse_x - self.pos.x, mouse_y - self.pos.y)
        distance = direction.length()  # Get distance to mouse

        # Move only if the player is not too close to the mouse
        if distance > self.stop_distance:
            direction = direction.normalize()  # Normalize for consistent speed
            self.pos += direction * self.speed  # Move in direction of the mouse

        # Rotate towards mouse
        if distance > 1:  # Avoid jittering when very close
            angle = math.degrees(math.atan2(-direction.y, direction.x))  
            self.image = pygame.transform.rotate(self.original_image, angle + 270)

        # Update rect to match new position
        self.rect = self.image.get_rect(center=self.pos)
