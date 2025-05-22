import pygame
import random
import asyncio
from sprites.Turtle import Turtle
from sprites.Crab import Crab
from sprites.Plastic import Plastic
from sprites.CrossHair import Crosshair
from sprites.Shop import Shop
from sprites.Plastic import PlasticBoss

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Game States
START_SCREEN = "start"
PLAYING = "playing"
GAME_OVER = "game_over"
SHOP_SCREEN = "shop"

# Boss wave configuration - CHANGE THIS TO ADJUST BOSS WAVE FREQUENCY
BOSS_WAVE_INTERVAL = 3  # Boss appears every 3 waves (change to 5 if you want)

game_state = START_SCREEN  # Start at the menu

# Create Sprites
crosshair = Crosshair()

# Create Players
turtle = Turtle(crosshair)
crab = Crab()

# Initialize Shop
shop_font = pygame.font.Font(None, 30)
shop = Shop(
    screen,
    shop_font,
    turtle,
    crab,
    pygame.Rect(
        screen.get_width() // 2 - 300,  # Center horizontally
        screen.get_height(),            # Start off-screen (will be animated in)
        600,                           # Width
        400                            # Height
    )
)

# Create sprite groups
player_sprites = pygame.sprite.Group(turtle, crab)
turtle_bullets = pygame.sprite.Group()
crab_bullets = pygame.sprite.Group()
crosshair_group = pygame.sprite.Group(crosshair)
plastic_group = pygame.sprite.Group()

# Game variables
last_plastic_spawn = pygame.time.get_ticks()
PLASTIC_SPAWN_TIME = 1000
coin_count = 0  # Starting coins
wave_number = 1
plastics_to_spawn = 4
plastics_spawned = 0
total_plastic_spawned = 0

# Load images
try:
    coin_image = pygame.image.load("assets/images/coin.png").convert_alpha()
    coin_image = pygame.transform.scale(coin_image, (30, 30))
except:
    # Fallback if coin image is missing
    coin_image = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(coin_image, (255, 215, 0), (15, 15), 15)

# Load background image
try:
    background_image = pygame.image.load("assets/images/ocean.jpg").convert()
    background_image = pygame.transform.scale(background_image, (800, 600))
except:
    background_image = None
    print("Could not load ocean.jpg - falling back to solid color background")

# Game information
info = [
    "Important information about the ocean: The Pacific Ocean is the largest ocean. The ocean contains more than 97% of Earth's water. Over 80% of ocean life remains unexplored.", 
    "Plastic kills turtles :(",
    "Plastic is not cool",
    "Every year, around 8 million metric tons of plastic end up in the ocean.",
    "There is a massive collection of floating plastic in the Pacific Ocean called the Great Pacific Garbage Patch.",
    "Microplastics, tiny plastic particles, have been found in fish, sea salt, and even drinking water.",
    "Marine animals often mistake plastic for food, which can lead to starvation and poisoning.",
    "Plastic waste can take hundreds of years to break down in the ocean.",
    "Over 1 million marine animals, including seabirds and sea turtles, die each year due to plastic pollution.",
    "Plastic pollution affects human health as toxic chemicals from plastics enter the food chain."
]


def is_boss_wave(wave_number):
    return wave_number % BOSS_WAVE_INTERVAL == 0

def draw_text_wrapped(text, font, color, surface, x, y, max_width, line_gap):
    """Renders the text with word wrapping within a maximum width, centers each line, and adds space between lines."""
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        test_surface = font.render(test_line, True, color)
        if test_surface.get_width() > max_width:
            if current_line:
                lines.append(current_line)
            current_line = word + " "
        else:
            current_line = test_line

    if current_line:
        lines.append(current_line)

    y_offset = y
    for line in lines:
        line_surface = font.render(line, True, color)
        line_x = x - line_surface.get_width() // 2
        surface.blit(line_surface, (line_x, y_offset))
        y_offset += line_surface.get_height() + line_gap

