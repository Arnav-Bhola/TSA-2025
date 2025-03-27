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

# Create Sprites
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

wave_number = 1  # Start at wave 1
plastics_to_spawn = 4  # First wave starts with 4 plastics
plastics_spawned = 0  # Track how many plastics have been spawned in the current wave
total_plastic_spawned = 0  # Track total plastics spawned

info = [
    "important information about the ocean: The Pacific Ocean is the largest ocean. The ocean contains more than 97% of Earth's water. Over 80% of ocean life remains unexplored.", 
    "plastic kills turtles :(",
    "plastic is not cool"
]

def draw_text_wrapped(text, font, color, surface, x, y, max_width, line_gap):
    """Renders the text with word wrapping within a maximum width, centers each line, and adds space between lines."""
    words = text.split(' ')  # Split the text into words
    lines = []  # List to store lines of text
    current_line = ""  # Current line being constructed

    # Go through each word and add it to the current line
    for word in words:
        # If adding this word would exceed the max width, start a new line
        test_line = current_line + word + " "
        test_surface = font.render(test_line, True, color)
        if test_surface.get_width() > max_width:
            if current_line:
                lines.append(current_line)  # Add the current line to the list
            current_line = word + " "  # Start a new line with the current word
        else:
            current_line = test_line  # Add the word to the current line

    # Add the last line
    if current_line:
        lines.append(current_line)

    # Now render the lines on the screen
    y_offset = y
    for line in lines:
        line_surface = font.render(line, True, color)
        line_x = x - line_surface.get_width() // 2  # Center each line
        surface.blit(line_surface, (line_x, y_offset))
        y_offset += line_surface.get_height() + line_gap  # Add gap between lines


def draw_start_screen():
    """Draws the start screen with centered instructions."""
    screen.fill((0, 0, 50))  # Deep ocean background

    font = pygame.font.Font(None, 45)  # Smaller font size
    
    if wave_number == 1:
        text = font.render("Press any key to start!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen.get_width() // 2, (screen.get_height() // 2)))
    else:
        text = font.render("Press any key to continue!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen.get_width() // 2, (screen.get_height() // 2) - 120))

    font = pygame.font.Font(None, 30)  # Smaller font size
    if wave_number > 1:
        # Render wrapped text for information
        message = info[wave_number - 2]
        draw_text_wrapped(message, font, (255, 255, 255), screen, screen.get_width() // 2, screen.get_height() // 2 + 50, 400, 10)
        
        draw_health(screen, turtle, crab)
        draw_coins(screen)
        draw_wave(screen)

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

def draw_wave(screen):
    """Draws the wave number on the screen with leading zeros, properly aligned with the icon."""
    global wave_number
    coin_x, coin_y = 700, 10  # Position of the wave icon

    font = pygame.font.Font(None, 30)
    wave_text = font.render(f"Wave: {wave_number:02d}", True, (255, 255, 255))

    # Get text size to adjust alignment
    text_width, text_height = wave_text.get_size()
    text_x = 700  # Position it slightly right of the coin
    text_y = 50  # Center it vertically

    screen.blit(wave_text, (text_x, text_y))  # Draw the coin count

def run_level():
    
    pygame.mouse.set_visible(True)  # Hide the cursor

    """Main gameplay loop."""
    global game_state, last_plastic_spawn, coin_count, wave_number, plastics_spawned, plastics_to_spawn, total_plastic_spawned
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
    
    def calc_plastic_total_spawned(wave_number):
        sum = 0
        for i in range(wave_number):
            sum += i
        sum *= 3
        sum += wave_number*4
        return sum

    current_time = pygame.time.get_ticks()
    number_of_plastics_that_should_have_been_spawned = calc_plastic_total_spawned(wave_number)
    if plastics_spawned < plastics_to_spawn and current_time - last_plastic_spawn >= PLASTIC_SPAWN_TIME:
        plastic_group.add(Plastic(crab, turtle, screen))  
        total_plastic_spawned += 1
        plastics_spawned += 1  # Increment count
        last_plastic_spawn = current_time  # Reset timer

    # Check if all plastics are gone (wave completed)
    if len(plastic_group) == 0 and total_plastic_spawned == number_of_plastics_that_should_have_been_spawned:
        wave_number += 1  # Increase wave number
        plastics_spawned = 0  # Reset the counter
        plastics_to_spawn = 4 + (wave_number - 1) * 3  # Increase difficulty
        game_state = START_SCREEN

    # Update Sprites
    turtle.update(screen)   # Turtle follows mouse
    crab.update(keys, screen)  # Crab moves with WASDxs
    turtle_bullets.update(screen)
    crab_bullets.update(screen)
    plastic_group.update(screen)
    crosshair_group.update()
    
    # Collision Handling - Turtle Bullets with Plastics using Rect.colliderect
    for bullet in turtle_bullets:
        for plastic in plastic_group:
            if bullet.rect.colliderect(plastic.rect):  # Check if the bullet's hitbox intersects with the plastic's hitbox
                bullet.kill()  # Remove the bullet
                if plastic.take_damage():
                    coin_count += 1

    # Collision Handling - Crab Bullets with Plastics using Rect.colliderect
    for bullet in crab_bullets:
        for plastic in plastic_group:
            if bullet.rect.colliderect(plastic.rect):  # Check if the bullet's hitbox intersects with the plastic's hitbox
                bullet.kill()  # Remove the bullet
                if plastic.take_damage():
                    coin_count += 1

    crab.check_bullet_collision(plastic_group)
    turtle.check_bullet_collision(plastic_group)

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
    draw_wave(screen)
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
                wave_number = 1  # Restart from wave 1
                plastics_to_spawn = 4  # Reset initial wave size
                plastics_spawned = 0  # Reset spawn counter
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
