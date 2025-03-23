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

        # Create a smaller hitbox
        hitbox_width = int(self.rect.width * 0.7)
        hitbox_height = int(self.rect.height * 0.7)
        self.hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.update_hitbox()  # Align hitbox with the crab's rect

        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 3
        self.angle = 0  # Store the current rotation angle

        self.health = 3

        self.shoot_cooldown = 300  
        self.last_shot_time = 0  

    def update_hitbox(self):
        """Keep the hitbox centered within the crab's rect."""
        self.hitbox.center = self.rect.center

    def update(self, keys, screen):
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
        self.update_hitbox()
        self.rect = self.image.get_rect(center=self.pos)

        # pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)  # Red border for hitbox

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
        """Decreases the crab's health and checks for game over."""
        self.health -= amount
        if self.health <= 0:
            self.health = 0

    def check_bullet_collision(self, bullets_group):
        """Check if a bullet collides with the crab's hitbox."""
        for bullet in bullets_group:
            if self.hitbox.colliderect(bullet.hitbox):  # Check for collision with bullet's hitbox
                self.take_damage()  # Decrease health if collision occurs
                bullet.kill()  # Remove the bullet after collision
