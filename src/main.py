import pygame
from sprites.Turtle import Turtle
from sprites.Crab import Crab

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Create Players
turtle = Turtle()
crab = Crab()

# Create a sprite group for multiple characters
all_sprites = pygame.sprite.Group(turtle, crab)

running = True
while running:
    screen.fill((0, 0, 50))  # Deep ocean background

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get Key Presses
    keys = pygame.key.get_pressed()

    # Update Sprites
    turtle.update()   # Turtle follows mouse
    crab.update(keys)  # Crab moves with WASD

    # Draw Sprites
    all_sprites.draw(screen)

    # Update Display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
