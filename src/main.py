import pygame
from sprites.Turtle import Turtle
from sprites.Crab import Crab
from sprites.Plastic import Plastic
from sprites.CrossHair import Crosshair

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Game States
START_SCREEN = "start"
PLAYING = "playing"
GAME_OVER = "game_over"

game_state = START_SCREEN  # Start at the menu

# Create Spriteswwd
crosshair = Crosshair()

# Create Players
turtle = Turtle(crosshair)
crab = Crab()

# Create a sprite group for multiple characters
player_sprites = pygame.sprite.Group(turtle, crab)
turtle_bullets = pygame.sprite.Group()
crab_bullets = pygame.sprite.Group()
crosshair_group = pygame.sprite.Group(crosshair)

# Create plastic sprite group
plastic_group = pygame.sprite.Group()
last_plastic_spawn = pygame.time.get_ticks()
PLASTIC_SPAWN_TIME = 1000

# Coin System
coin_count = 0  # Starting coins
coin_image = pygame.image.load("assets/images/coin.png").convert_alpha()  # Load coin image
coin_image = pygame.transform.scale(coin_image, (30, 30))  # Scale the coin image

def draw_start_screen():
    """Draws the start screen with centered instructions."""
    screen.fill((0, 0, 50))  # Deep ocean background
    font = pygame.font.Font(None, 50)
    
    text = font.render("Press any key to start!", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    
    screen.blit(text, text_rect)
    pygame.display.flip()


def draw_game_over():
    """Draws the game over screen with centered text."""
    screen.fill((50, 0, 0))  # Dark red background
    font = pygame.font.Font(None, 50)

    game_over_text = font.render("Game Over!", True, (255, 255, 255))
    restart_text = font.render("Press R to Restart", True, (255, 255, 255))

    # Get center positions
    game_over_rect = game_over_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 25))
    restart_rect = restart_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 25))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(restart_text, restart_rect)
    
    pygame.display.flip()

def draw_health(screen, turtle, crab):
    font = pygame.font.Font(None, 30)

    def draw_character_health(character, x, y):
        """Helper function to draw health with vertical centering."""
        image = pygame.transform.scale(character.original_image, (30, 30))  # Resize the image
        screen.blit(image, (x, y))  # Draw the character image

        health_text = font.render(f"{character.health}", True, (255, 255, 255))

        # Get text size for alignment
        text_width, text_height = health_text.get_size()
        text_x = x + image.get_width() + 10  # Place text slightly to the right
        text_y = y + (image.get_height() - text_height) // 2  # Center text vertically

        screen.blit(health_text, (text_x, text_y))  # Draw the health text

    # Draw health for turtle and crab
    draw_character_health(turtle, 10, 10)  # Turtle at (10, 10)
    draw_character_health(crab, 10, 50)  # Crab at (10, 50)


def draw_coins(screen):
    """Draws the coin count on the screen with leading zeros, properly aligned with the icon."""
    global coin_count
    coin_x, coin_y = 700, 10  # Position of the coin image
    screen.blit(coin_image, (coin_x, coin_y))  # Draw the coin icon

    font = pygame.font.Font(None, 30)
    coin_text = font.render(f"{coin_count:04d}", True, (255, 255, 255))

    # Get text size to adjust alignment
    text_width, text_height = coin_text.get_size()
    text_x = coin_x + coin_image.get_width() + 5  # Position it slightly right of the coin
    text_y = coin_y + (coin_image.get_height() - text_height) // 2  # Center it vertically

    screen.blit(coin_text, (text_x, text_y))  # Draw the coin count


def run_level():
    
    pygame.mouse.set_visible(True)  # Hide the cursor

    """Main gameplay loop."""
    global game_state, last_plastic_spawn, coin_count  # So we can change game state
    screen.fill((0, 0, 50))  # Deep ocean background

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Quit to menu
                game_state = START_SCREEN

        # Shoot bullet when left mouse button is clicked
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            turtle.shoot(turtle_bullets, pygame.mouse.get_pos())  # Pass target position

        # Shoot bullet when spacebar is pressed
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            crab.shoot(crab_bullets)

    # Get Key Presses
    keys = pygame.key.get_pressed()

    # **Spawn Plastic Every 5 Seconds**
    current_time = pygame.time.get_ticks()
    if current_time - last_plastic_spawn >= PLASTIC_SPAWN_TIME:
        plastic_group.add(Plastic(crab, turtle))  # Add new plastic to the group
        last_plastic_spawn = current_time  # Reset timer

    # Update Sprites
    turtle.update()   # Turtle follows mouse
    crab.update(keys)  # Crab moves with WASDxs
    turtle_bullets.update()
    crab_bullets.update()
    plastic_group.update()
    crosshair_group.update()

    # Check Bullet-Plastic Collisions
    hits = pygame.sprite.groupcollide(turtle_bullets, plastic_group, True, False)
    for bullet, plastics in hits.items():
        for plastic in plastics:
            if plastic.take_damage():  # Only increment coin count if plastic dies
                coin_count += 1  

    hits = pygame.sprite.groupcollide(crab_bullets, plastic_group, True, False)
    for bullet, plastics in hits.items():
        for plastic in plastics:
            if plastic.take_damage():  # Only increment coin count if plastic dies
                coin_count += 1  

    # Check Player-Plastic Collisions
    turtle_hits = pygame.sprite.spritecollide(turtle, plastic_group, True)
    for plastic in turtle_hits:
        turtle.take_damage()
        coin_count += 1  # Plastic died due to collision, so give a coin

    crab_hits = pygame.sprite.spritecollide(crab, plastic_group, True)
    for plastic in crab_hits:
        crab.take_damage()
        coin_count += 1  # Plastic died due to collision, so give a coin

    # Check if the game is over
    if turtle.health <= 0 or crab.health <= 0:
        game_state = GAME_OVER
        return True  # Keep the loop running so the game over screen can be displayed

    # Draw Sprites
    turtle_bullets.draw(screen) 
    crab_bullets.draw(screen) 
    player_sprites.draw(screen)
    plastic_group.draw(screen)
    draw_health(screen, turtle, crab)
    draw_coins(screen)
    crosshair_group.draw(screen)

    return True

# Main Game Loop
running = True
while running:
    if game_state == START_SCREEN:
        pygame.mouse.set_visible(True)  # Hide the cursor

        draw_start_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                game_state = PLAYING  # Start game

    elif game_state == PLAYING:
        running = run_level()

    elif game_state == GAME_OVER:
        pygame.mouse.set_visible(True)  # Hide the cursor

        draw_game_over()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Reset game variables
                turtle.health = 3
                crab.health = 3
                turtle.rect.topleft = (100, 300)  # Reset positions if necessary
                crab.rect.topleft = (600, 300)

                coin_count = 0  # Reset coins
                plastic_group.empty()  # Clear plastics

                game_state = PLAYING  # Restart game

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