def draw_start_screen():
    """Draws the start screen with centered instructions."""
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill((0, 0, 50))  # Fallback color

    font = pygame.font.Font(None, 45)
    
    if wave_number == 1:
        text = font.render("Press any key to start!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen.get_width() // 2, (screen.get_height() // 2)))
    else:
        if is_boss_wave(wave_number):
            boss_text = font.render("BOSS WAVE!", True, (255, 0, 0))
            boss_rect = boss_text.get_rect(center=(screen.get_width() // 2, (screen.get_height() // 2) - 160))
            screen.blit(boss_text, boss_rect)
            text = font.render("Press any key to continue!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width() // 2, (screen.get_height() // 2) - 120))
        else:
            text = font.render("Press any key to continue!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width() // 2, (screen.get_height() // 2) - 120))

    font = pygame.font.Font(None, 30)
    if wave_number > 1:
        message = info[wave_number - 2]
        draw_text_wrapped(message, font, (255, 255, 255), screen, screen.get_width() // 2, screen.get_height() // 2 + 50, 400, 10)
        
        draw_health(screen, turtle, crab)
        draw_coins(screen)
        draw_wave(screen)

    screen.blit(text, text_rect)
    pygame.display.flip()

def draw_game_over():
    """Draws the game over screen with centered text."""
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill((50, 0, 0))  # Fallback color

    font = pygame.font.Font(None, 50)

    game_over_text = font.render("Game Over!", True, (255, 255, 255))
    restart_text = font.render("Press R to Restart", True, (255, 255, 255))

    game_over_rect = game_over_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 25))
    restart_rect = restart_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 25))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(restart_text, restart_rect)
    
    pygame.display.flip()

def draw_health(screen, turtle, crab):
    font = pygame.font.Font(None, 30)

    def draw_character_health(character, x, y):
        image = pygame.transform.scale(character.original_image, (30, 30))
        screen.blit(image, (x, y))
        health_text = font.render(f"{character.health}", True, (255, 255, 255))
        text_x = x + image.get_width() + 10
        text_y = y + (image.get_height() - health_text.get_height()) // 2
        screen.blit(health_text, (text_x, text_y))

    draw_character_health(turtle, 10, 10)
    draw_character_health(crab, 10, 50)

def draw_coins(screen):
    coin_x, coin_y = 700, 10
    screen.blit(coin_image, (coin_x, coin_y))
    font = pygame.font.Font(None, 30)
    coin_text = font.render(f"{coin_count:04d}", True, (255, 255, 255))
    text_x = coin_x + coin_image.get_width() + 5
    text_y = coin_y + (coin_image.get_height() - coin_text.get_height()) // 2
    screen.blit(coin_text, (text_x, text_y))

def draw_wave(screen):
    font = pygame.font.Font(None, 30)
    wave_text = font.render(f"Wave: {wave_number:02d}", True, (255, 255, 255))
    screen.blit(wave_text, (700, 50))

def reset_game():
    global game_state, coin_count, wave_number, plastics_spawned, plastics_to_spawn, total_plastic_spawned, last_plastic_spawn
    
    game_state = PLAYING
    coin_count = 100  # Reset to starting coins
    wave_number = 1
    plastics_spawned = 0
    plastics_to_spawn = 4
    total_plastic_spawned = 0
    last_plastic_spawn = pygame.time.get_ticks()
    
    turtle_bullets.empty()
    crab_bullets.empty()
    plastic_group.empty()
    
    turtle.health = 3
    crab.health = 3
    
    turtle.pos = pygame.Vector2(400, 300)
    crab.pos = pygame.Vector2(200, 200)
    turtle.rect.center = turtle.pos
    crab.rect.center = crab.pos
    turtle.update_hitbox()
    crab.update_hitbox()
    
    crosshair.pos = pygame.Vector2(screen.get_width() // 2, screen.get_height() // 2)
    crosshair.rect.center = crosshair.pos

def calc_plastic_total_spawned(wave_number):
    sum = 0
    for i in range(wave_number):
        sum += i
    sum *= 3
    sum += wave_number * 4
    return sum

def run_level():
    global game_state, last_plastic_spawn, coin_count, wave_number, plastics_spawned, plastics_to_spawn, total_plastic_spawned
    
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill((0, 0, 50))  # Fallback color
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state = START_SCREEN
            elif event.key == pygame.K_p:  # Open shop with P key
                game_state = SHOP_SCREEN
                shop.toggle()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            turtle.shoot(turtle_bullets, pygame.mouse.get_pos())

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            crab.shoot(crab_bullets)

    keys = pygame.key.get_pressed()
    
    current_time = pygame.time.get_ticks()
    number_of_plastics_that_should_have_been_spawned = calc_plastic_total_spawned(wave_number)
    
    # Spawn boss on boss waves instead of regular plastics
    if is_boss_wave(wave_number) and plastics_spawned == 0 and total_plastic_spawned < number_of_plastics_that_should_have_been_spawned:
        plastic_group.add(PlasticBoss(crab, turtle, screen, wave_number, plastic_group))
        total_plastic_spawned += 1
        plastics_spawned += 1
        last_plastic_spawn = current_time
    # Regular plastic spawning
    elif plastics_spawned < plastics_to_spawn and current_time - last_plastic_spawn >= PLASTIC_SPAWN_TIME:
        plastic_group.add(Plastic(crab, turtle, screen, wave_number))  
        total_plastic_spawned += 1
        plastics_spawned += 1
        last_plastic_spawn = current_time

    # Wave completion check
    if len(plastic_group) == 0 and total_plastic_spawned == number_of_plastics_that_should_have_been_spawned:
        wave_number += 1
        plastics_spawned = 0
        plastics_to_spawn = 4 + (wave_number - 1) * 3
        game_state = START_SCREEN

    turtle.update(screen)
    crab.update(keys, screen)
    turtle_bullets.update(screen)
    crab_bullets.update(screen)
    plastic_group.update(screen)
    crosshair_group.update()
    
    for bullet in turtle_bullets:
        for plastic in plastic_group:
            if bullet.rect.colliderect(plastic.rect):
                bullet.kill()
                if plastic.take_damage(100):
                    coin_count += 5 if isinstance(plastic, PlasticBoss) else 1

    for bullet in crab_bullets:
        for plastic in plastic_group:
            if bullet.rect.colliderect(plastic.rect):
                bullet.kill()
                if plastic.take_damage(50):
                    coin_count += 5 if isinstance(plastic, PlasticBoss) else 1

    crab.check_bullet_collision(plastic_group)
    turtle.check_bullet_collision(plastic_group)

    if turtle.health <= 0 or crab.health <= 0:
        game_state = GAME_OVER
        return True

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
async def main():
    running = True
    while running:
        if game_state == START_SCREEN:       
            draw_start_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    game_state = PLAYING
    
        elif game_state == SHOP_SCREEN:
            if background_image:
                screen.blit(background_image, (0, 0))
            else:
                screen.fill((0, 0, 50))  # Fallback color
            
            turtle_bullets.draw(screen)
            crab_bullets.draw(screen)
            player_sprites.draw(screen)
            plastic_group.draw(screen)
            draw_health(screen, turtle, crab)
            draw_coins(screen)
            draw_wave(screen)
        
            shop.update(coin_count)
            screen.blit(shop.image, shop.rect.topleft)
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                coins_spent = shop.handle_input(event, coin_count)
                coin_count -= coins_spent
        
            if not shop.is_open and not shop.is_animating:
                game_state = PLAYING

        elif game_state == PLAYING:
            running = run_level()

        elif game_state == GAME_OVER:
            draw_game_over()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    reset_game()
                    game_state = PLAYING
        
        await asyncio.sleep(0)
        pygame.display.flip()
        clock.tick(60)

pygame.quit()

asyncio.run(main())