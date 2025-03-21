import pygame

class Crosshair(pygame.sprite.Sprite):
    def __init__(self, speed=10, size=(40, 40), max_speed=10, friction=0.9, stop_threshold=4):
        super().__init__()
        self.image = pygame.image.load("assets/images/crosshair.png").convert_alpha()  # Load image with transparency
        self.image = pygame.transform.scale(self.image, size)  # Scale image to the desired size
        self.rect = self.image.get_rect()

        self.pos = pygame.Vector2(pygame.mouse.get_pos())  # Current position
        self.speed = speed  # Interpolation speed (lower = more lag)
        self.max_speed = max_speed  # Maximum speed of movement
        self.velocity = pygame.Vector2(0, 0)  # Starting velocity
        self.friction = friction  # Friction for deceleration
        self.stop_threshold = stop_threshold  # Threshold distance to stop movement

    def update(self):
        # Get the target position (current mouse position)
        target_pos = pygame.Vector2(pygame.mouse.get_pos())

        # Calculate the direction to the target
        direction = target_pos - self.pos
        distance = direction.length()

        # If the distance is greater than a small threshold, we move the crosshair
        if distance > self.stop_threshold:
            # Normalize direction and apply acceleration
            direction.normalize_ip()
            self.velocity += direction * self.speed  # Apply acceleration towards the target

            # Limit the speed to the max speed
            if self.velocity.length() > self.max_speed:
                self.velocity.scale_to_length(self.max_speed)

            # Apply friction (to simulate deceleration as it approaches the target)
            self.velocity *= self.friction

            # Update position with the current velocity
            self.pos += self.velocity
        else:
            # When close enough, stop the velocity and don't apply friction
            self.velocity = pygame.Vector2(0, 0)
            self.pos = target_pos  # Snap directly to the target position

        # Update the position of the crosshair
        self.rect.center = self.pos
