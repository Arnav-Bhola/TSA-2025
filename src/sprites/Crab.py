import pygame
import math
from sprites.Bullet import CrabBullet

class Crab(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        original_image = pygame.image.load("assets/images/crab.png").convert_alpha()
        self.original_image = pygame.transform.scale(original_image, (100, 80))  
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(200, 200))

        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 3
        self.angle = 0  # Store the current rotation angle

        self.health = 3

        self.shoot_cooldown = 300  
        self.last_shot_time = 0  

    def update(self, keys):
        movement_vector = pygame.Vector2(0, 0)

        if keys[pygame.K_w]:
            movement_vector.y -= 1
        if keys[pygame.K_s]:
            movement_vector.y += 1
        if keys[pygame.K_a]:
            movement_vector.x -= 1
        if keys[pygame.K_d]:
            movement_vector.x += 1

        # Normalize movement so diagonal speed is the same
        if movement_vector.length() > 0:
            movement_vector = movement_vector.normalize() * self.speed

        # Update position
        self.pos += movement_vector

        # Get current image size
        image_width, image_height = self.image.get_size()

        # Clamp position to screen boundaries
        screen_width, screen_height = 800, 600
        self.pos.x = max(image_width // 2, min(screen_width - image_width // 2, self.pos.x))
        self.pos.y = max(image_height // 2, min(screen_height - image_height // 2, self.pos.y))

        # Rotate crab based on movement
        if movement_vector.length() > 0:
            self.angle = math.degrees(math.atan2(-movement_vector.y, movement_vector.x))
            self.image = pygame.transform.rotate(self.original_image, self.angle + 270)

        # Update rect
        self.rect = self.image.get_rect(center=self.pos)


    def shoot(self, bullets_group):
        """Shoot a bullet in the direction the crab is facing."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            # Convert angle to radians for velocity calculation
            angle_rad = math.radians(self.angle)
            direction = pygame.Vector2(math.cos(angle_rad), -math.sin(angle_rad))  # Negative sin to match Pygame's coordinate system

            bullet = CrabBullet(self.rect.center, direction)  
            bullets_group.add(bullet)
            self.last_shot_time = current_time

    def take_damage(self, amount=1):
        """Decreases the turtle's health and checks for game over."""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
