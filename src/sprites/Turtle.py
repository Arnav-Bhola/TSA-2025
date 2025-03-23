import pygame
import math
from sprites.Bullet import TurtleBullet

class Turtle(pygame.sprite.Sprite):
    def __init__(self, crosshair):
        super().__init__()
        original_image = pygame.image.load("assets/images/turtle.png").convert_alpha()

        # Scale the image to a smaller size (adjust the values as needed)
        self.original_image = pygame.transform.scale(original_image, (100, 100))  
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(400, 300))

        # Create a smaller hitbox
        hitbox_width = int(self.rect.width * 0.7)  # 70% of original width
        hitbox_height = int(self.rect.height * 0.7)  # 70% of original height
        self.hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
        self.update_hitbox()  # Align hitbox with the turtle's rect

        self.pos = pygame.Vector2(self.rect.center)
        self.speed = 5
        self.stop_distance = 5

        self.health = 3

        # Cooldown properties
        self.shoot_cooldown = 560  # Cooldown time in milliseconds (0.3 seconds)
        self.last_shot_time = 0  # Timestamp of the last shot

        self.crosshair = crosshair  # Save reference to crosshair

    def update_hitbox(self):
        """Keep the hitbox centered within the turtle's rect."""
        self.hitbox.center = self.rect.center

    def update(self, screen):
        # Get the crosshair position
        crosshair_pos = self.crosshair.pos

        # Calculate direction vector towards the crosshair
        direction = pygame.Vector2(crosshair_pos.x - self.pos.x, crosshair_pos.y - self.pos.y)
        distance = direction.length()  # Get distance to crosshair

        # Move only if the turtle is not too close to the crosshair
        if distance > self.stop_distance:
            direction = direction.normalize()  # Normalize for consistent speed
            self.pos += direction * self.speed  # Move towards crosshair

        # Rotate towards the crosshair
        if distance > 1:  # Avoid jittering when very close
            angle = math.degrees(math.atan2(-direction.y, direction.x))  
            self.image = pygame.transform.rotate(self.original_image, angle + 270)

        # Update rect to match new position
        self.update_hitbox()
        self.rect = self.image.get_rect(center=self.pos)

        # pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)  # Red border for hitbox

    def shoot(self, bullets_group, target_pos):
        """Creates a bullet with cooldown and adds it to the bullets group."""
        current_time = pygame.time.get_ticks()  # Get current time in milliseconds

        if current_time - self.last_shot_time >= self.shoot_cooldown:
            bullet = TurtleBullet(self.rect.center, target_pos)  # Shoot towards crosshair
            bullets_group.add(bullet)
            self.last_shot_time = current_time  # Update last shot time

    def take_damage(self, amount=1):
        """Decreases the turtle's health and checks for game over."""
        self.health -= amount
        if self.health <= 0:
            self.health = 0

    def check_bullet_collision(self, bullets_group):
        """Check if a bullet collides with the turtle's hitbox."""
        for bullet in bullets_group:
            if self.hitbox.colliderect(bullet.hitbox):  # Check for collision with bullet's hitbox
                self.take_damage()  # Decrease health if collision occurs
                bullet.kill()  # Remove the bullet after collision
